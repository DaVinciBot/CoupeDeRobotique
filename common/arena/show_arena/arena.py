from math import pi
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
        forbidden_cover_threshold: float = 0.5,
        grid_manager_logger: Logger = None,
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
            ((2.5, 20), (12.5, 60), [OrientedPoint(12,5 + x, 40, pi/2)]), #TODO: x = distance necessaire entre le robot et les conserves. Theta ??
            ((2.5, 112.5), (12.5, 152.5), [OrientedPoint(12,5 + x, 132.5, pi/2)]),
            ((57.5, 20), (97.5, 30), [OrientedPoint(77.5, 30 + x, 0)]),
            ((62.5, 167.5), (102.5, 177.5), [OrientedPoint(82.5, 167.5 - x, pi)]),
            ((90, 90), (130, 100), [OrientedPoint(110, 90 - x, pi), OrientedPoint(110, 100 + x, 0)]),
            ((300 - 12.5, 20), (300 - 2.5, 60), [OrientedPoint(300 - 12.5 - x, 40, -pi/2)]), #TODO: -pi/2 ou 3pi/2 ?? et je me suis pas trompé sur l'angle initial ?
            ((300 - 12.5, 112.5), (300 - 2.5, 152.5), [OrientedPoint(300 - 12.5 - x, 132.5, -pi/2)]),
            ((300 - 97.5, 20), (300 - 57.5, 30), [OrientedPoint(300 - 77.5, 30 + x, 0)]),
            ((300 - 102.5, 167.5), (300 - 62.5, 177.5), [OrientedPoint(300 - 82.5, 167.5 - x, pi)]),
            ((300 - 130, 90), (300 - 90, 100), [OrientedPoint(300 - 110, 90 - x, pi), OrientedPoint(300 - 110, 100 + x, 0)]),
        ]

        yellow_reserved_zones_points = [
            ((0, 0), (45, 15), [OrientedPoint(22.5, 15 + x, 0)]), #TODO: x = distance necessaire entre le robot et les zones jaunes. Theta ??
            ((0, 65), (45, 110), [OrientedPoint(22.5, 65 - x, pi), OrientedPoint(22.5, 110 + x, 0), OrientedPoint(45 + x, 87.5, pi/2)]),
            ((155,0), (200, 45), [OrientedPoint(177.5, 45 + x, 0), OrientedPoint(200 + x, 22.5, pi/2)]),
            ((200, 0), (245, 15), [OrientedPoint(222.5, 15 + x, 0)]),
        ]

        blue_reserved_zones_points = [
            ((255, 0), (300, 15), [OrientedPoint(277.5, 15 + x, 0)]),
            ((255, 65), (300, 110), [OrientedPoint(277.5, 65 - x, pi), OrientedPoint(277.5, 110 + x, 0), OrientedPoint(255 - x, 87.5, -pi/2)]),
            ((55, 0), (100, 15), [OrientedPoint(77.5, 15 + x, 0)]),
            ((100, 0), (145, 45), [OrientedPoint(122.5, 45 + x, 0), OrientedPoint(100 - x, 22.5, -pi/2)]),
        ]
        #TODO: backstage et pami sans zones ??

        forbidden_zones_points = []

        zones: list[BaseArenaZone] = []

        for (corner_point1, corner_point2, goto_points) in stuff_zones_points:
            zones.append(
                StuffZone(
                    logger=stuff_zone_logger,
                    buffer_size=obstacle_buffer,
                    polygon=create_straight_rectangle(
                        Point(*corner_point1), Point(*corner_point2)
                    ),
                    goto_positions=goto_points,
                )
            )

        for (corner_point1, corner_point2, goto_points) in yellow_reserved_zones_points:
            zones.append(
                YellowReservedZone(
                    logger=yellow_reserved_zone_logger,
                    buffer_size=obstacle_buffer,
                    polygon=create_straight_rectangle(
                        Point(*corner_point1), Point(*corner_point2)
                    ),
                    goto_positions=goto_points,
                )
            )

        for (corner_point1, corner_point2, goto_points) in blue_reserved_zones_points:
            zones.append(
                BlueReservedZone(
                    logger=blue_reserved_zone_logger,
                    buffer_size=obstacle_buffer,
                    polygon=create_straight_rectangle(
                        Point(*corner_point1), Point(*corner_point2)
                    ),
                    goto_positions=goto_points,
                )
            )

        for corner_point in forbidden_zones_points:
            zones.append(
                ForbiddenZone(
                    logger=forbidden_zone_logger,
                    buffer_size=obstacle_buffer,
                    polygon=create_straight_rectangle(
                        Point(*corner_point[0]), Point(*corner_point[1])
                    ),
                )
            )

        # This is the scene for the rockstar
        rockstar_stage = ForbiddenZone(
            logger=forbidden_zone_logger,
            buffer_size=obstacle_buffer,
            polygon=Polygon(
                (
                    (65, 200),
                    (65, 180),
                    (105, 180),
                    (105, 155),
                    (195, 155),
                    (195, 180),
                    (235, 180),
                    (235, 200),
                    (65, 200),
                )
            ),
        )
        zones.append(rockstar_stage)

        if grid_manager_logger:
            super().__init__(
                logger,
                width=300,
                height=200,
                border_buffer=border_buffer,
                obstacle_buffer=obstacle_buffer,
                zones=zones,
                chunk_size=chunk_size,
                forbidden_cover_threshold=forbidden_cover_threshold,
                grid_manager_logger=grid_manager_logger,
            )
        else:
            super().__init__(
                logger,
                width=300,
                height=200,
                border_buffer=border_buffer,
                obstacle_buffer=obstacle_buffer,
                zones=zones,
                chunk_size=chunk_size,
                forbidden_cover_threshold=forbidden_cover_threshold,
            )

        self.logger.log("ShowArena initialized.", LogLevels.INFO)
        self.logger.log(f"Width: {self.width}, Height: {self.height}", LogLevels.DEBUG)
