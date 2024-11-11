import os
import datetime
from flask_mail import Message

from flask import render_template

from dotenv import load_dotenv
from sqlalchemy import and_, func

from main import db
from main.modules.shifts.models import ShiftInstance, Shift
from utils.date_time_enums import TimeOfDayEnum, DayOfWeekEnum
from utils import date_functions

from main import mail

load_dotenv()

EMAIL_SENDER = (
    "Morey Chickens",
    os.environ.get("EMAIL_FROM_ADDRESS")
)


def send_status_email():
    relevant_shift_instance = get_relevant_shift_instance()
    shift_was_completed = relevant_shift_instance.completed_timestamp is not None
    person_responsible = relevant_shift_instance.instance_assigned_to if (
        relevant_shift_instance.instance_assigned_to is not None) \
        else relevant_shift_instance.shift.assigned_to
    shift_was_completed_text = (f"Completed by {relevant_shift_instance.completed_by} at"
                                f"{relevant_shift_instance.completed_timestamp.strftime('%l:%M %p')}") \
        if shift_was_completed else f"NOT COMPLETED by {person_responsible}"
    eggs = relevant_shift_instance.eggs

    day_of_week_str = date_functions.day_of_week_str(relevant_shift_instance.shift.day_of_week)
    time_of_day_str = date_functions.time_of_day_str(relevant_shift_instance.shift.time_of_day)

    summary_text = f"{day_of_week_str} {time_of_day_str} - {shift_was_completed_text}"

    email_body = render_template("emails/status-email.html",
                                 summary_text=summary_text,
                                 person_responsible=person_responsible,
                                 day_of_week_str=day_of_week_str,
                                 time_of_day_str=time_of_day_str,
                                 shift_was_completed=shift_was_completed,
                                 eggs=eggs)
    # Create the email
    message = Message(
        subject=summary_text,
        sender=EMAIL_SENDER,
        html=email_body
    )
    message.recipients = [os.environ.get("REMINDER_RECIPIENT_EMAIL_ADDRESS")]
    mail.send(message)


# Utility functions

def get_current_time_of_day() -> TimeOfDayEnum:
    if datetime.datetime.now().hour >= 12:
        return TimeOfDayEnum.EVENING
    return TimeOfDayEnum.MORNING


def get_relevant_shift_instance() -> ShiftInstance:
    time_of_day = get_current_time_of_day()
    today = datetime.datetime.today().date()
    shift_instance = db.session.query(ShiftInstance) \
        .join(ShiftInstance.shift) \
        .filter(and_(
        Shift.time_of_day == time_of_day,
        func.date(ShiftInstance.due_date) == today
    )).first_or_404()

    return shift_instance
