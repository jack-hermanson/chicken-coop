from flask import Blueprint, render_template, abort
from flask_login import login_required, current_user

from ..accounts.ClearanceEnum import ClearanceEnum
from ..shifts.forms import AssignShiftForm
from ..shifts.models import Shift
from ..shifts.services import generate_assign_shift_view_model
from ... import db

admin = Blueprint("admin", __name__, url_prefix="/admin")


@admin.route("/")
@login_required
def index():
    if not current_user.min_clearance >= ClearanceEnum.ADMIN:
        return abort(403)
    return render_template("admin/index.html")


@admin.route("/users")
@login_required
def users():
    if not current_user.min_clearance >= ClearanceEnum.ADMIN:
        return abort(403)
    return render_template("admin/users.html")
