from enum import IntEnum

from colorama import just_fix_windows_console, Fore, Back, Style

just_fix_windows_console()  # Enables colors in windows consoles (why not)


class LogLevels(IntEnum):
    # Log levels in ascending priority
    DEBUG = 0
    INFO = 1
    WARNING = 2
    ERROR = 3
    CRITICAL = 4


class STYLES:
    LogLevelsColorsDict: dict[LogLevels, str] = {
        LogLevels.DEBUG: Style.RESET_ALL + Back.WHITE,
        LogLevels.INFO: Style.RESET_ALL + Back.BLUE,
        LogLevels.WARNING: Style.RESET_ALL + Back.YELLOW,
        LogLevels.ERROR: Style.RESET_ALL + Back.RED,
        LogLevels.CRITICAL: Style.RESET_ALL + Back.RED + Fore.YELLOW,
    }
    RESET_ALL = Style.RESET_ALL
    DATE = Style.RESET_ALL + Fore.YELLOW
    IDENTIFIER = Style.RESET_ALL + Style.BRIGHT + Fore.LIGHTGREEN_EX
    MESSAGE = Style.RESET_ALL
    DIM = Style.DIM
    BRIGHT = Style.BRIGHT


def center_and_limit(string: str, width: int, trailing_dots: int = 2):
    return (
        (string[: width - trailing_dots] + "." * trailing_dots)
        if len(string) > width
        else string.center(width)
    )
