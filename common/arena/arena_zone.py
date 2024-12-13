# ====== Imports ======
# Standard library imports
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


# ====== Base Zone Class ======
class BaseArenaZone:
    """
    Represents a general zone in the arena.

    Attributes:
        polygon (Polygon): The geometric representation of the zone.
        zone_type (ZoneType): The type of the zone.
    """

    def __init__(self, polygon: Polygon, zone_type: ZoneType,zone_color : str = "#742A2A") -> None:
        self.polygon: Polygon = polygon
        self.zone_type: ZoneType = zone_type
        self.zone_color = zone_color


# ====== Specific Zone Classes ======
class EnemyZone(BaseArenaZone):
    """Zone designated for enemies."""

    def __init__(self, polygon: Polygon) -> None:
        super().__init__(polygon, ZoneType.ENEMY,"#EE950F")


class StuffZone(BaseArenaZone):
    """Zone designated for storage or stuff placement."""

    def __init__(self, polygon: Polygon) -> None:
        super().__init__(polygon, ZoneType.STUFF_ZONE,"#0FEE9C")


class ForbiddenZone(BaseArenaZone):
    """Zone where access is restricted."""

    def __init__(self, polygon: Polygon) -> None:
        super().__init__(polygon, ZoneType.FORBIDDEN,"#8D0909")


class BlueReservedZone(BaseArenaZone):
    """Zone reserved for blue team operations."""

    def __init__(self, polygon: Polygon) -> None:
        super().__init__(polygon, ZoneType.BLUE_RESERVED,"#097D8D")


class YellowReservedZone(BaseArenaZone):
    """Zone reserved for yellow team operations."""

    def __init__(self, polygon: Polygon) -> None:
        super().__init__(polygon, ZoneType.YELLOW_RESERVED,"#ECC92E")


class BorderZone(BaseArenaZone):
    """Zone representing the border of the arena."""

    def __init__(self, polygon: Polygon) -> None:
        super().__init__(polygon, ZoneType.BORDER_ZONE,"#EF0D0D")


# ====== Code Summary ======
# The code defines a set of classes to manage different zones in an arena.
# It includes an enumeration for zone types, a base zone class (`BaseArenaZone`),
# and derived classes for specific zone types (`EnemyZone`, `StuffZone`, etc.).
# Each class associates a polygonal geometry with a zone type to represent spatial areas logically.
