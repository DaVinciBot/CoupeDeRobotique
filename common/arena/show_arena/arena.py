# ====== Imports ======
# Internal project imports
from loggerplusplus import Logger

from arena.base_arena.arena import BaseArena
from arena.base_arena.arena_zone import (
    BaseArenaZone,
    ForbiddenZone,
    StuffZone,
    BlueReservedZone,
    YellowReservedZone,
)

from geometry import (
    Point,
    Polygon,
    create_straight_rectangle,
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
            follow_logger_manager_rules=True,
        )

        yellow_reserved_zone_logger = Logger(
            identifier="YellowReservedZone",
            follow_logger_manager_rules=True,
        )

        blue_reserved_zone_logger = Logger(
            identifier="BlueReservedZone",
            follow_logger_manager_rules=True,
        )

        forbidden_zone_logger = Logger(
            identifier="ForbiddenZone",
            follow_logger_manager_rules=True,
        )

        stuff_zones_points = [
            ((2.5, 20), (12.5, 60)),
            ((2.5, 112.5), (12.5, 152.5)),
            ((57.5, 20), (97.5, 30)),
            ((62.5, 167.5), (102.5, 177.5)),
            ((90, 90), (130, 100)),
            ((300 - 12.5, 20), (300 - 2.5, 60)),
            ((300 - 12.5, 112.5), (300 - 2.5, 152.5)),
            ((300 - 97.5, 20), (300 - 57.5, 30)),
            ((300 - 102.5, 167.5), (300 - 62.5, 177.5)),
            ((300 - 130, 90), (300 - 90, 100)),
        ]

        yellow_reserved_zones_points = [
            ((0, 0), (45, 15)),
            ((0, 65), (45, 110)),
            ((155, 0), (200, 45)),
            ((200, 0), (245, 15)),
        ]

        blue_reserved_zones_points = [
            ((255, 0), (300, 15)),
            ((255, 65), (300, 110)),
            ((55, 0), (100, 15)),
            ((100, 0), (145, 45)),
        ]

        forbidden_zones_points = []

        zones: list[BaseArenaZone] = []

        for corner_point in stuff_zones_points:
            zones.append(
                StuffZone(
                    logger=stuff_zone_logger,
                    buffer_size=obstacle_buffer,
                    polygon=create_straight_rectangle(
                        Point(*corner_point[0]), Point(*corner_point[1])
                    ),
                )
            )

        for corner_point in yellow_reserved_zones_points:
            zones.append(
                YellowReservedZone(
                    logger=yellow_reserved_zone_logger,
                    buffer_size=obstacle_buffer,
                    polygon=create_straight_rectangle(
                        Point(*corner_point[0]), Point(*corner_point[1])
                    ),
                )
            )

        for corner_point in blue_reserved_zones_points:
            zones.append(
                BlueReservedZone(
                    logger=blue_reserved_zone_logger,
                    buffer_size=obstacle_buffer,
                    polygon=create_straight_rectangle(
                        Point(*corner_point[0]), Point(*corner_point[1])
                    ),
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

        self.logger.info("ShowArena initialized.")
        self.logger.debug(f"Width: {self.width}, Height: {self.height}")
