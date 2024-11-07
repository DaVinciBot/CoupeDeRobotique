import re
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
    FATAL = 5


class STYLES:
    LogLevelsColorsDict: dict[LogLevels, str] = {
        LogLevels.DEBUG: Style.RESET_ALL + Fore.BLUE,
        LogLevels.INFO: Style.RESET_ALL + Back.BLUE,
        LogLevels.WARNING: Style.RESET_ALL + Back.YELLOW,
        LogLevels.ERROR: Style.RESET_ALL + Back.RED,
        LogLevels.CRITICAL: Style.RESET_ALL + Back.RED + Fore.YELLOW,
        LogLevels.FATAL: Style.RESET_ALL + Back.RED + Fore.YELLOW,  # TODO: to update
    }
    RESET_ALL = Style.RESET_ALL
    DATE = Style.RESET_ALL + Fore.YELLOW
    IDENTIFIER = Style.RESET_ALL + Style.BRIGHT + Fore.LIGHTGREEN_EX
    MESSAGE = Style.RESET_ALL
    DIM = Style.DIM
    BRIGHT = Style.BRIGHT


def center_and_limit(text: str, width: int, trailing_dots: int = 2):
    return (
        (text[: width - trailing_dots] + "." * trailing_dots)
        if len(text) > width
        else text.center(width)
    )


def style(text: str, style: str) -> str:
    """Style text with ANSI escape sequences

    Args:
        text (str): Text to style
        style (str): Style to apply (should be ANSI)

    Returns:
        str: Result
    """
    return style + text + (STYLES.RESET_ALL if style != "" else "")


# 7-bit C1 ANSI sequences
ansi_escape = re.compile(
    r"""
    \x1B  # ESC
    (?:   # 7-bit C1 Fe (except CSI)
        [@-Z\\-_]
    |     # or [ for CSI, followed by a control sequence
        \[
        [0-?]*  # Parameter bytes
        [ -/]*  # Intermediate bytes
        [@-~]   # Final byte
    )
""",
    re.VERBOSE,
)


def strip_ANSI(text: str) -> str:
    """Remove ANSI escape sequences from the text through RegEx

    Args:
        text (str): Text to strip from

    Returns:
        str: Result
    """
    return ansi_escape.sub("", text)
