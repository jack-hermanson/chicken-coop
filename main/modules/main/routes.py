import datetime

from flask import Blueprint, render_template, url_for, request, make_response, session
from main import logger, db
from main.modules.shifts.models import Shift
from utils.date_time_enums import DayOfWeekEnum, TimeOfDayEnum
from ..shifts import services as shift_services

main = Blueprint("main", __name__, url_prefix="")


@main.route("/")
def index():
    session.permanent = True
    name = request.cookies.get("name") or ""
    page = int(request.args.get("page", default=1, type=int))
    previous_shift_instances = shift_services.get_previous_shifts(page)
    return render_template("main/index.html",
                           prefilled_name=name,
                           next_shift_instances=shift_services.generate_next_shift_instances(),
                           previous_shift_instances=previous_shift_instances,
                           todays_date=datetime.date.today())


# todo - delete
@main.route("/submit-form", methods=["POST"])
def test():
    name = request.form.get("name")
    response = make_response(render_template("main/index.html",
                                             prefilled_name=name))
    response.set_cookie("name", name)
    return response


@main.route("/seed-shifts")
def seed_shifts():
    if db.session.query(Shift).count() != 0:
        return {"status": "already done!"}, 400

    times_of_day = [TimeOfDayEnum.MORNING, TimeOfDayEnum.AFTERNOON]
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
