# ====== Imports ======
# Standard library imports
from colorama import Fore, Back, Style

# Internal project imports
from logger.log_levels import LogLevels


# ====== Class Part ======

class BaseColors:
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
    DIM: str = ""
    BRIGHT: str = ""

    @classmethod
    def get_log_level_color(cls, level: LogLevels) -> str:
        return cls.LogLevelsColorsDict.get(level, cls.RESET_ALL)


class ClassicColors(BaseColors):
    LogLevelsColorsDict = {
        LogLevels.DEBUG: Style.RESET_ALL + Fore.BLUE,
        LogLevels.INFO: Style.RESET_ALL + Back.BLUE,
        LogLevels.WARNING: Style.RESET_ALL + Back.YELLOW,
        LogLevels.ERROR: Style.RESET_ALL + Back.RED,
        LogLevels.CRITICAL: Style.RESET_ALL + Back.RED + Fore.YELLOW,
        LogLevels.FATAL: Style.RESET_ALL + Back.RED + Fore.YELLOW,  # TODO: to update
    }

    DATE: str = Style.RESET_ALL + Fore.YELLOW
    IDENTIFIER: str = Style.RESET_ALL + Style.BRIGHT + Fore.LIGHTGREEN_EX
    FILENAME: str = Style.RESET_ALL + Fore.LIGHTCYAN_EX
    LINENO: str = Style.RESET_ALL + Fore.LIGHTMAGENTA_EX
    MESSAGE: str = Style.RESET_ALL
    DIM: str = Style.DIM
    BRIGHT: str = Style.BRIGHT
