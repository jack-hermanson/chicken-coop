import datetime
import random

from flask import Blueprint, render_template, redirect, url_for, request

from main import db, logger
from main.modules.shifts.forms import AssignRecurringShiftForm, AssignSpecificShiftForm
from main.modules.shifts.models import Shift, SpecificShiftInstanceAssignment
from main.modules.shifts.services import generate_assign_shift_view_model, assign_specific_shift, \
    get_specific_shift_instance_assignments
from utils.date_time_enums import TimeOfDayEnum

shifts = Blueprint("shifts", __name__, url_prefix="/shifts")


@shifts.route("/")
def index_redirect():
    return redirect(url_for("shifts.recurring_shift_signup"), 301)


@shifts.route("/recurring")
def recurring_shift_signup():
    raw_shifts_list = Shift.query.order_by(Shift.day_of_week, Shift.time_of_day).all()
    shifts_list = [generate_assign_shift_view_model(shift) for shift in raw_shifts_list]

    return render_template("shifts/recurring-shift-signup.html",
                           shifts_list=shifts_list)


@shifts.route("/sign-up", methods=["POST"])
def sign_up():
    form = AssignRecurringShiftForm()
    shift = Shift.query.get_or_404(form.shift_id.data)

    if form.validate_on_submit():

        if form.assigned_to.data.strip() == "":
            shift.assigned_to = None
            alert_message = "Successfully unassigned shift.", "success"
        else:
            shift.assigned_to = form.assigned_to.data
            alert_message = f"Successfully assigned shift to {shift.assigned_to}.", "success"

        shift.seeking_replacement = form.seeking_replacement.data

        db.session.commit()

        assign_shift_view_model = generate_assign_shift_view_model(shift)

        return render_template("shifts/partials/recurring-shift-signup-partial.html",
                               assign_shift_view_model=assign_shift_view_model,
                               alert_message=alert_message)
    else:
        return render_template("shifts/partials/recurring-shift-signup-partial.html",
                               assign_shift_view_model=generate_assign_shift_view_model(shift, form))


@shifts.route("/specific")
def specific_shift_signup():
    form = AssignSpecificShiftForm()
    specific_shift_instance_assignments = get_specific_shift_instance_assignments()
    return render_template("shifts/specific-shift-signup.html",
                           form=form,
                           specific_shift_instance_assignments=specific_shift_instance_assignments)


@shifts.route("/specific/create-update", methods=["POST"])
def specific_shift_signup_create_update():
    form = AssignSpecificShiftForm()
    logger.info("Specific shift signup %s", form.data)
    if form.validate_on_submit():
        specific_shift_instance_assignment = assign_specific_shift(form)
        logger.debug(f"Created or updated specific shift instance assignment with ID "
                     f"{specific_shift_instance_assignment.specific_shift_instance_assignment_id}")
        specific_shift_instance_assignments = get_specific_shift_instance_assignments()
        return render_template("shifts/partials/specific-shift-instance-signup-list-partial.html",
                               specific_shift_instance_assignments=specific_shift_instance_assignments)
    else:
        return "invalid " + form.errors.__str__()
