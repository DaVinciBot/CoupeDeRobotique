"""Demo arena with predefined zones for visualization and testing."""

from __future__ import annotations

from math import pi
from typing import override

from loggerplusplus import Logger

from arena.base_arena.arena import BaseArena
from arena.base_arena.arena_zones import (
    BaseArenaZone,
    BlueReservedZone,
    ForbiddenZone,
    StuffZone,
    YellowReservedZone,
)
from geometry import OrientedPoint, Point, Polygon, create_straight_rectangle

GO_TO_POSITIONS_INDEX = 2


class ShowArena(BaseArena):
    """Arena configuration used to display the competition setup."""

    def __init__(
        self,
        logger: Logger,
        grid_manager_logger: Logger | None,
        border_buffer: float,
        obstacle_buffer: float,
        chunk_size: int = 2,
        forbidden_cover_threshold: float = 0.5,
        distance_between_robot_and_pickup_zone: float = 25,
        distance_between_robot_and_big_construct_zone: float = 0,
        distance_between_robot_and_small_construct_zone: float = 22,
    ) -> None:
        """Initialize the arena with fixed zones.

        Args:
            logger (Logger): Logger used for zone loggers.
            grid_manager_logger (Logger | None): Logger for the grid manager.
            border_buffer (float): Arena border safety buffer.
            obstacle_buffer (float): Margin around obstacles.
            chunk_size (int): Size of grid chunks in centimeters.
            forbidden_cover_threshold (float):
                Coverage ratio to mark cells forbidden.
            distance_between_robot_and_pickup_zone (float):
                Offset for pickup zones.
            distance_between_robot_and_big_construct_zone (float):
                Offset for big constructs.
            distance_between_robot_and_small_construct_zone (float):
                Offset for small constructs.
        """
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
        stuff_zones_points: list[
            tuple[tuple[float, float], tuple[float, float], list[OrientedPoint | Point]]
        ] = [
            (
                (2.5, 20),
                (12.5, 60),
                [OrientedPoint(12.5 + distance_between_robot_and_pickup_zone, 40, pi)],
            ),
            (
                (2.5, 112.5),
                (12.5, 152.5),
                [
                    OrientedPoint(
                        12.5 + distance_between_robot_and_pickup_zone,
                        132.5,
                        pi,
                    ),
                ],
            ),
            (
                (57.5, 20),
                (97.5, 30),
                [
                    OrientedPoint(
                        77.5,
                        30 + distance_between_robot_and_pickup_zone,
                        -pi / 2,
                    ),
                ],
            ),
            (
                (62.5, 167.5),
                (102.5, 177.5),
                [
                    OrientedPoint(
                        82.5,
                        167.5 - distance_between_robot_and_pickup_zone,
                        pi / 2,
                    ),
                ],
            ),
            (
                (90, 90),
                (130, 100),
                [
                    OrientedPoint(
                        110,
                        90 - distance_between_robot_and_pickup_zone,
                        pi / 2,
                    ),
                    OrientedPoint(
                        110,
                        100 + distance_between_robot_and_pickup_zone,
                        -pi / 2,
                    ),
                ],
            ),
            (
                (300 - 12.5, 20),
                (300 - 2.5, 60),
                [
                    OrientedPoint(
                        300 - 12.5 - distance_between_robot_and_pickup_zone,
                        40,
                        0,
                    ),
                ],
            ),
            (
                (300 - 12.5, 112.5),
                (300 - 2.5, 152.5),
                [
                    OrientedPoint(
                        300 - 12.5 - distance_between_robot_and_pickup_zone,
                        132.5,
                        0,
                    ),
                ],
            ),
            (
                (300 - 97.5, 20),
                (300 - 57.5, 30),
                [
                    OrientedPoint(
                        300 - 77.5,
                        30 + distance_between_robot_and_pickup_zone,
                        -pi / 2,
                    ),
                ],
            ),
            (
                (300 - 102.5, 167.5),
                (300 - 62.5, 177.5),
                [
                    OrientedPoint(
                        300 - 82.5,
                        167.5 - distance_between_robot_and_pickup_zone,
                        pi / 2,
                    ),
                ],
            ),
            (
                (300 - 130, 90),
                (300 - 90, 100),
                [
                    OrientedPoint(
                        300 - 110,
                        90 - distance_between_robot_and_pickup_zone,
                        pi / 2,
                    ),
                    OrientedPoint(
                        300 - 110,
                        100 + distance_between_robot_and_pickup_zone,
                        -pi / 2,
                    ),
                ],
            ),
        ]

        yellow_reserved_zones_points: list[
            tuple[tuple[float, float], tuple[float, float], list[OrientedPoint | Point]]
        ] = [
            (
                (0, 0),
                (45, 15),
                [
                    OrientedPoint(
                        22.5,
                        15 + distance_between_robot_and_small_construct_zone,
                        -pi / 2,
                    ),
                ],
            ),
            (
                (0, 65),
                (45, 110),
                [
                    OrientedPoint(
                        22.5,
                        65 - distance_between_robot_and_big_construct_zone,
                        pi / 2,
                    ),
                    OrientedPoint(
                        22.5,
                        110 + distance_between_robot_and_big_construct_zone,
                        -pi / 2,
                    ),
                    OrientedPoint(
                        45 + distance_between_robot_and_big_construct_zone,
                        87.5,
                        pi,
                    ),
                ],
            ),
            (
                (155, 0),
                (200, 45),
                [
                    OrientedPoint(
                        177.5,
                        45 + distance_between_robot_and_big_construct_zone,
                        -pi / 2,
                    ),
                    # OrientedPoint(200 + distance_between_robot_and_work_zone,
                    #               22.5, pi),
                ],
            ),
            (
                (200, 0),
                (245, 15),
                [
                    OrientedPoint(
                        222.5,
                        15 + distance_between_robot_and_small_construct_zone,
                        -pi / 2,
                    ),
                ],
            ),
        ]

        blue_reserved_zones_points: list[
            tuple[tuple[float, float], tuple[float, float], list[OrientedPoint | Point]]
        ] = [
            (
                (255, 0),
                (300, 15),
                [
                    OrientedPoint(
                        277.5,
                        15 + distance_between_robot_and_small_construct_zone,
                        -pi / 2,
                    ),
                ],
            ),
            (
                (255, 65),
                (300, 110),
                [
                    OrientedPoint(
                        277.5,
                        65 - distance_between_robot_and_big_construct_zone,
                        pi / 2,
                    ),
                    OrientedPoint(
                        277.5,
                        110 + distance_between_robot_and_big_construct_zone,
                        -pi / 2,
                    ),
                    OrientedPoint(
                        255 - distance_between_robot_and_big_construct_zone,
                        87.5,
                        0,
                    ),
                ],
            ),
            (
                (100, 0),
                (145, 45),
                [
                    OrientedPoint(
                        122.5,
                        45 + distance_between_robot_and_big_construct_zone,
                        -pi / 2,
                    ),
                ],
            ),
            (
                (55, 0),
                (100, 15),
                [
                    OrientedPoint(
                        77.5,
                        15 + distance_between_robot_and_small_construct_zone,
                        -pi / 2,
                    ),
                ],
            ),
        ]

        forbidden_zones_points: list[
            tuple[tuple[float, float], tuple[float, float]]
        ] = []

        zones: list[BaseArenaZone] = []

        zones.extend(
            StuffZone(
                logger=stuff_zone_logger,
                buffer_size=obstacle_buffer,
                polygon=create_straight_rectangle(
                    Point(*corner_point[0]),
                    Point(*corner_point[1]),
                ),
                go_to_positions=(
                    corner_point[GO_TO_POSITIONS_INDEX]
                    if len(corner_point) > GO_TO_POSITIONS_INDEX
                    else None
                ),
            )
            for corner_point in stuff_zones_points
        )

        zones.extend(
            YellowReservedZone(
                logger=yellow_reserved_zone_logger,
                buffer_size=obstacle_buffer,
                polygon=create_straight_rectangle(
                    Point(*corner_point[0]),
                    Point(*corner_point[1]),
                ),
                go_to_positions=(
                    corner_point[GO_TO_POSITIONS_INDEX]
                    if len(corner_point) > GO_TO_POSITIONS_INDEX
                    else None
                ),
            )
            for corner_point in yellow_reserved_zones_points
        )

        zones.extend(
            BlueReservedZone(
                logger=blue_reserved_zone_logger,
                buffer_size=obstacle_buffer,
                polygon=create_straight_rectangle(
                    Point(*corner_point[0]),
                    Point(*corner_point[1]),
                ),
                go_to_positions=(
                    corner_point[GO_TO_POSITIONS_INDEX]
                    if len(corner_point) > GO_TO_POSITIONS_INDEX
                    else None
                ),
            )
            for corner_point in blue_reserved_zones_points
        )

        zones.extend(
            ForbiddenZone(
                logger=forbidden_zone_logger,
                buffer_size=obstacle_buffer,
                polygon=create_straight_rectangle(
                    Point(*corner_point[0]),
                    Point(*corner_point[1]),
                ),
            )
            for corner_point in forbidden_zones_points
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
                ),
            ),
        )

        zones.extend(
            (
                rockstar_stage,
                BlueReservedZone(
                    logger=blue_reserved_zone_logger,
                    buffer_size=obstacle_buffer,
                    polygon=create_straight_rectangle(
                        Point((15, 155)),
                        Point((60, 200)),
                    ),
                    go_to_positions=[OrientedPoint(37.5, 150.5, pi / 2)],
                ),
                YellowReservedZone(
                    logger=yellow_reserved_zone_logger,
                    buffer_size=obstacle_buffer,
                    polygon=create_straight_rectangle(
                        Point((285, 155)),
                        Point((240, 200)),
                    ),
                    go_to_positions=[OrientedPoint(262.5, 150.5, pi / 2)],
                ),
            ),
        )

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

        self.logger.info("ShowArena initialized.")
        self.logger.debug(f"Width: {self.width}, Height: {self.height}")

    @override
    def __eq__(self, other: object) -> bool:
        """Checks equality between two ShowArena instances.

        Args:
            other (object): The other instance to compare against.

        Returns:
            bool: ``True`` if the instances are equal, ``False`` otherwise.
        """
        if not isinstance(other, ShowArena):
            return False

        return (
            self.ally_zone == other.ally_zone
            and self.enemy_zone == other.enemy_zone
            and self.grid_manager == other.grid_manager
        )

    @override
    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)

    @override
    def __hash__(self) -> int:
        return hash(
            (
                self.ally_zone,
                self.enemy_zone,
                self.grid_manager,
            ),
        )
