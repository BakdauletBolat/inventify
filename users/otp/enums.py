from enum import Enum


class SmsStatus(Enum):
    NOT_CREATED = 0
    INVALID_CODE = 1
    TIMEOUT = 2
    SUCCESS = 3
