from enum import IntEnum


class LogLevels(IntEnum):
    # Log levels in ascending priority
    DEBUG = 0
    INFO = 1
    WARNING = 2
    ERROR = 3
    CRITICAL = 4
