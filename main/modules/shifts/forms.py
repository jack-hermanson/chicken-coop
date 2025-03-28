import time

from flask_wtf import FlaskForm
from wtforms import DateTimeLocalField, StringField, SubmitField, HiddenField, TelField, BooleanField, SelectField, \
    DateField, IntegerField
from wtforms.validators import DataRequired, Optional, ValidationError, Length
from datetime import datetime
from main import Config
from utils.date_functions import time_of_day_str
from utils.date_time_enums import TimeOfDayEnum


class ShiftInstanceCompletedTimestampForm(FlaskForm):
    """
    Form for setting when a shift instance was completed and who completed it.
    """
    shift_instance_id = HiddenField()
    completed_timestamp = DateTimeLocalField(label="Completed Time", format='%Y-%m-%dT%H:%M', validators=[Optional()],
                                             default=datetime.now, description="When was this shift completed?")
    completed_by = StringField("Completed By", validators=[], description="Who completed this shift?")
    eggs = IntegerField(
        description="Please enter the amount of eggs you took home from the coop. (Enter 0 if none.)",
        default="0",
        validators=[Optional()],
        render_kw={
            "inputmode": "numeric",
            "placeholder": "The number of eggs you took home"
        }
    )
    submit = SubmitField("Save")


class AssignRecurringShiftForm(FlaskForm):
    """
    Form for assigning shift to a person.
    """
    shift_id = HiddenField()
    assigned_to = StringField(validators=[Length(max=128)])
    # secret_code = TelField(description="Prevents spam. Same code as the shed and the chicken coop padlock. Clears
    # out " "after form is submitted.")
    seeking_replacement = BooleanField("Seeking Replacement", description="If checked, this shift is \"up for grabs\" "
                                                                          "for anyone willing to take it.")
    submit = SubmitField("Save")

    # @staticmethod
    # def validate_secret_code(_, secret_code):
    #     if secret_code.data != Config.SECRET_CODE:
    #         time.sleep(1)
    #         raise ValidationError("Incorrect code. Please message the WhatsApp group for guide.")


class AssignSpecificShiftForm(FlaskForm):
    """
    Form for assigning a specific date for a shift to someone.
    """
    specific_shift_instance_assignment_id = HiddenField()  # for editing
    date = DateField(
        format='%Y-%m-%d',
        default=datetime.now,
        validators=[
            DataRequired()
        ],
        description="What is the exact date of the specific shift you wish to take?"
    )
    time_of_day = SelectField(
        "Time of Day",
        choices=[
            (int(TimeOfDayEnum.MORNING), time_of_day_str(TimeOfDayEnum.MORNING)),
            (int(TimeOfDayEnum.EVENING), time_of_day_str(TimeOfDayEnum.EVENING))
        ],
        validators=[
            DataRequired()
        ],
        description="Do you want the morning or evening shift?"
    )
    assigned_to = StringField(
        validators=[
            Length(max=128)
        ],
        description="Who is the person who will be taking that specific shift?"
    )

    submit = SubmitField(label="Save")
