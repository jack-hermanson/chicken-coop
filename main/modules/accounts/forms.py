from flask_wtf import FlaskForm
from sqlalchemy import func
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, ValidationError

from main.modules.accounts.models import Account

name_length = Length(min=2, max=15)
password_length = Length(max=100)


class LoginForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired(), name_length], render_kw={
        "autofocus": "true",
    })
    password = PasswordField("Password", validators=[DataRequired(), password_length], render_kw={
    })
    remember = BooleanField("Remember Me", default=True)
    submit = SubmitField("Log In")

    @staticmethod
    def validate_name(_, name):
        if not Account.query.filter(func.lower(Account.name) == func.lower(name.data)).count():
            raise ValidationError("Doesn't exist.")
