from __future__ import annotations
from dateutil.relativedelta import relativedelta

from datetime import datetime, timedelta, date, time

from main import logger
from .date_time_enums import DayOfWeekEnum


def get_next_date_with_same_day_of_week(day_of_week: DayOfWeekEnum, exclude_today=True,
                                        offset_days=0, relative_to_date: datetime = None):
    """
    Relative to today, get the next date that has the specified day of the week.
    It will exclude today unless you tell it not to.
    """
    start = relative_to_date or datetime.now()
    if (not exclude_today) and start.weekday() == day_of_week:
        # today is the day of the week we're looking for, and that's allowed
        # so go ahead and return it.
        return start + timedelta(days=offset_days)

    # if we cannot use today, or today is not the day of the week we want,
    # try adding a certain number of days (1-7) until we get to the desired day
    logger.debug(f"{int(day_of_week)} - {start.weekday()}")
    days_ahead = day_of_week - start.weekday()
    if days_ahead <= 0:
        # already happened
        days_ahead += 7
    return (start + timedelta(days=days_ahead + offset_days)).date()


def extract_date(date_or_datetime: date | datetime) -> date:
    if isinstance(date_or_datetime, datetime):
        return date_or_datetime.date()
    if isinstance(date_or_datetime, date):
        return date_or_datetime  # nothing to change
    else:
        raise ValueError(
            f"Invalid type for date_or_datetime (value: {date_or_datetime}) (type: {type(date_or_datetime)}")


def extract_datetime(date_or_datetime: date | datetime) -> datetime:
    if isinstance(date_or_datetime, datetime):
        return date_or_datetime  # nothing to change
    if isinstance(date_or_datetime, date):
        return datetime.combine(date_or_datetime, time.min)
    else:
        raise ValueError(
            f"Invalid type for date_or_datetime (value: {date_or_datetime}) (type: {type(date_or_datetime)}")


def day_of_week_str(raw):
    try:
        return DayOfWeekEnum(int(raw)).name.capitalize()
    except Exception as e:
        return e.__str__()


def get_next_date_with_same_number(number: int, exclude_relative_to_date=True,
                                   relative_to_date=extract_date(datetime.now())):

    # next occurrence
    try:
        next_occurrence = relative_to_date.replace(day=number)
    except ValueError:
        print("value error")
        # we probably gave it a 31 when there are only 30 days, or a 29 or 30 when there are only 28
        next_occurrence = (relative_to_date.replace(day=1) + relativedelta(months=2)) + timedelta(days=-1)
        print("beyond error")

    print(f"next occurrence {next_occurrence.__str__()}")

    # past
    if next_occurrence < relative_to_date or (next_occurrence == relative_to_date and exclude_relative_to_date):
        logger.debug("past")
        # okay that day already occurred, so let's go to next month
        return next_occurrence + relativedelta(months=1)

    print("next occurrence")
    return next_occurrence  # equivalent to commented out lines
    # # present
    # if next_occurrence == relative_to_date and not exclude_relative_to_date:
    #     print("same date")
    #     return next_occurrence
    # if next_occurrence > relative_to_date:
    #     print(f"{next_occurrence.__str__()} > {relative_to_date.__str__()}")
    #     print("future")
    #     return next_occurrence
