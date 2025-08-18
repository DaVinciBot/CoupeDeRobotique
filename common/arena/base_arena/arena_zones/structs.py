"""Enumerations and records describing arena zones and movement."""

from dataclasses import dataclass
from enum import Enum, auto

from geometry import Point


# ====== Enums ======
class ZoneType(Enum):
    """Enumeration for different types of zones in the arena.

    Attributes:
        YELLOW_RESERVED: Reserved for the yellow team.
        BLUE_RESERVED: Reserved for the blue team.
        FORBIDDEN: Zone that cannot be accessed.
        STUFF_ZONE: Designated for storage or items.
        ENEMY: Zone associated with enemy activity.
        ALLY: Zone associated with ally activity.
        BORDER_ZONE: Represents arena borders.

    """

    YELLOW_RESERVED = auto()
    """Reserved for the yellow team."""
    BLUE_RESERVED = auto()
    """Reserved for the blue team."""
    FORBIDDEN = auto()
    """Zone that cannot be accessed."""
    STUFF_ZONE = auto()
    """Designated for storage or items."""
    ENEMY = auto()
    """Zone associated with enemy activity."""
    ALLY = auto()
    """Zone associated with ally activity."""
    BORDER_ZONE = auto()
    """Represents arena borders."""


class ZoneAccessibility(Enum):
    """Enumeration for zone accessibility types in the arena.

    Attributes:
        FREE: Free to navigate.
        RESTRICTED: Restricted access.
        FORBIDDEN: Completely inaccessible.

    """

    FREE = auto()
    """Free to navigate."""
    RESTRICTED = auto()
    """Restricted access."""
    FORBIDDEN = auto()
    """Completely inaccessible."""


# ====== Data Classes ======
@dataclass
class Record:
    """Represents a timestamped position record.

    Attributes:
        timestamp (float): Time of the record.
        position (Point): The position recorded.

    """

    timestamp: float
    """Time of the record."""
    position: Point
    """The position recorded."""


@dataclass
class SpeedVector:
    """Represents a speed vector with direction and magnitude.

    Attributes:
        speed (float): Magnitude of the speed.
        dx (float): Change in x-direction.
        dy (float): Change in y-direction.
        factor (float): Scaling factor for direction components (defaults to 1.0).

    """

    speed: float
    """Magnitude of the speed."""
    dx: float
    """Change in x-direction."""
    dy: float
    """Change in y-direction."""
    factor: float = 1.0
    """Scaling factor for direction components."""

    @property
    def factored_dx(self) -> float:
        """Returns the scaled change in the x-direction."""
        return self.dx * self.factor

    @property
    def factored_dy(self) -> float:
        """Returns the scaled change in the y-direction."""
        return self.dy * self.factor
