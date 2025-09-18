"""Enumerations for identifying robot team colors."""

from __future__ import annotations

from enum import Enum


class TeamColor(Enum):
    """Enumerate the available team colors.

    Attributes:
        YELLOW: Yellow team.
        BLUE: Blue team.
        UNDEFINED: Team color not set.
    """

    YELLOW = "yellow"
    """Yellow team."""
    BLUE = "blue"
    """Blue team."""
    UNDEFINED = "undefined"
    """Team color not set."""
