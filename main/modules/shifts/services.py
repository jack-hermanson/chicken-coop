from __future__ import annotations

import time

from dateutil import tz
from flask import flash
from sqlalchemy import and_, or_, func, desc

from main import logger, db
from utils.date_functions import get_next_date_with_same_day_of_week, day_of_week_str, time_of_day_str, extract_date
from utils.date_time_enums import DayOfWeekEnum, TimeOfDayEnum
from .forms import ShiftInstanceCompletedTimestampForm, AssignRecurringShiftForm, AssignSpecificShiftForm
from .models import Shift, ShiftInstance, SpecificShiftInstanceAssignment
from datetime import date, datetime, timedelta

from .utils.sunrise_sunset import get_sunrise_sunset
from .view_models import ShiftInstanceViewModel, AssignShiftViewModel


def get_future_shift_instances(shift_id):
    return (ShiftInstance.query
            .filter(and_(ShiftInstance.due_date >= date.today(),
                         ShiftInstance.shift_id == shift_id))
            .order_by(ShiftInstance.due_date)
            .all())


def generate_next_shift_instances():
    """
    Generate shift instances for the current day and the next 7 days.
    If they've already been created, then return them.
    """
    # get all shifts
    raw_shifts = Shift.query.all()

    # make sure each shift has instances to mark as complete
    for shift in raw_shifts:
        # there should only be one
        future_shift_instances = get_future_shift_instances(shift.shift_id)

        if len(future_shift_instances) > 1:
            logger.error(f"There is more than 1 shift instance for shift with ID {shift.shift_id}")
            raise ValueError("Bad shift instance count")

        if len(future_shift_instances) == 1:
            logger.debug(f"Relevant shift instance already exists for shift with ID {shift.shift_id}")
            continue

        if len(future_shift_instances) == 0:
            logger.info(f"Creating shift instance for shift with ID {shift.shift_id}")
            # need to create one
            new_shift_instance = ShiftInstance()
            new_shift_instance.due_date = get_next_date_with_same_day_of_week(
                DayOfWeekEnum(shift.day_of_week),
                exclude_today=False
            )
            set_sunrise_sunset(new_shift_instance, shift)
            update_shift_instance_with_assignment(new_shift_instance, shift)
            shift.shift_instances.append(new_shift_instance)
            db.session.add(new_shift_instance)
            db.session.commit()

    shift_instances_to_return = []
    for shift in raw_shifts:
        # there should only be one
        future_shift_instances = get_future_shift_instances(shift.shift_id)
        if len(future_shift_instances) != 1:
            logger.error(
                f"There {'is' if len(future_shift_instances) == 1 else 'are'} {len(future_shift_instances)} shift "
                f"instance{'' if len(future_shift_instances) == 1 else 's'} for shift with ID {shift.shift_id}")
            raise ValueError("Bad shift instance count")
        shift_instances_to_return.append(future_shift_instances[0])

    shift_instances_to_return.sort(key=lambda si: (si.due_date, si.shift.time_of_day))
    return shift_instances_to_return


def get_previous_shifts(page: int):
    """
    Get a paginated list of previous shifts in descending order of most recent to least recent.
    """
    shift_instances = (
        ShiftInstance.query
        .join(ShiftInstance.shift)
        .filter(
            ShiftInstance.due_date < date.today()
        )
        .order_by(ShiftInstance.due_date.desc(), Shift.time_of_day.desc())
        .paginate(page=page, per_page=14)
    )
    return shift_instances


