import time
from datetime import datetime

from flask import request, flash
from flask_login import login_user, current_user
from sqlalchemy import func

from .forms import CreateAccountForm, LoginForm
from .models import Account
from main import bcrypt, db


def register(form: CreateAccountForm) -> Account:
    hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
    user = Account()
    user.name = form.name.data.lower().strip()
    user.password = hashed_password
    db.session.add(user)
    db.session.commit()
    return user


def log_user_in(form: LoginForm):
    user = Account.query.filter(func.lower(Account.name) == func.lower(form.name.data)).first()
    if user and bcrypt.check_password_hash(user.password, form.password.data):
        login_user(user, remember=form.remember.data)
        last_login = user.last_login.strftime('%a %d %b %Y, %I:%M%p') \
            if user.last_login is not None else "never"
        flash(f"Welcome back, {user.name}. Your last login was {last_login}.", "info")
        current_user.last_login = datetime.now()
        db.session.commit()
        return True
    else:
        time.sleep(2)  # prevent spamming
        flash("Incorrect username or password.", "danger")
        return False
