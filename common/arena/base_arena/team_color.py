from enum import Enum


class TeamColor(Enum):
    """Enumerate the available team colors.

    Attributes:
        YELLOW: Yellow team.
        BLUE: Blue team.
        UNDEFINED: Team color not set.
    """

    YELLOW = "yellow"
    BLUE = "blue"
    UNDEFINED = "undefined"
