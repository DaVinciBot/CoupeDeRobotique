"""Demo arena with predefined zones for visualization and testing."""

from __future__ import annotations

from math import pi
from typing import override

from loggerplusplus import Logger

from arena.base_arena.arena import BaseArena
from arena.base_arena.arena_zones import (
    BaseArenaZone,
    BlueReservedZone,
    DropZone,
    ForbiddenZone,
    JengaZone,
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
        distance_to_jenga_zone: float = 69,  # TODO : to adjust according to actual arena setup, 69 is a joke lol
        distance_to_drop_zone: float = 69,  # TODO : to adjust according to actual arena setup, 69 is a joke lol
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
            distance_to_jenga_zone (float):
                Distance to maintain from Jenga zones.
            distance_to_drop_zone (float):
                Distance to maintain from Deposit zones.
        """
        jenga_zone_logger = Logger(
            identifier="JengaZone",
            follow_logger_manager_rules=True,
        )
        drop_zone_logger = Logger(
            identifier="DropZone",
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
        jenga_zones_points: list[
            tuple[tuple[float, float], tuple[float, float], list[OrientedPoint | Point]]
        ] = [
            (
                (10, 130),
                (25, 110),
                [
                    OrientedPoint(25, 120, pi),
                    OrientedPoint(17.5, 130, -pi / 2),
                    OrientedPoint(17.5, 110, pi / 2),
                ],
            ),
            (
                (10, 50),
                (25, 30),
                [
                    OrientedPoint(25, 40, pi),
                    OrientedPoint(17.5, 50, -pi / 2),
                    OrientedPoint(17.5, 30, pi / 2),
                ],
            ),
            (
                (100, 25),
                (120, 10),
                [
                    OrientedPoint(110, 25, -pi / 2),
                    OrientedPoint(120, 17.5, pi),
                    OrientedPoint(100, 17.5, 0),
                ],
            ),
            (
                (105, 87.5),
                (125, 72.5),
                [
                    OrientedPoint(105, 80, 0),
                    OrientedPoint(115, 87.5, -pi / 2),
                    OrientedPoint(115, 72.5, pi / 2),
                    OrientedPoint(125, 80, pi),
                ],
            ),
            (
                (290, 130),
                (275, 110),
                [
                    OrientedPoint(275, 120, 0),
                    OrientedPoint(282.5, 130, -pi / 2),
                    OrientedPoint(282.5, 110, pi / 2),
                ],
            ),
            (
                (275, 50),
                (290, 30),
                [
                    OrientedPoint(275, 40, 0),
                    OrientedPoint(282.5, 50, -pi / 2),
                    OrientedPoint(282.5, 30, pi / 2),
                ],
            ),
            (
                (200, 25),
                (180, 10),
                [
                    OrientedPoint(190, 25, -pi / 2),
                    OrientedPoint(180, 17.5, 0),
                    OrientedPoint(200, 17.5, pi),
                ],
            ),
            (
                (195, 87.5),
                (175, 72.5),
                [
                    OrientedPoint(195, 80, pi),
                    OrientedPoint(185, 87.5, -pi / 2),
                    OrientedPoint(185, 72.5, pi / 2),
                    OrientedPoint(175, 80, 0),
                ],
            ),
        ]

        drop_zones_points: list[
            tuple[tuple[float, float], tuple[float, float], list[OrientedPoint | Point]]
        ] = [
            (
                (0, 90),
                (20, 70),
                [
                    OrientedPoint(20, 80, pi),
                    OrientedPoint(10, 90, -pi / 2),
                    OrientedPoint(10, 70, pi / 2),
                ],
            ),
            (
                (60, 20),
                (80, 0),
                [
                    OrientedPoint(80, 10, pi),
                    OrientedPoint(70, 20, -pi / 2),
                    OrientedPoint(60, 10, 0),
                ],
            ),
            (
                (115, 155),
                (135, 135),
                [
                    OrientedPoint(115, 145, 0),
                    OrientedPoint(135, 145, pi),
                    OrientedPoint(125, 135, pi / 2),
                ],
            ),
            (
                (70, 90),
                (90, 70),
                [
                    OrientedPoint(70, 80, 0),
                    OrientedPoint(90, 80, pi),
                    OrientedPoint(80, 70, pi / 2),
                    OrientedPoint(80, 90, -pi / 2),
                ],
            ),
            (
                (300, 90),
                (280, 70),
                [
                    OrientedPoint(290, 70, pi / 2),
                    OrientedPoint(290, 90, -pi / 2),
                    OrientedPoint(280, 80, 0),
                ],
            ),
            (
                (240, 20),
                (220, 0),
                [
                    OrientedPoint(220, 10, 0),
                    OrientedPoint(230, 20, -pi / 2),
                    OrientedPoint(240, 10, pi),
                ],
            ),
            (
                (185, 155),
                (165, 135),
                [
                    OrientedPoint(185, 145, pi),
                    OrientedPoint(165, 145, 0),
                    OrientedPoint(175, 135, pi / 2),
                ],
            ),
            (
                (230, 90),
                (210, 70),
                [
                    OrientedPoint(230, 80, pi),
                    OrientedPoint(210, 80, 0),
                    OrientedPoint(220, 70, pi / 2),
                    OrientedPoint(220, 90, -pi / 2),
                ],
            ),
            (
                (140, 90),
                (160, 70),
                [
                    OrientedPoint(140, 80, 0),
                    OrientedPoint(160, 80, pi),
                    OrientedPoint(150, 70, pi / 2),
                    OrientedPoint(150, 90, -pi / 2),
                ],
            ),
            (
                (140, 20),
                (160, 0),
                [
                    OrientedPoint(160, 10, pi),
                    OrientedPoint(150, 20, -pi / 2),
                    OrientedPoint(140, 10, 0),
                ],
            ),
        ]

        yellow_reserved_zones_points: list[
            tuple[tuple[float, float], tuple[float, float]]
        ] = [
            (
                (0, 200),
                (60, 155),
            ),
        ]

        blue_reserved_zones_points: list[
            tuple[tuple[float, float], tuple[float, float]]
        ] = [
            (
                (240, 200),
                (300, 155),
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
            DropZone(
                logger=drop_zone_logger,
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
            for corner_point in drop_zones_points
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
                    (60, 200),
                    (240, 200),
                    (240, 165),
                    (60, 165),
                    (60, 200),
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
