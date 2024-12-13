# ====== Code Summary ======
# The code defines a framework for managing zones in an arena. It includes:
# - Enumerations for zone types (`ZoneType`) and their accessibility (`ZoneAccessibility`).
# - A base class (`BaseArenaZone`) to represent a generic zone
# with attributes for geometry, type, color, and visit counters.
# - Specialized classes derived from `BaseArenaZone` for specific zone types such as `EnemyZone`, `StuffZone`, etc.
# Each class provides default settings and configurations relevant to its purpose.

# ====== Imports ======
# Standard library imports
from abc import ABC, abstractmethod
from enum import Enum, auto

# Third-party library imports
from geometry import (
    Polygon,
    BufferCapStyle,
    BufferJoinStyle,
    Geometry,
    create_straight_rectangle,
    prepare,
    distance,
    Point,
    MultiPoint,
    LineString,
    OrientedPoint,
    nearest_points,
    MultiPolygon,
)


# ====== Enums ======
class ZoneType(Enum):
    """Enumeration for different types of zones in the arena."""
    YELLOW_RESERVED = auto()
    BLUE_RESERVED = auto()
    FORBIDDEN = auto()
    STUFF_ZONE = auto()
    ENEMY = auto()
    BORDER_ZONE = auto()


class ZoneAccessibility(Enum):
    """Enumeration for zone accessibility types in the arena."""
    FREE = auto()  # Free to navigate
    RESTRICTED = auto()  # Restricted access; emergencies only
    FORBIDDEN = auto()  # Forbidden access; cannot be entered


# ====== Base Zone Class ======
class BaseArenaZone(ABC):
    """
    Represents a zone within an arena with attributes for geometry, type, color, and navigability.

    Attributes:
        polygon (Polygon): The geometric shape of the zone.
        zone_type (ZoneType): The type/category of the zone.
        accessibility (ZoneAccessibility): The navigability of the zone.
        zone_color (str): The color representation of the zone.
        enemy_visits (int): Count of opponent visits.
        self_visits (int): Count of self visits.
    """

    def __init__(
            self,
            polygon: Polygon,
            zone_type: ZoneType,
            accessibility: ZoneAccessibility,
            zone_color: str = "#f0aef2",
    ) -> None:
        self.polygon: Polygon = polygon
        self.zone_type: ZoneType = zone_type
        self.accessibility: ZoneAccessibility = accessibility
        self.zone_color: str = zone_color
        self.enemy_visits: int = 0
        self.self_visits: int = 0

    def is_accessible(self, team_color=None) -> bool:
        if self.accessibility == ZoneAccessibility.FORBIDDEN:
            return False

    def is_accessible_for_emergency(self) -> bool:
        return self.accessibility != ZoneAccessibility.FORBIDDEN


# ====== Specific Zone Classes ======
class EnemyZone(BaseArenaZone):
    """Zone designated for enemies, dynamically updated based on their position."""

    def __init__(
            self, polygon: Polygon, accessibility: ZoneAccessibility = ZoneAccessibility.FORBIDDEN
    ) -> None:
        super().__init__(
            polygon=polygon, zone_type=ZoneType.ENEMY, accessibility=accessibility, zone_color="#EE950F"
        )


class StuffZone(BaseArenaZone):
    """Zone designated for storage or placement of items."""

    def __init__(
            self, polygon: Polygon, accessibility: ZoneAccessibility = ZoneAccessibility.RESTRICTED
    ) -> None:
        super().__init__(
            polygon=polygon, zone_type=ZoneType.STUFF_ZONE, accessibility=accessibility, zone_color="#0FEE9C"
        )


class BlueReservedZone(BaseArenaZone):
    """Zone reserved for operations of the blue team."""

    def __init__(
            self, polygon: Polygon, accessibility: ZoneAccessibility = ZoneAccessibility.RESTRICTED
    ) -> None:
        super().__init__(
            polygon=polygon, zone_type=ZoneType.BLUE_RESERVED, accessibility=accessibility, zone_color="#097D8D"
        )

    def is_accessible(self, team_color=None) -> bool:
        return super().is_accessible(team_color) and team_color.lower() in ["blue", "b"]


class YellowReservedZone(BaseArenaZone):
    """Zone reserved for operations of the yellow team."""

    def __init__(
            self, polygon: Polygon, accessibility: ZoneAccessibility = ZoneAccessibility.RESTRICTED
    ) -> None:
        super().__init__(
            polygon=polygon, zone_type=ZoneType.YELLOW_RESERVED, accessibility=accessibility, zone_color="#ECC92E"
        )

    def is_accessible(self, team_color=None) -> bool:
        return super().is_accessible(team_color) and team_color.lower() in ["yellow", "y"]


class BorderZone(BaseArenaZone):
    """Zone representing the borders of the arena."""

    def __init__(
            self, polygon: Polygon, accessibility: ZoneAccessibility = ZoneAccessibility.FORBIDDEN
    ) -> None:
        super().__init__(
            polygon=polygon, zone_type=ZoneType.BORDER_ZONE, accessibility=accessibility, zone_color="#EF0D0D"
        )
