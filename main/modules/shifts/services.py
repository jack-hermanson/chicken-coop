from __future__ import annotations

from flask import flash
from sqlalchemy import and_, or_

from main import logger, db
from utils.date_functions import get_next_date_with_same_day_of_week, day_of_week_str, time_of_day_str
from utils.date_time_enums import DayOfWeekEnum
from .forms import ShiftInstanceCompletedTimestampForm, AssignShiftForm
from .models import Shift, ShiftInstance
from datetime import date, datetime, timedelta

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
            shift.shift_instances.append(new_shift_instance)
            db.session.add(new_shift_instance)
            db.session.commit()

    shift_instances_to_return = []
    for shift in raw_shifts:
        # there should only be one
        future_shift_instances = get_future_shift_instances(shift.shift_id)
        if len(future_shift_instances) != 1:
            logger.error(f"There are {len(future_shift_instances)} shift instances for shift with ID {shift.shift_id}")
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
        .paginate(page=page, per_page=10)
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
    else:
        form = None

    view_model = ShiftInstanceViewModel(
        shift_instance,
        form
    )
    return view_model


def generate_assign_shift_view_model(shift: Shift, form: AssignShiftForm = None) -> AssignShiftViewModel:
    assign_shift_view_model = AssignShiftViewModel(
        shift=shift,
        assign_shift_form=(form or AssignShiftForm(
            assigned_to=shift.assigned_to,
            shift_id=shift.shift_id,
            seeking_replacement=shift.seeking_replacement
        ))
    )
    if not form:
        assign_shift_view_model.assign_shift_form.secret_code.data = ""
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
        logger.info(f"There are {len(shifts_that_need_signups)} shifts that need signups")
        message = "The following shifts are looking for volunteers: "
        for index, shift in enumerate(shifts_that_need_signups):
            message += f"{day_of_week_str(shift.day_of_week)} {time_of_day_str(shift.time_of_day)}"
            if index < len(shifts_that_need_signups) - 1:
                message += ", "
        message += "."
        flash(message, "warning")
