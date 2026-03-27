"""Crate model used by spatial computation and rendering."""

from dataclasses import dataclass


@dataclass
class Crate:
    """Represent a crate with position, color, and zone metadata."""

    zone_id: int
    x: float
    y: float
    color_id: int
    held: bool = False

    @property
    def color(self) -> str:
        """Return the display color hex for the crate."""
        return "#005B8C" if self.color_id == 0 else "#F7B500"
