from flask import Blueprint, render_template, url_for, request, make_response
from main import logger

main = Blueprint("main", __name__, url_prefix="")


@main.route("/")
def index():
    name = request.cookies.get("name") or ""
    return render_template("main/index.html",
                           prefilled_name=name)


@main.route("/submit-form", methods=["POST"])
def test():
    name = request.form.get("name")
    response = make_response(render_template("main/index.html",
                                             prefilled_name=name))
    response.set_cookie("name", name)
    return response
