"""Crate model used by spatial computation and rendering."""

from dataclasses import dataclass


@dataclass
class Crate:
    """Represent a crate with position, color, and zone metadata.

    Attributes:
        zone_id (int): Zone identifier where the crate is located.
        x (float): X coordinate of the crate center.
        y (float): Y coordinate of the crate center.
        color_id (int): Integer color identifier (0 blue, 1 yellow).
        held (bool): Whether the crate is currently held.
    """

    zone_id: int
    x: float
    y: float
    color_id: int
    held: bool = False

    @property
    def color(self) -> str:
        """Return the display color hex for the crate."""
        return "#005B8C" if not self.color_id else "#F7B500"
