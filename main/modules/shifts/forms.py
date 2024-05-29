from flask_wtf import FlaskForm
from wtforms import DateTimeLocalField, StringField, SubmitField, HiddenField
from wtforms.validators import DataRequired, Optional
from datetime import datetime


class ShiftInstanceCompletedTimestampForm(FlaskForm):
    """
    Form for setting when a shift instance was completed and who completed it.
    """
    shift_instance_id = HiddenField()
    completed_timestamp = DateTimeLocalField(format='%Y-%m-%dT%H:%M', validators=[Optional()], default=datetime.now)
    completed_by = StringField("Completed By", validators=[])
    submit = SubmitField("Save")


class AssignShiftForm(FlaskForm):
    """
    Form for assigning shift to a person.
    """
    shift_id = HiddenField()
    assigned_to = StringField()
    submit = SubmitField("Save")
