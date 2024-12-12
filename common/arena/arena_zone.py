from geometry import (
    Point,
    MultiPoint,
    Polygon,
    MultiPolygon,
    LineString,
    BufferCapStyle,
    BufferJoinStyle,
    Geometry,
    create_straight_rectangle,
    prepare,
    distance,
    OrientedPoint,
    nearest_points,
)
from enum import Enum, auto


class ZoneType(Enum):
    YELLOW_RESERVED = auto()
    BLUE_RESERVED = auto()

    FORBIDDEN = auto()

    STUFF_ZONE = auto()

    ENEMY = auto()

    BORDER_ZONE = auto()


class BaseArenaZone:
    def __init__(self, polygon: Polygon, zone_type: ZoneType) -> None:
        self.polygon: Polygon = polygon
        self.zone_type: ZoneType = zone_type


class EnemyZone(BaseArenaZone):
    def __init__(self, polygon: Polygon) -> None:
        super().__init__(polygon, ZoneType.ENEMY)


class StuffZone(BaseArenaZone):
    def __init__(self, polygon: Polygon) -> None:
        super().__init__(polygon, ZoneType.STUFF_ZONE)


class ForbiddenZone(BaseArenaZone):
    def __init__(self, polygon: Polygon) -> None:
        super().__init__(polygon, ZoneType.FORBIDDEN)


class BlueReservedZone(BaseArenaZone):
    def __init__(self, polygon: Polygon) -> None:
        super().__init__(polygon, ZoneType.BLUE_RESERVED)


class YellowReservedZone(BaseArenaZone):
    def __init__(self, polygon: Polygon) -> None:
        super().__init__(polygon, ZoneType.YELLOW_RESERVED)


class BorderZone(BaseArenaZone):
    def __init__(self, polygon: Polygon) -> None:
        super().__init__(polygon, ZoneType.BORDER_ZONE)
