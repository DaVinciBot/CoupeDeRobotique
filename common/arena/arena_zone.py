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
    DEFFAULT = auto()
    YELLOW_RESERVED = auto()
    BLUE_RESERVED = auto()
    FORBIDDEN = auto()
    STUFF_ZONE = auto()
    ENEMY = auto()
    BORDER_ZONE = auto()
    
class ZoneNavigability(Enum):
    """Enumeration for different types of zones in the arena."""
    FREE = auto()
    RESTRICTED = auto()
    FORBIDDEN = auto()


# ====== Base Zone Class ======
class BaseArenaZone:
    """
    Represents a zone within an arena.
    Attributes:
        polygon (Polygon): The geometric shape of the zone.
        zone_type (ZoneType): The type/category of the zone.
        zone_color (str): The color representation of the zone. Default is "#742A2A".
        navigability (ZoneNavigability): The navigability of the zone. Default is "FREE".
        visited_opposant (int): Counter for how many times the zone has been visited by the opponent.
        visited_self (int): Counter for how many times the zone has been visited by self.
    Args:
        polygon (Polygon): The geometric shape of the zone.
        zone_type (ZoneType): The type/category of the zone.
        navigability (ZoneNavigability): The navigability of the zone.
        zone_color (str, optional): The color representation of the zone. Default is "#742A2A".
    """

    def __init__(self,
            polygon: Polygon,
            zone_type: ZoneType = ZoneType.DEFFAULT,
            navigability: ZoneNavigability = ZoneNavigability.FREE,
            zone_color : str = "#f0aef2") -> None:
        self.polygon: Polygon = polygon
        self.zone_type: ZoneType = zone_type
        self.zone_color = zone_color
        self.navigability: ZoneNavigability = navigability
        self.visited_opposant = 0
        self.visited_self = 0


# ====== Specific Zone Classes ======
class EnemyZone(BaseArenaZone):
    """Zone designated for enemies."""

    def __init__(self, polygon: Polygon,navigability:ZoneNavigability=ZoneNavigability.FREE) -> None:
        super().__init__(polygon, ZoneType.ENEMY,navigability=navigability,zone_color="#EE950F")


class StuffZone(BaseArenaZone):
    """Zone designated for storage or stuff placement."""

    def __init__(self, polygon: Polygon,navigability:ZoneNavigability=ZoneNavigability.FREE) -> None:
        super().__init__(polygon, ZoneType.STUFF_ZONE,navigability=navigability,zone_color="#0FEE9C")


class BlueReservedZone(BaseArenaZone):
    """Zone reserved for blue team operations."""

    def __init__(self, polygon: Polygon,navigability:ZoneNavigability=ZoneNavigability.FREE) -> None:
        super().__init__(polygon, ZoneType.BLUE_RESERVED,navigability=navigability,zone_color="#097D8D")


class YellowReservedZone(BaseArenaZone):
    """Zone reserved for yellow team operations."""

    def __init__(self, polygon: Polygon,navigability:ZoneNavigability=ZoneNavigability.FREE) -> None:
        super().__init__(polygon, ZoneType.YELLOW_RESERVED,navigability=navigability,zone_color="#ECC92E")


class BorderZone(BaseArenaZone):
    """Zone representing the border of the arena."""

    def __init__(self, polygon: Polygon,navigability:ZoneNavigability=ZoneNavigability.FREE) -> None:
        super().__init__(polygon, ZoneType.BORDER_ZONE,navigability=navigability,zone_color="#EF0D0D")


# ====== Code Summary ======
# The code defines a set of classes to manage different zones in an arena.
# It includes an enumeration for zone types, a base zone class (`BaseArenaZone`),
# and derived classes for specific zone types (`EnemyZone`, `StuffZone`, etc.).
# Each class associates a polygonal geometry with a zone type to represent spatial areas logically.
