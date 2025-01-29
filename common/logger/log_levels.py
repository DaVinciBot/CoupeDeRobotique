# ====== Code Summary ======
# This script defines custom logging levels by modifying the built-in `logging` module.
# It also introduces a `LogLevels` enum to enhance clarity and usability when dealing with log levels.
# The purpose is to differentiate FATAL from CRITICAL (which are identical in the standard `logging` module)
# and to provide a dedicated enumeration for better type safety and code readability.

# ====== Imports ======
# Standard library imports
from enum import IntEnum
import logging

# ====== Custom Log Levels ======
# The default logging module defines these levels:
# CRITICAL = 50
# FATAL = CRITICAL
# ERROR = 40
# WARNING = 30
# WARN = WARNING
# INFO = 20
# DEBUG = 10
# NOTSET = 0
#
# However, FATAL and CRITICAL are the same in the built-in module, which may be confusing.
# To differentiate them, we manually assign a unique value to FATAL.

logging.FATAL = 60  # Assign a unique value to FATAL to distinguish it from CRITICAL
logging.CRITICAL = 50
logging.ERROR = 40
logging.WARNING = 30
logging.WARN = logging.WARNING
logging.INFO = 20
logging.DEBUG = 10
logging.NOTSET = 0


class LogLevels(IntEnum):
    """
    Enumeration for log levels to provide clear and explicit usage.
    This makes it clear that these are log levels and not just constants from the logging module.
    """
    FATAL = logging.FATAL  # Highest severity, explicitly separated from CRITICAL
    CRITICAL = logging.CRITICAL
    ERROR = logging.ERROR
    WARNING = logging.WARNING
    INFO = logging.INFO
    DEBUG = logging.DEBUG
    NOTSET = logging.NOTSET
