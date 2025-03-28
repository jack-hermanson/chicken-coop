from flask import Blueprint, render_template, request, redirect, url_for

guide = Blueprint("guide", __name__, url_prefix="/guide")

@guide.route("/")
def index():
    return render_template("guide/index.html")