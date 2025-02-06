# ====== Imports ======
# Standard library imports
from colorama import Fore, Back, Style

# Internal project imports
from logger.log_levels import LogLevels
from logger.colors.base import BaseColors


class NeonColors(BaseColors):
    """
    Neon theme with vibrant colors for high visibility.
    """
    LogLevelsColorsDict = {
        LogLevels.DEBUG: Style.BRIGHT + Fore.LIGHTGREEN_EX,
        LogLevels.INFO: Style.BRIGHT + Fore.LIGHTBLUE_EX,
        LogLevels.WARNING: Style.BRIGHT + Back.YELLOW + Fore.BLACK,
        LogLevels.ERROR: Style.BRIGHT + Back.RED + Fore.LIGHTWHITE_EX,
        LogLevels.CRITICAL: Style.BRIGHT + Back.MAGENTA + Fore.LIGHTCYAN_EX,
        LogLevels.FATAL: Style.BRIGHT + Back.RED + Fore.YELLOW + BaseColors.BRIGHT,
    }

    DATE = Style.BRIGHT + Fore.LIGHTCYAN_EX
    IDENTIFIER = Style.BRIGHT + Fore.LIGHTGREEN_EX
    FILENAME = Style.BRIGHT + Fore.LIGHTBLUE_EX
    LINENO = Style.BRIGHT + Fore.LIGHTMAGENTA_EX
    MESSAGE = Style.BRIGHT + Fore.LIGHTWHITE_EX
