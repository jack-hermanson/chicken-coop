from main import db
from utils.date_time_enums import DayOfWeekEnum, TimeOfDayEnum


class Shift(db.Model):
    """
    I think I'm gonna make it so a "shift" is generic.
    There will be 14, so 2 per day.
    Every shift creates a new ShiftInstance.
    """
    shift_id = db.Column(db.Integer, primary_key=True)
    day_of_week = db.Column(db.Integer, nullable=False, default=DayOfWeekEnum.MONDAY)
    time_of_day = db.Column(db.Integer, nullable=False, default=TimeOfDayEnum.MORNING)

    # who this is assigned to
    assigned_to = db.Column(db.String(128), nullable=True)
    # I had these, but I'm going to cheap out and just use a string
    # person_id = db.mapped_column(db.ForeignKey("person.person_id"), nullable=True)
    # person = db.relationship("Person", back_populates="shifts")
    seeking_replacement = db.Column(db.Boolean, nullable=False, default=False)

    shift_instances = db.relationship("ShiftInstance", back_populates="shift", cascade="all, delete-orphan")


class ShiftInstance(db.Model):
    """
    One instance of the shift. It has a specific date.
    """
    shift_instance_id = db.Column(db.Integer, primary_key=True)

    shift_id = db.mapped_column(db.ForeignKey("shift.shift_id"), nullable=False)
    shift = db.relationship("Shift", back_populates="shift_instances")
    due_date = db.Column(db.DateTime, nullable=False)
    completed_timestamp = db.Column(db.DateTime, nullable=True)
    completed_by = db.Column(db.String(32), nullable=True)

    # This particular instance of the shift is assigned to someone,
    # not necessarily the same person as the shift itself.
    instance_assigned_to = db.Column(db.String(128), nullable=True)

    # Record the sunrise time on mornings, sunset time on evenings
    sunrise_utc = db.Column(db.DateTime, nullable=True)
    sunset_utc = db.Column(db.DateTime, nullable=True)

    eggs_taken_home = db.Column(db.Integer, nullable=True)
    eggs_left_behind = db.Column(db.Integer, nullable=True)


class SpecificShiftInstanceAssignment(db.Model):
    specific_shift_instance_assignment_id = db.Column(db.Integer, primary_key=True)
    time_of_day = db.Column(db.Integer, nullable=False)
    instance_date = db.Column(db.DateTime, nullable=False)
    instance_assigned_to = db.Column(db.String(128), nullable=False)
