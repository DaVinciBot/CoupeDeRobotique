# ====== Code Summary ======
# This module defines enumerations and data classes for managing zones and movement within an arena.
# It includes zone types, accessibility levels, and structures for tracking positions and speed vectors.


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
    BLUE_RESERVED = auto()
    FORBIDDEN = auto()
    STUFF_ZONE = auto()
    ENEMY = auto()
    ALLY = auto()
    BORDER_ZONE = auto()


class ZoneAccessibility(Enum):
    """Enumeration for zone accessibility types in the arena.

    Attributes:
        FREE: Free to navigate.
        RESTRICTED: Restricted access.
        FORBIDDEN: Completely inaccessible.
    """

    FREE = auto()
    RESTRICTED = auto()
    FORBIDDEN = auto()


# ====== Data Classes ======
@dataclass
class Record:
    """Represents a timestamped position record.

    Attributes:
        timestamp (float): Time of the record.
        position (Point): The position recorded.
    """

    timestamp: float
    position: Point


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
    dx: float
    dy: float
    factor: float = 1.0

    @property
    def factored_dx(self) -> float:
        """Returns the scaled change in the x-direction."""
        return self.dx * self.factor

    @property
    def factored_dy(self) -> float:
        """Returns the scaled change in the y-direction."""
        return self.dy * self.factor
