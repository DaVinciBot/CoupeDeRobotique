# ====== Code Summary ======
# This module defines different color schemes for log levels using the `colorama` library.
# It provides a base class (`BaseColors`) and multiple subclasses (`ClassicColors`, `DarkModeColors`, etc.)
# that define color mappings for log levels such as DEBUG, INFO, WARNING, ERROR, CRITICAL, and FATAL.
# These classes can be used to format log messages with different visual styles.

# ====== Imports ======
# Standard library imports
from colorama import Fore, Back, Style

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


# ====== Log Color Themes ======
class ClassicColors(BaseColors):
    """
    Classic color theme for logs.
    """
    LogLevelsColorsDict = {
        LogLevels.DEBUG: Style.RESET_ALL + Fore.BLUE,
        LogLevels.INFO: Style.RESET_ALL + Back.BLUE,
        LogLevels.WARNING: Style.RESET_ALL + Back.YELLOW,
        LogLevels.ERROR: Style.RESET_ALL + Back.RED,
        LogLevels.CRITICAL: Style.RESET_ALL + Back.RED + Fore.YELLOW,
        LogLevels.FATAL: Style.BRIGHT + Back.RED + Fore.WHITE + BaseColors.BRIGHT,
    }

    DATE = Style.RESET_ALL + Fore.YELLOW
    IDENTIFIER = Style.RESET_ALL + Style.BRIGHT + Fore.LIGHTGREEN_EX
    FILENAME = Style.RESET_ALL + Fore.LIGHTCYAN_EX
    LINENO = Style.RESET_ALL + Fore.LIGHTMAGENTA_EX
    MESSAGE = ""


class DarkModeColors(BaseColors):
    """
    Dark mode theme with high contrast for readability.
    """
    LogLevelsColorsDict = {
        LogLevels.DEBUG: Style.DIM + Fore.LIGHTBLACK_EX,
        LogLevels.INFO: Style.RESET_ALL + Fore.CYAN,
        LogLevels.WARNING: Style.BRIGHT + Fore.LIGHTYELLOW_EX,
        LogLevels.ERROR: Style.BRIGHT + Fore.LIGHTRED_EX,
        LogLevels.CRITICAL: Style.BRIGHT + Fore.RED + Back.BLACK,
        LogLevels.FATAL: Style.BRIGHT + Back.RED + Fore.WHITE + BaseColors.BRIGHT,
    }

    DATE = Style.DIM + Fore.LIGHTWHITE_EX
    IDENTIFIER = Style.BRIGHT + Fore.LIGHTBLUE_EX
    FILENAME = Style.BRIGHT + Fore.LIGHTCYAN_EX
    LINENO = Style.BRIGHT + Fore.LIGHTMAGENTA_EX
    MESSAGE = Style.BRIGHT + Fore.WHITE


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
