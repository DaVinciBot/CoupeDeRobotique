# ====== Imports ======
# Standard library imports
from colorama import Fore, Back, Style

# Internal project imports
from logger.log_levels import LogLevels
from logger.colors.base import BaseColors


class DarkModeColors(BaseColors):
    """
    Dark mode theme with high contrast for readability.
    """
    LogLevelsColorsDict = {
        LogLevels.DEBUG: Style.RESET_ALL + Fore.LIGHTBLACK_EX,
        LogLevels.INFO: Style.RESET_ALL + Fore.CYAN + BaseColors.DIM,
        LogLevels.WARNING: Style.RESET_ALL + Fore.YELLOW,
        LogLevels.ERROR: Style.RESET_ALL + Fore.LIGHTRED_EX + BaseColors.BRIGHT,
        LogLevels.CRITICAL: Style.RESET_ALL + Back.LIGHTRED_EX + BaseColors.BRIGHT,
        LogLevels.FATAL: Style.RESET_ALL + Back.RED + Fore.BLACK + BaseColors.BRIGHT,
    }

    DATE = Style.RESET_ALL + Fore.LIGHTYELLOW_EX
    IDENTIFIER = Style.RESET_ALL + Style.BRIGHT + Fore.GREEN
    FILENAME = Style.RESET_ALL + Fore.LIGHTBLUE_EX
    LINENO = Style.RESET_ALL + Fore.MAGENTA
    MESSAGE = ""
