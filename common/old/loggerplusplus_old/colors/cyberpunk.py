# ====== Imports ======
# Standard library imports
from colorama import Fore, Back, Style

# Internal project imports
from logger.log_levels import LogLevels
from logger.colors.base import BaseColors


class CyberpunkColors(BaseColors):
    """
    Cyberpunk-inspired theme: neon colors and strong contrasts.
    """
    LogLevelsColorsDict = {
        LogLevels.DEBUG: Style.BRIGHT + Fore.LIGHTBLACK_EX,
        LogLevels.INFO: Style.BRIGHT + Fore.LIGHTCYAN_EX,
        LogLevels.WARNING: Style.BRIGHT + Back.LIGHTYELLOW_EX + Fore.BLACK,
        LogLevels.ERROR: Style.BRIGHT + Back.LIGHTRED_EX + Fore.WHITE,
        LogLevels.CRITICAL: Style.BRIGHT + Back.LIGHTMAGENTA_EX + Fore.LIGHTCYAN_EX,
        LogLevels.FATAL: Style.BRIGHT + Back.LIGHTRED_EX + Fore.YELLOW + BaseColors.BRIGHT,
    }

    DATE = Style.BRIGHT + Fore.LIGHTCYAN_EX
    IDENTIFIER = Style.BRIGHT + Fore.LIGHTGREEN_EX
    FILENAME = Style.BRIGHT + Fore.LIGHTBLUE_EX
    LINENO = Style.BRIGHT + Fore.LIGHTMAGENTA_EX
    MESSAGE = Style.BRIGHT + Fore.LIGHTWHITE_EX