def generate_shift_instance_view_model(shift_instance: ShiftInstance, default_name: str) -> ShiftInstanceViewModel:
    due_date_is_within_editable_range = (
        # today
        shift_instance.due_date.date() == datetime.today().date() or
        (
            # or yesterday
            (datetime.today().date() + timedelta(days=-1)) == shift_instance.due_date.date()
        )
    )
    if due_date_is_within_editable_range:
        form = ShiftInstanceCompletedTimestampForm()
        form.shift_instance_id.data = shift_instance.shift_instance_id
        form.completed_by.data = default_name
        if shift_instance.completed_timestamp:
            form.completed_timestamp.data = shift_instance.completed_timestamp
            form.completed_by.data = shift_instance.completed_by
            form.eggs_taken_home.data = shift_instance.eggs_taken_home
            form.eggs_left_behind.data = shift_instance.eggs_left_behind
    else:
        form = None

    from_zone = tz.gettz('UTC')
    to_zone = tz.gettz('America/Denver')

    view_model = ShiftInstanceViewModel(
        shift_instance,
        form,
        sunrise=(shift_instance.sunrise_utc.replace(tzinfo=from_zone).astimezone(to_zone).strftime(
            "%l:%M %p") if shift_instance.sunrise_utc else None),
        sunset=(shift_instance.sunset_utc.replace(tzinfo=from_zone).astimezone(to_zone).strftime(
            "%l:%M %p") if shift_instance.sunset_utc else None),
        target_time=(
            (shift_instance.sunrise_utc + timedelta(minutes=30)).replace(tzinfo=from_zone).astimezone(to_zone).strftime(
                "%l:%M %p") if shift_instance.sunrise_utc is not None
            else None
        )
        # target_time=(
        #     (shift_instance.sunrise_utc.replace(tzinfo=from_zone).astimezone(to_zone) + timedelta(minutes=30)).strftime(
        #         "%l:%M %p") if shift_instance.sunset_utc else None),
    )
    return view_model


def generate_assign_shift_view_model(shift: Shift, form: AssignRecurringShiftForm = None) -> AssignShiftViewModel:
    assign_shift_view_model = AssignShiftViewModel(
        shift=shift,
        assign_shift_form=(form or AssignRecurringShiftForm(
            assigned_to=shift.assigned_to,
            shift_id=shift.shift_id,
            seeking_replacement=shift.seeking_replacement
        ))
    )
    # if not form:
    # assign_shift_view_model.assign_shift_form.secret_code.data = ""
    return assign_shift_view_model


def get_shifts_that_need_signups():
    """Get all the shifts that have 'seeking_replacement' or no assignment at all."""
    shifts_that_need_signups = Shift.query.filter(
        or_(
            Shift.seeking_replacement,
            Shift.assigned_to.is_(None)
        )
    ).order_by(Shift.day_of_week, Shift.time_of_day).all()
    return shifts_that_need_signups


def generate_alert_for_shifts_that_need_signups():
    """Generate the alert saying these shifts need signups."""
    shifts_that_need_signups = get_shifts_that_need_signups()
    if len(shifts_that_need_signups):
        logger.info(f"There {'is' if len(shifts_that_need_signups) else 'are'} {len(shifts_that_need_signups)} "
                    f"shift{'' if len(shifts_that_need_signups) else 's'} that need signups")
        message = "The following shifts are looking for volunteers: "
        for index, shift in enumerate(shifts_that_need_signups):
            message += f"{day_of_week_str(shift.day_of_week)} {time_of_day_str(shift.time_of_day)}"
            if index < len(shifts_that_need_signups) - 1:
                message += ", "
        message += "."
        flash(message, "warning")


