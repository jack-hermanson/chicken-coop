from flask import Blueprint, render_template

dues = Blueprint("dues", __name__, url_prefix="/dues")


@dues.route("/")
def index():
    return render_template("dues/index.html")
