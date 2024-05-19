from enum import IntEnum


class ClearanceEnum(IntEnum):
    SUPER_ADMIN = 5
    ADMIN = 2
    NORMAL = 1
    UNVERIFIED = 0
