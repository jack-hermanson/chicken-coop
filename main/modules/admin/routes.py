from flask import Blueprint, render_template

from ..shifts.forms import AssignShiftForm
from ..shifts.models import Shift
from ..shifts.services import generate_assign_shift_view_model
from ... import db

admin = Blueprint("admin", __name__, url_prefix="/admin")


@admin.route("/")
def index():
    return render_template("admin/index.html")


@admin.route("/shifts")
def shifts():
    raw_shifts_list = Shift.query.all()
    shifts_list = [generate_assign_shift_view_model(shift) for shift in raw_shifts_list]

    return render_template("admin/shifts.html",
                           shifts_list=shifts_list)


@admin.route("/save-shift", methods=["POST"])
def save_shift():
    form = AssignShiftForm()
    if form.validate_on_submit():
        shift = Shift.query.get_or_404(form.shift_id.data)

        if form.assigned_to.data.strip() == "":
            shift.assigned_to = None
            alert_message = "Successfully unassigned shift."
        else:
            shift.assigned_to = form.assigned_to.data
            alert_message = f"Successfully assigned shift to {shift.assigned_to}."

        db.session.commit()

        return render_template("admin/partials/admin-shift-partial.html",
                               assign_shift_view_model=generate_assign_shift_view_model(shift),
                               alert_message=alert_message)
    # todo

    #     shift_instance = Shift.query.get_or_404(int(form.shift_id.data))
    #     shift_instance.completed_timestamp = form.completed_timestamp.data
    #     shift_instance.completed_by = form.completed_by.data
    #     db.session.commit()
    #
    #     response = make_response(redirect(url_for("main.index")))
    #     response.set_cookie("name", form.completed_by.data)
    #     flash(f"Successfully updated {day_of_week_str(shift_instance.shift.day_of_week)} "
    #           f"{time_of_day_str(shift_instance.shift.time_of_day)}.", "success")
    #     return response
    # else:
    #     flash(f"Failed with errors: {form.errors}", "danger")
    #     return redirect(url_for("main.index"))

@admin.route("/users")
def users():
    return render_template("admin/users.html")
