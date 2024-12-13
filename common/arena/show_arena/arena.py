from arena.base_arena.arena import BaseArena

from logger import Logger, LogLevels
from arena.base_arena.grid_manager import GridManager

from arena.base_arena.arena_zone import (
    # Enums
    ZoneType,
    ZoneAccessibility,
    # Zones
    BaseArenaZone,
    ForbiddenZone,
    EnemyZone,
    StuffZone,
    BlueReservedZone,
    YellowReservedZone,
    BorderZone,
)

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
    box,
)


class ShowArena(BaseArena):
    def __init__(
        self,
        logger: Logger,
        border_buffer: float,
        obstacle_buffer: float,
        chunk_size: int = 2,
    ) -> None:
        zones: list[BaseArenaZone] = [
            # Stuff zones first
            StuffZone(create_straight_rectangle(Point(2.5, 20), Point(7.5, 60))),
            StuffZone(create_straight_rectangle(Point(2.5, 115), Point(7.5, 155))),
            StuffZone(create_straight_rectangle(Point(57.5, 20), Point(97.5, 30))),
            StuffZone(create_straight_rectangle(Point(90, 90), Point(130, 100))),
            StuffZone(
                create_straight_rectangle(Point(300 - 7.5, 20), Point(300 - 2.5, 60))
            ),
            StuffZone(
                create_straight_rectangle(Point(300 - 7.5, 115), Point(300 - 2.5, 155))
            ),
            StuffZone(
                create_straight_rectangle(Point(300 - 97.5, 20), Point(300 - 57.5, 30))
            ),
            StuffZone(
                create_straight_rectangle(Point(300 - 130, 90), Point(300 - 90, 100))
            ),
            # Reserved zones (yellow and blue)
            YellowReservedZone(create_straight_rectangle(Point(0, 0), Point(45, 15))),
            YellowReservedZone(create_straight_rectangle(Point(0, 65), Point(45, 110))),
            BlueReservedZone(create_straight_rectangle(Point(15, 165), Point(60, 200))),
            BlueReservedZone(
                create_straight_rectangle(Point(60, 165), Point(105, 180))
            ),
            BlueReservedZone(create_straight_rectangle(Point(55, 0), Point(100, 15))),
            BlueReservedZone(create_straight_rectangle(Point(100, 0), Point(145, 45))),
            BlueReservedZone(
                create_straight_rectangle(Point(300 - 45, 0), Point(300 - 0, 15))
            ),
            BlueReservedZone(
                create_straight_rectangle(Point(300 - 45, 65), Point(300 - 0, 110))
            ),
            YellowReservedZone(
                create_straight_rectangle(Point(300 - 60, 165), Point(300 - 15, 200))
            ),
            YellowReservedZone(
                create_straight_rectangle(Point(300 - 105, 165), Point(300 - 60, 180))
            ),
            YellowReservedZone(
                create_straight_rectangle(Point(300 - 100, 0), Point(300 - 55, 15))
            ),
            YellowReservedZone(
                create_straight_rectangle(Point(300 - 145, 0), Point(300 - 100, 45))
            ),
            ForbiddenZone(create_straight_rectangle(Point(290, 190), Point(300, 200))),
        ]

        super().__init__(
            logger,
            width=300,
            height=200,
            border_buffer=border_buffer,
            obstacle_buffer=obstacle_buffer,
            zones=zones,
            chunk_size=chunk_size,
        )

        self.logger.log("ShowArena initialized.", LogLevels.INFO)
        self.logger.log(f"Width: {self.width}, Height: {self.height}", LogLevels.DEBUG)
