from flask import Blueprint, redirect, url_for
from main import logger

main = Blueprint("main", __name__, url_prefix="")


@main.route("/")
def index():
    return "main index"
