from enum import IntEnum


class TimeOfDayEnum(IntEnum):
    MORNING = 1
    AFTERNOON = 2


# These start at 0 because date.today().weekday() starts at 0 for Monday
class DayOfWeekEnum(IntEnum):
    MONDAY = 0
    TUESDAY = 1
    WEDNESDAY = 2
    THURSDAY = 3
    FRIDAY = 4
    SATURDAY = 5
    SUNDAY = 6


class MonthEnum(IntEnum):
    JANUARY = 1
    FEBRUARY = 2
    MARCH = 3
    APRIL = 4
    MAY = 5
    JUNE = 6
    JULY = 7
    AUGUST = 8
    SEPTEMBER = 9
    OCTOBER = 10
    NOVEMBER = 11
    DECEMBER = 12


