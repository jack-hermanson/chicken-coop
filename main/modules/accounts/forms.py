from flask_wtf import FlaskForm
from sqlalchemy import func
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, ValidationError, EqualTo

from main.modules.accounts.models import Account

name_length = Length(min=2, max=15)
password_length = Length(max=100)


class CreateOrEditFormBase(FlaskForm):
    """Just the base - inherit this in create and edit"""
    name = StringField(
        "Name",
        validators=[DataRequired(), name_length],
        render_kw={
            "autofocus": "true",
        },
        description="Just your first name, not case-sensitive."
    )


class LoginForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired(), name_length], description="Just your first name, this acts as your username.", render_kw={
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


class CreateAccountForm(CreateOrEditFormBase):
    password = PasswordField("Password", validators=[DataRequired(), password_length])
    confirm_password = PasswordField(
        "Confirm Password",
        validators=[
            DataRequired(),
            EqualTo("password", "Your passwords must match.")
        ]
    )
    submit = SubmitField("Create Account")

    @staticmethod
    def validate_name(_, name):
        stripped_name = name.data.strip()
        if Account.query.filter(func.lower(Account.name) == func.lower(stripped_name)).all():
            raise ValidationError("That name has already been taken.")


# if we allowed editing name, then CreateOrEditFormBase will be used, until then don't inherit
# class EditAccountForm(CreateOrEditFormBase):
class EditAccountForm(FlaskForm):
    password = PasswordField("Password", validators=[password_length])
    confirm_password = PasswordField(
        "Confirm Password",
        validators=[
            EqualTo("password", "Your passwords must match.")
        ]
    )
    submit = SubmitField("Save Changes")

    @staticmethod
    def validate_password(_, password):
        if len(password.data) > password_length.max:
            raise ValidationError(f"Name must be fewer than {password_length.max} characters")

