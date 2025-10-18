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
    JengaZone,
    DepositZone,
    YellowReservedZone,
)
from geometry import OrientedPoint, Point, Polygon, create_straight_rectangle

GO_TO_POSITIONS_INDEX = 2


class WinterArena(BaseArena):
    """Arena configuration used to display the competition setup."""
    def __init__(
            self,
            logger: Logger,
            grid_manager_logger: Logger | None,
            border_buffer: float,
            obstacle_buffer: float,
            chunk_size: int = 2,
            forbidden_cover_threshold: float = 0.5,
            distance_to_jenga_zone: float = 69,     # TODO : to adjust according to actual arena setup, 69 is a joke lol
            distance_to_deposit_zone: float = 69,   # TODO : to adjust according to actual arena setup, 69 is a joke lol
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
        jenga_zone_logger = Logger(
            identifier="JengaZone",
            follow_logger_manager_rules=True,
        )
        deposit_zone_logger = Logger(
            identifier="DepositZone",
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

        # TODO : adjust pickup angles, oskour y'a des angles ET en plus Eliott a changé l'orientation !!!
        jenga_zones_points: list[tuple[tuple[float, float], tuple[float, float], list[OrientedPoint | Point]]
        ] = [
            (
                (100, 1300), (250, 1100),
                [
                    OrientedPoint(Point(250, 1200), -pi / 2),
                    OrientedPoint(Point(175, 1300), 0),
                    OrientedPoint(Point(175, 1100), pi),
                ],
            ),
            (
                (500, 100), (300, 250),
                [
                    OrientedPoint(Point(250, 400), -pi / 2),
                    OrientedPoint(Point(175, 500), 0),
                    OrientedPoint(Point(175, 300), pi),
                ],
            ),
            (
                (1000, 250), (1200, 100),
                [
                    OrientedPoint(Point(1100, 250), 0),
                    OrientedPoint(Point(1200, 175), -pi/2),
                    OrientedPoint(Point(1000, 175), 0),
                ],
            ),
            (
                (1050, 875), (1250, 725),
                [
                    OrientedPoint(Point(1050, 800), pi/2),
                    OrientedPoint(Point(1150, 875), 0),
                    OrientedPoint(Point(1150, 725), pi),
                    OrientedPoint(Point(1250, 800), -pi/2),
                ],
            ),
            (
                (2900, 1300), (2750, 1100),
                [
                    OrientedPoint(Point(2750, 1200), -pi / 2),
                    OrientedPoint(Point(2825, 1300), pi),
                    OrientedPoint(Point(2825, 1100), 0),
                ],
            ),
            (
                (2500, 100), (2700, 250),
                [
                    OrientedPoint(Point(2750, 400), -pi / 2),
                    OrientedPoint(Point(2825, 500), pi),
                    OrientedPoint(Point(2825, 300), 0),
                ],
            ),
            (
                (2000, 250), (1800, 100),
                [
                    OrientedPoint(Point(1900, 250), pi),
                    OrientedPoint(Point(1800, 175), -pi / 2),
                    OrientedPoint(Point(2000, 175), pi),
                ],
            ),
            (
                (1950, 875), (1750, 725),
                [
                    OrientedPoint(Point(1950, 800), pi / 2),
                    OrientedPoint(Point(1850, 875), pi),
                    OrientedPoint(Point(1850, 725), 0),
                    OrientedPoint(Point(1750, 800), -pi / 2),
                ],
            )
        ]

        deposit_zones_points: list[tuple[tuple[float, float], tuple[float, float], list[OrientedPoint | Point]]
        ] = [
            (
                (0, 900), (200, 700),
                [
                    OrientedPoint(Point(800, 200), -pi / 2),
                    OrientedPoint(Point(900, 100), 0),
                    OrientedPoint(Point(700, 100), pi),
                ],
            ),
            (
                (600, 200), (800, 0),
                [
                    OrientedPoint(Point(800, 100), -pi / 2),
                    OrientedPoint(Point(700, 200), 0),
                    OrientedPoint(Point(600, 100), pi/2),
                ],
            ),
            (
                (0, 900), (200, 700),
                [
                    OrientedPoint(Point(800, 200), -pi / 2),
                    OrientedPoint(Point(900, 100), 0),
                    OrientedPoint(Point(700, 100), pi),
                ],
            ),
            (
                (1150, 1550), (1350, 1350),
                [
                    OrientedPoint(Point(1150, 1450), pi / 2),
                    OrientedPoint(Point(1350, 1450), -pi / 2),
                    OrientedPoint(Point(1250, 1300), pi),
                ],
            ),
            (
                (700, 900), (900, 700),
                [
                    OrientedPoint(Point(700, 800), pi / 2),
                    OrientedPoint(Point(900, 800), -pi / 2),
                    OrientedPoint(Point(800, 700), pi),
                    OrientedPoint(Point(800, 900), 0),
                ],
            ),
            (
                (3000, 900), (2800, 700),
                [
                    OrientedPoint(Point(2200, 200), -pi / 2),
                    OrientedPoint(Point(2100, 100), pi),
                    OrientedPoint(Point(2300, 100), 0),
                ],
            ),
            (
                (2400, 200), (2200, 0),
                [
                    OrientedPoint(Point(2200, 100), -pi / 2),
                    OrientedPoint(Point(2300, 200), pi),
                    OrientedPoint(Point(2400, 100), pi / 2),
                ],
            ),
            (
                (3000, 900), (2800, 700),
                [
                    OrientedPoint(Point(2200, 200), -pi / 2),
                    OrientedPoint(Point(2100, 100), pi),
                    OrientedPoint(Point(2300, 100), 0),
                ],
            ),
            (
                (1850, 1550), (1650, 1350),
                [
                    OrientedPoint(Point(1850, 1450), pi / 2),
                    OrientedPoint(Point(1650, 1450), -pi / 2),
                    OrientedPoint(Point(1750, 1300), 0),
                ],
            ),
            (
                (2300, 900), (2100, 700),
                [
                    OrientedPoint(Point(2300, 800), pi / 2),
                    OrientedPoint(Point(2100, 800), -pi / 2),
                    OrientedPoint(Point(2200, 700), 0),
                    OrientedPoint(Point(2200, 900), pi),
                ],
            ),
            (
                (1400, 900), (1600, 700),
                [
                    OrientedPoint(Point(1400, 800), pi / 2),
                    OrientedPoint(Point(1600, 800), -pi / 2),
                    OrientedPoint(Point(1500, 700), pi),
                    OrientedPoint(Point(1500, 900), 0),
                ],
            ),
            (
                (1400, 200), (1600, 0),
                [
                    OrientedPoint(Point(1600, 100), -pi / 2),
                    OrientedPoint(Point(1500, 200), pi),
                    OrientedPoint(Point(1400, 100), pi / 2),
                ],
            ),
        ]

        yellow_reserved_zones_points: list[
            tuple[tuple[float, float], tuple[float, float]]
        ] = [
            (
                (0, 2000), (600, 1550),
            ),
        ]

        blue_reserved_zones_points: list[
            tuple[tuple[float, float], tuple[float, float]]
        ] = [
            (
                (2400, 2000), (3000, 1550),
            ),
        ]

        forbidden_zones_points: list[
            tuple[tuple[float, float], tuple[float, float]]
        ] = []

        zones: list[BaseArenaZone] = []

        zones.extend(
            JengaZone(
                logger=jenga_zone_logger,
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
            for corner_point in jenga_zones_points
        )

        zones.extend(
            DepositZone(
                logger=deposit_zone_logger,
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
            for corner_point in deposit_zones_points
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

        # This is the scene for the ninjas
        ninja_stage = ForbiddenZone(
            logger=forbidden_zone_logger,
            buffer_size=obstacle_buffer,
            polygon=Polygon(
                (
                    (625, 2000),
                    (2375, 1600),
                ),
            ),
        )

        zones.extend([ninja_stage])

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

        self.logger.info("WinterArena initialized.")
        self.logger.debug(f"Width: {self.width}, Height: {self.height}")

    @override
    def __eq__(self, other: object) -> bool:
        """Checks equality between two ShowArena instances.

        Args:
            other (object): The other instance to compare against.

        Returns:
            bool: ``True`` if the instances are equal, ``False`` otherwise.
        """
        if not isinstance(other, WinterArena):
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
