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
        stuff_zone_logger = Logger(
            identifier="StuffZone",
            decorator_level=LogLevels.INFO,
            print_log_level=LogLevels.DEBUG,
            file_log_level=LogLevels.DEBUG,
        )

        yellow_reserved_zone_logger = Logger(
            identifier="YellowReservedZone",
            decorator_level=LogLevels.INFO,
            print_log_level=LogLevels.DEBUG,
            file_log_level=LogLevels.DEBUG,
        )

        blue_reserved_zone_logger = Logger(
            identifier="BlueReservedZone",
            decorator_level=LogLevels.INFO,
            print_log_level=LogLevels.DEBUG,
            file_log_level=LogLevels.DEBUG,
        )

        forbidden_zone_logger = Logger(
            identifier="ForbiddenZone",
            decorator_level=LogLevels.INFO,
            print_log_level=LogLevels.DEBUG,
            file_log_level=LogLevels.DEBUG,
        )

        stuff_zones_points = [
            ((2.5, 20), (7.5, 60)),
            ((2.5, 115), (7.5, 155)),
            ((57.5, 20), (97.5, 30)),
            ((90, 90), (130, 100)),
            ((300 - 7.5, 20), (300 - 2.5, 60)),
            ((300 - 7.5, 115), (300 - 2.5, 155)),
            ((300 - 97.5, 20), (300 - 57.5, 30)),
            ((300 - 130, 90), (300 - 90, 100))
        ]

        yellow_reserved_zones_points = [
            ((0, 0), (45, 15)),
            ((0, 65), (45, 110)),
            ((300 - 60, 165), (300 - 15, 200)),
            ((300 - 105, 165), (300 - 60, 180)),
            ((300 - 100, 0), (300 - 55, 15)),
            ((300 - 145, 0), (300 - 100, 45))
        ]

        blue_reserved_zones_points = [
            ((15, 165), (60, 200)),
            ((60, 165), (105, 180)),
            ((55, 0), (100, 15)),
            ((100, 0), (145, 45)),
            ((300 - 45, 0), (300 - 0, 15)),
            ((300 - 45, 65), (300 - 0, 110))
        ]

        forbidden_zones_points = [
            ((290, 190), (300, 200))
        ]

        zones: list[BaseArenaZone] = []

        for point in stuff_zones_points:
            zones.append(
                StuffZone(
                    logger=stuff_zone_logger,
                    buffer_size=obstacle_buffer,
                    polygon=create_straight_rectangle(Point(*point[0]), Point(*point[1])),
                )
            )

        for point in yellow_reserved_zones_points:
            zones.append(
                YellowReservedZone(
                    logger=yellow_reserved_zone_logger,
                    buffer_size=obstacle_buffer,
                    polygon=create_straight_rectangle(Point(*point[0]), Point(*point[1])),
                )
            )

        for point in blue_reserved_zones_points:
            zones.append(
                BlueReservedZone(
                    logger=blue_reserved_zone_logger,
                    buffer_size=obstacle_buffer,
                    polygon=create_straight_rectangle(Point(*point[0]), Point(*point[1])),
                )
            )

        for point in forbidden_zones_points:
            zones.append(
                ForbiddenZone(
                    logger=forbidden_zone_logger,
                    buffer_size=obstacle_buffer,
                    polygon=create_straight_rectangle(Point(*point[0]), Point(*point[1])),
                )
            )

        # This is the scene for the rockstar
        rockstar_stage = ForbiddenZone(logger=forbidden_zone_logger,
                                       buffer_size=obstacle_buffer,
                                       polygon=Polygon(((65, 200), (65, 180), (105, 180), (105, 155),
                                                        (195, 155), (195, 180), (235, 180), (235, 200), (65, 200)))
                                       )
        zones.append(rockstar_stage)

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