def assign_specific_shift(assign_specific_shift_form: AssignSpecificShiftForm) -> SpecificShiftInstanceAssignment:
    # First, try to find a matching shift instance.
    existing_shift_instance: ShiftInstance = ShiftInstance.query.join(ShiftInstance.shift).filter(
        and_(
            func.date(ShiftInstance.due_date) == assign_specific_shift_form.date.data,
            Shift.time_of_day == assign_specific_shift_form.time_of_day.data
        )
    ).scalar()
    # Update shift instance record if found.
    if existing_shift_instance:
        existing_shift_instance.instance_assigned_to = assign_specific_shift_form.assigned_to.data
        db.session.commit()

    # Try to find existing SpecificShiftInstanceAssignment with that date and shift
    existing_specific_shift_instance_assignment = SpecificShiftInstanceAssignment.query.filter(
        and_(
            func.date(SpecificShiftInstanceAssignment.instance_date) == assign_specific_shift_form.date.data,
            SpecificShiftInstanceAssignment.time_of_day == assign_specific_shift_form.time_of_day.data
        )
    ).scalar()
    if existing_specific_shift_instance_assignment:
        logger.warn(f"Updating existing specific shift instance assignment with ID "
                    f"{existing_specific_shift_instance_assignment.specific_shift_instance_assignment_id}")
        logger.debug(f"{existing_specific_shift_instance_assignment.instance_date.strftime('%F')} "
                     f"{time_of_day_str(existing_specific_shift_instance_assignment.time_of_day)}")
        # only need to change person, no need to set date and time
        logger.debug(f"Original: {existing_specific_shift_instance_assignment.instance_assigned_to}")
        existing_specific_shift_instance_assignment.instance_assigned_to = assign_specific_shift_form.assigned_to.data
        logger.debug(f"New: {assign_specific_shift_form.assigned_to.data}")
        db.session.commit()
        return existing_specific_shift_instance_assignment

    # Need to add it to the queue
    logger.info("Adding a new specific_shift_instance_assignment %s %s", assign_specific_shift_form.date.data,
                time_of_day_str(TimeOfDayEnum(int(assign_specific_shift_form.time_of_day.data))))
    specific_shift_instance_assignment = SpecificShiftInstanceAssignment()
    specific_shift_instance_assignment.instance_assigned_to = assign_specific_shift_form.assigned_to.data
    specific_shift_instance_assignment.time_of_day = TimeOfDayEnum(int(assign_specific_shift_form.time_of_day.data))
    specific_shift_instance_assignment.instance_date = assign_specific_shift_form.date.data
    db.session.add(specific_shift_instance_assignment)
    db.session.commit()

    return specific_shift_instance_assignment


def get_specific_shift_instance_assignments() -> list[SpecificShiftInstanceAssignment]:
    return SpecificShiftInstanceAssignment.query.order_by(
        SpecificShiftInstanceAssignment.instance_date.desc())


def get_paginated_specific_shift_instance_assignments(page: int):
    specific_shift_instance_assignments = (
        SpecificShiftInstanceAssignment.query
        .order_by(
            SpecificShiftInstanceAssignment.instance_date.desc(),
            SpecificShiftInstanceAssignment.time_of_day.desc()
        )
        .paginate(page=page, per_page=10)
    )
    return specific_shift_instance_assignments


def update_shift_instance_with_assignment(new_shift_instance: ShiftInstance, shift: Shift):
    """
        Given a brand new ShiftInstance, check if there is already a specific date assignment for it.
        If there is, then make sure to copy that to the instance_assigned_to property.
    """
    specific_shift_instance_assignment = SpecificShiftInstanceAssignment.query.filter(
        and_(
            func.date(SpecificShiftInstanceAssignment.instance_date) == new_shift_instance.due_date,
            SpecificShiftInstanceAssignment.time_of_day == shift.time_of_day
        )
    ).scalar()
    if specific_shift_instance_assignment:
        new_shift_instance.instance_assigned_to = specific_shift_instance_assignment.instance_assigned_to


def get_average_eggs_for_all_shifts():
    return (db.session
            .query(func.avg(ShiftInstance.eggs_taken_home))
            .filter(ShiftInstance.eggs_taken_home.is_not(None))
            .scalar())


def get_average_eggs_for_day_and_time(day_of_week: DayOfWeekEnum, time_of_day: TimeOfDayEnum,
                                      weeks_ago: int):
    cutoff_date = datetime.now() - timedelta(weeks=weeks_ago)

    average_eggs = (db.session
                    .query(func.avg(ShiftInstance.eggs_taken_home))
                    .join(ShiftInstance.shift)
                    .filter(and_(
        ShiftInstance.eggs_taken_home.isnot(None),
        ShiftInstance.due_date >= cutoff_date,
        Shift.time_of_day == time_of_day,
        Shift.day_of_week == day_of_week
    ))
                    .scalar()) or 0
    return round(float(average_eggs) if float(average_eggs) >= 0.1 else 0, 3)


