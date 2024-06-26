import time

from flask_wtf import FlaskForm
from wtforms import DateTimeLocalField, StringField, SubmitField, HiddenField, TelField, BooleanField
from wtforms.validators import DataRequired, Optional, ValidationError
from datetime import datetime
from main import Config


class ShiftInstanceCompletedTimestampForm(FlaskForm):
    """
    Form for setting when a shift instance was completed and who completed it.
    """
    shift_instance_id = HiddenField()
    completed_timestamp = DateTimeLocalField(label="Completed Time", format='%Y-%m-%dT%H:%M', validators=[Optional()], default=datetime.now, description="When was this shift completed?")
    completed_by = StringField("Completed By", validators=[], description="Who completed this shift?")
    submit = SubmitField("Save")


class AssignShiftForm(FlaskForm):
    """
    Form for assigning shift to a person.
    """
    shift_id = HiddenField()
    assigned_to = StringField()
    secret_code = TelField(description="Prevents spam. Same code as the shed and the chicken coop padlock. Clears out "
                                       "after form is submitted.")
    seeking_replacement = BooleanField("Seeking Replacement", description="If checked, this shift is \"up for grabs\" "
                                                                          "for anyone willing to take it.")
    submit = SubmitField("Save")

    @staticmethod
    def validate_secret_code(_, secret_code):
        if secret_code.data != Config.SECRET_CODE:
            time.sleep(1)
            raise ValidationError("Incorrect code. Please message the WhatsApp group for help.")
