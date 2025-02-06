# ====== Imports ======
# Standard library imports
from colorama import Fore, Back, Style

# Internal project imports
from logger.log_levels import LogLevels
from logger.colors.base import BaseColors


class ClassicColors(BaseColors):
    """
    Classic color theme for logs.
    """
    LogLevelsColorsDict = {
        LogLevels.DEBUG:    Style.RESET_ALL +               Fore.LIGHTBLACK_EX,
        LogLevels.INFO:     Style.RESET_ALL +               Fore.LIGHTBLUE_EX   + BaseColors.BRIGHT,
        LogLevels.WARNING:  Style.RESET_ALL + Back.YELLOW,
        LogLevels.ERROR:    Style.RESET_ALL +               Fore.RED            + BaseColors.BRIGHT,
        LogLevels.CRITICAL: Style.RESET_ALL + Back.RED +    Fore.LIGHTWHITE_EX  + BaseColors.DIM,
        LogLevels.FATAL:    Style.RESET_ALL + Back.RED +    Fore.BLACK          + BaseColors.BRIGHT,
    }

    DATE = Style.RESET_ALL + Fore.YELLOW
    IDENTIFIER = Style.RESET_ALL + Style.BRIGHT + Fore.LIGHTGREEN_EX
    FILENAME = Style.RESET_ALL + Fore.BLUE
    LINENO = Style.RESET_ALL + Fore.MAGENTA + BaseColors.DIM
    MESSAGE = ""


