# ====== Imports ======
# Standard library imports
from colorama import Style

# Internal project imports
from logger.log_levels import LogLevels


# ====== Base Class for Log Colors ======
class BaseColors:
    """
    Base class for defining log level color mappings.
    """
    LogLevelsColorsDict = {
        LogLevels.DEBUG: "",
        LogLevels.INFO: "",
        LogLevels.WARNING: "",
        LogLevels.ERROR: "",
        LogLevels.CRITICAL: "",
        LogLevels.FATAL: "",
    }

    RESET_ALL: str = Style.RESET_ALL
    DATE: str = ""
    IDENTIFIER: str = ""
    FILENAME: str = ""
    LINENO: str = ""
    MESSAGE: str = ""

    DIM: str = Style.DIM
    BRIGHT: str = Style.BRIGHT

    @classmethod
    def get_log_level_color(cls, level: LogLevels) -> str:
        """
        Retrieve the color formatting for a given log level.

        Args:
            level (LogLevels): The log level.

        Returns:
            str: The color formatting string.
        """
        return cls.LogLevelsColorsDict.get(level, cls.RESET_ALL)
