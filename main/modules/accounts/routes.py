from flask import Blueprint, render_template

from main.modules.accounts.forms import LoginForm

accounts = Blueprint("accounts", __name__, url_prefix="/accounts")


@accounts.route("/login")
def login():
    form = LoginForm()
    if form.validate_on_submit():
        pass
    return render_template("accounts/login.html",
                           form=form)