def get_average_eggs_per_shift(weeks_ago):
    """
    Get average gets per shift.
    :param weeks_ago: Cutoff date for computing the average. How many weeks ago is the min?
    """
    output = []
    for day in [DayOfWeekEnum.MONDAY, DayOfWeekEnum.TUESDAY, DayOfWeekEnum.WEDNESDAY,
                DayOfWeekEnum.THURSDAY, DayOfWeekEnum.FRIDAY, DayOfWeekEnum.SATURDAY, DayOfWeekEnum.SUNDAY]:
        morning = get_average_eggs_for_day_and_time(day, TimeOfDayEnum.MORNING, weeks_ago)
        evening = get_average_eggs_for_day_and_time(day, TimeOfDayEnum.EVENING, weeks_ago)
        difference = round(evening - morning, 3)
        total = round(morning + evening, 3)
        day_dict = {
            "day of week": day_of_week_str(day),
            "morning": morning,
            "evening": evening,
            "total": total,
            "difference": difference
        }
        output.append(day_dict)
    return output


def get_raw_shift_instance_data() -> str:
    """
    Get all of our shift instance data, dump it into a CSV.
    """
    raw_data = (ShiftInstance.query
                .filter(ShiftInstance.due_date <= datetime.today())
                .join(ShiftInstance.shift)
                .order_by(desc(ShiftInstance.due_date), Shift.time_of_day)
                .all())
    headers = [
        "shift_instance_id",
        "date",
        "time_of_day",
        "completed_by",
        "completed_timestamp",
        "eggs"
    ]
    rows = [
        ([
            str(shift_instance.shift_instance_id),
            shift_instance.due_date.strftime("%F") if shift_instance.due_date is not None else "null",
            str(shift_instance.shift.time_of_day),
            shift_instance.completed_by.strip() if shift_instance.completed_by is not None else "null",
            shift_instance.completed_timestamp.strftime("%T") if shift_instance.completed_timestamp is not None else "null",
            str(shift_instance.eggs_taken_home) if shift_instance.eggs_taken_home is not None else "null",
        ]) for shift_instance in raw_data
    ]
    output_string = ",".join(headers) + "\n"
    for row in rows:
        output_string += ",".join(row) + "\n"
    return output_string



def test_filter():
    cutoff_date = datetime.now() - timedelta(weeks=8)
    data = ShiftInstance.query.filter(and_(
        ShiftInstance.due_date >= cutoff_date,
        ShiftInstance.eggs_taken_home.isnot(None)
    )).all()
    result = []
    for item in data:
        result.append({
            "due_date": item.due_date.__str__(),
            "eggs": item.eggs_taken_home
        })
    return result


def get_table_data() -> dict[str, list[Shift]]:
    """Get data for a calendar-like table of shifts."""
    output = {
        "morning_shifts": [],
        "evening_shifts": []
    }
    morning_shifts = Shift.query.filter(Shift.time_of_day == TimeOfDayEnum.MORNING).order_by(
        Shift.day_of_week,
        Shift.time_of_day.desc()
    ).all()
    evening_shifts = Shift.query.filter(Shift.time_of_day == TimeOfDayEnum.EVENING).order_by(
        Shift.day_of_week,
        Shift.time_of_day.desc()
    ).all()
    output["morning_shifts"] = morning_shifts
    output["evening_shifts"] = evening_shifts
    return output


def set_sunrise_sunset(shift_instance: ShiftInstance, shift: Shift):
    sunrise_sunset = get_sunrise_sunset(shift_instance.due_date)
    if shift.time_of_day == TimeOfDayEnum.MORNING:
        logger.info(f"setting sunrise to {sunrise_sunset.sunrise_utc.__str__()} on {shift_instance.shift_instance_id}")
        shift_instance.sunrise_utc = sunrise_sunset.sunrise_utc
    if shift.time_of_day == TimeOfDayEnum.EVENING:
        logger.info(f"setting sunset to {sunrise_sunset.sunset_utc.__str__()} on {shift_instance.shift_instance_id}")
        shift_instance.sunset_utc = sunrise_sunset.sunset_utc


def set_sunrise_sunset_on_all():
    shift_instances = ShiftInstance.query.filter(and_(ShiftInstance.sunrise_utc.is_(None),
                                                      ShiftInstance.sunset_utc.is_(None))).join(
        ShiftInstance.shift).all()

    for shift_instance in shift_instances:
        set_sunrise_sunset(shift_instance, shift_instance.shift)
        time.sleep(0.1)
    db.session.commit()
