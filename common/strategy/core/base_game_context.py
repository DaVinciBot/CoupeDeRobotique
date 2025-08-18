"""Shared game context passed to strategy components."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from arena import BaseArena


@dataclass
class BaseGameContext:
    """Container for the competition arena."""

    arena: BaseArena
    """A reference to the competition arena."""
