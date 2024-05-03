from flask_wtf import FlaskForm
from wtforms import DateTimeLocalField, StringField, SubmitField, HiddenField
from wtforms.validators import DataRequired


class ShiftInstanceCompletedTimestampForm(FlaskForm):
    """
    Form for setting when a shift instance was completed and who completed it.
    """
    shift_instance_id = HiddenField()
    completed_timestamp = DateTimeLocalField(format='%Y-%m-%dT%H:%M', validators=[DataRequired()])
    completed_by = StringField("Completed By", validators=[DataRequired()])
    submit = SubmitField("Save")
