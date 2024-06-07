from flask import Blueprint, render_template

from ..shifts.forms import AssignShiftForm
from ..shifts.models import Shift
from ..shifts.services import generate_assign_shift_view_model
from ... import db

admin = Blueprint("admin", __name__, url_prefix="/admin")


@admin.route("/")
def index():
    return render_template("admin/index.html")


@admin.route("/users")
def users():
    return render_template("admin/users.html")
