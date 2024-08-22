import datetime

from flask import Blueprint, render_template, url_for, request, make_response, session, flash, redirect
from main import logger, db
from main.modules.shifts.models import Shift, ShiftInstance
from utils.date_functions import day_of_week_str, time_of_day_str
from utils.date_time_enums import DayOfWeekEnum, TimeOfDayEnum
from ..shifts import services as shift_services
from ..shifts.forms import ShiftInstanceCompletedTimestampForm
from ..shifts.services import generate_alert_for_shifts_that_need_signups

main = Blueprint("main", __name__, url_prefix="")


@main.route("/")
def index():
    generate_alert_for_shifts_that_need_signups()
    session.permanent = True
    name = request.cookies.get("name") or ""
    page = int(request.args.get("page", default=1, type=int))

    # Create view models for the page
    next_shift_instances = [
        shift_services.generate_shift_instance_view_model(shift_instance, name)
        for shift_instance in shift_services.generate_next_shift_instances()
    ]
    previous_shift_instances = shift_services.get_previous_shifts(page)
    for item_index, item in enumerate(previous_shift_instances.items):
        previous_shift_instances.items[item_index] = shift_services.generate_shift_instance_view_model(item, name)

    return render_template("main/index.html",
                           prefilled_name=name,
                           next_shift_instances=next_shift_instances,
                           previous_shift_instances=previous_shift_instances,
                           todays_date=datetime.date.today())


@main.route("/undo/<int:shift_instance_id>", methods=["POST"])
def undo_shift_instance(shift_instance_id: int):
    pass
    shift_instance = ShiftInstance.query.get_or_404(shift_instance_id)
    shift_instance.completed_timestamp = None
    shift_instance.completed_by = None
    shift_instance.eggs = None
    db.session.commit()

    response = make_response(redirect(url_for("main.index")))
    flash(f"Successfully cleared {day_of_week_str(shift_instance.shift.day_of_week)} "
          f"{time_of_day_str(shift_instance.shift.time_of_day)}.", "success")
    return response


@main.route("/save-shift-instance", methods=["POST"])
def save_shift_instance():
    form = ShiftInstanceCompletedTimestampForm()
    if form.validate_on_submit():
        shift_instance = ShiftInstance.query.get_or_404(int(form.shift_instance_id.data))
        shift_instance.completed_timestamp = form.completed_timestamp.data
        shift_instance.completed_by = form.completed_by.data
        shift_instance.eggs = form.eggs.data
        db.session.commit()

        response = make_response(redirect(url_for("main.index")))
        one_year_in_seconds = 31_536_000
        response.set_cookie("name", form.completed_by.data, max_age=one_year_in_seconds)
        flash(f"Successfully updated {day_of_week_str(shift_instance.shift.day_of_week)} "
              f"{time_of_day_str(shift_instance.shift.time_of_day)}.", "success")
        return response
    else:
        flash(f"Failed with errors: {form.errors}", "danger")
        return redirect(url_for("main.index"))


@main.route("/seed-shifts")
def seed_shifts():
    if db.session.query(Shift).count() != 0:
        return {"status": "already done!"}, 400

    times_of_day = [TimeOfDayEnum.MORNING, TimeOfDayEnum.EVENING]
    days_of_week = [DayOfWeekEnum.MONDAY, DayOfWeekEnum.TUESDAY, DayOfWeekEnum.WEDNESDAY, DayOfWeekEnum.THURSDAY,
                    DayOfWeekEnum.FRIDAY, DayOfWeekEnum.SATURDAY, DayOfWeekEnum.SUNDAY]

    for day_of_week in days_of_week:
        for time_of_day in times_of_day:
            shift = Shift(
                day_of_week=day_of_week,
                time_of_day=time_of_day
            )
            db.session.add(shift)
            db.session.commit()

    return [
        (str(DayOfWeekEnum(s.day_of_week)), str(TimeOfDayEnum(s.time_of_day)))
        for s in Shift.query.all()
    ]


@main.route("/fake-error")
def fake_error():
    raise ValueError("Just want to see what happens")