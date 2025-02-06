# ====== Imports ======
# Standard library imports
from colorama import Fore, Style

# Internal project imports
from logger.log_levels import LogLevels
from logger.colors.base import BaseColors


class PastelColors(BaseColors):
    """
    Soft pastel theme to reduce eye strain.
    """
    LogLevelsColorsDict = {
        LogLevels.DEBUG: Style.RESET_ALL + Fore.LIGHTMAGENTA_EX,
        LogLevels.INFO: Style.RESET_ALL + Fore.LIGHTCYAN_EX,
        LogLevels.WARNING: Style.RESET_ALL + Fore.LIGHTYELLOW_EX,
        LogLevels.ERROR: Style.BRIGHT + Fore.LIGHTRED_EX,
        LogLevels.CRITICAL: Style.BRIGHT + Fore.LIGHTBLUE_EX,
        LogLevels.FATAL: Style.BRIGHT + Fore.LIGHTRED_EX + BaseColors.BRIGHT,
    }

    DATE = Style.DIM + Fore.LIGHTWHITE_EX
    IDENTIFIER = Style.BRIGHT + Fore.LIGHTBLUE_EX
    FILENAME = Style.BRIGHT + Fore.LIGHTGREEN_EX
    LINENO = Style.BRIGHT + Fore.LIGHTMAGENTA_EX
    MESSAGE = Style.BRIGHT + Fore.LIGHTBLACK_EX
