"""Demo arena with predefined zones for visualization and testing."""

from __future__ import annotations

from math import pi
from typing import TYPE_CHECKING, override

from arena.base_arena.arena import BaseArena
from arena.base_arena.arena_zones import (
    BaseArenaZone,
    BlueReservedZone,
    DropZone,
    ForbiddenZone,
    StuffZone,
    YellowReservedZone,
)
from geometry import OrientedPoint, Point, Polygon, create_straight_rectangle
from log_manager import LogLogger

if TYPE_CHECKING:
    from loggerplusplus import Logger

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
        distance_to_jenga_zone: float = 10,  # TODO : to adjust
        distance_to_drop_zone: float = 10,  # TODO : to adjust
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
        jenga_zone_logger = LogLogger(
            identifier="JengaZone",
            follow_logger_manager_rules=True,
        )
        drop_zone_logger = LogLogger(
            identifier="DropZone",
            follow_logger_manager_rules=True,
        )

        yellow_reserved_zone_logger = LogLogger(
            identifier="YellowReservedZone",
            follow_logger_manager_rules=True,
        )

        blue_reserved_zone_logger = LogLogger(
            identifier="BlueReservedZone",
            follow_logger_manager_rules=True,
        )

        ninja_stage_zone_logger = LogLogger(
            identifier="NinjaStageZone",
            follow_logger_manager_rules=True,
        )

        jenga_zones_points: list[
            tuple[tuple[float, float], tuple[float, float], list[OrientedPoint]]
        ] = [
            (
                (10, 130),
                (25, 110),
                [
                    OrientedPoint(25 + distance_to_jenga_zone, 120, pi),
                ],
            ),
            (
                (10, 50),
                (25, 30),
                [
                    OrientedPoint(25 + distance_to_jenga_zone, 40, pi),
                ],
            ),
            (
                (100, 25),
                (120, 10),
                [
                    OrientedPoint(110, 25 + distance_to_jenga_zone, -pi / 2),
                ],
            ),
            (
                (105, 87.5),
                (125, 72.5),
                [
                    OrientedPoint(115, 87.5 + distance_to_jenga_zone, -pi / 2),
                    OrientedPoint(115, 72.5 - distance_to_jenga_zone, pi / 2),
                ],
            ),
            (
                (290, 130),
                (275, 110),
                [
                    OrientedPoint(275 - distance_to_jenga_zone, 120, 0),
                ],
            ),
            (
                (275, 50),
                (290, 30),
                [
                    OrientedPoint(275 - distance_to_jenga_zone, 40, 0),
                ],
            ),
            (
                (200, 25),
                (180, 10),
                [
                    OrientedPoint(190, 25 + distance_to_jenga_zone, -pi / 2),
                ],
            ),
            (
                (195, 87.5),
                (175, 72.5),
                [
                    OrientedPoint(185, 87.5 + distance_to_jenga_zone, -pi / 2),
                    OrientedPoint(185, 72.5 - distance_to_jenga_zone, pi / 2),
                ],
            ),
        ]

        drop_zones_points: list[
            tuple[tuple[float, float], tuple[float, float], list[OrientedPoint]]
        ] = [
            (
                (0, 70),
                (20, 90),
                [
                    OrientedPoint(20 + distance_to_drop_zone, 80, pi),
                ],
            ),
            (
                (60, 20),
                (80, 0),
                [
                    OrientedPoint(70, 20 + distance_to_drop_zone, -pi / 2),
                ],
            ),
            (
                (115, 155),
                (135, 135),
                [
                    OrientedPoint(125, 135 - distance_to_drop_zone, pi / 2),
                ],
            ),
            (
                (70, 90),
                (90, 70),
                [
                    OrientedPoint(80, 70 - distance_to_drop_zone, pi / 2),
                    OrientedPoint(80, 90 + distance_to_drop_zone, -pi / 2),
                ],
            ),
            (
                (300, 90),
                (280, 70),
                [
                    OrientedPoint(280 - distance_to_drop_zone, 80, 0),
                ],
            ),
            (
                (240, 20),
                (220, 0),
                [
                    OrientedPoint(230, 20 + distance_to_drop_zone, -pi / 2),
                ],
            ),
            (
                (185, 155),
                (165, 135),
                [
                    OrientedPoint(175, 135 - distance_to_drop_zone, pi / 2),
                ],
            ),
            (
                (230, 90),
                (210, 70),
                [
                    OrientedPoint(220, 70 - distance_to_drop_zone, pi / 2),
                    OrientedPoint(220, 90 + distance_to_drop_zone, -pi / 2),
                ],
            ),
            (
                (140, 90),
                (160, 70),
                [
                    OrientedPoint(150, 70 - distance_to_drop_zone, pi / 2),
                    OrientedPoint(150, 90 + distance_to_drop_zone, -pi / 2),
                ],
            ),
            (
                (140, 20),
                (160, 0),
                [
                    OrientedPoint(150, 20 + distance_to_drop_zone, -pi / 2),
                ],
            ),
        ]

        yellow_backstage_zone = YellowReservedZone(
            logger=yellow_reserved_zone_logger,
            buffer_size=obstacle_buffer,
            polygon=create_straight_rectangle(
                Point(0, 200),
                Point(60, 155),
            ),
            go_to_positions=[OrientedPoint(25, 177.5, pi / 2)],
        )

        blue_backstage_zone = BlueReservedZone(
            logger=blue_reserved_zone_logger,
            buffer_size=obstacle_buffer,
            polygon=create_straight_rectangle(
                Point(240, 200),
                Point(300, 155),
            ),
            go_to_positions=[OrientedPoint(275, 177.5, pi / 2)],
        )

        ninja_stage = ForbiddenZone(
            logger=ninja_stage_zone_logger,
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

        zones: list[BaseArenaZone] = []

        zones.extend([yellow_backstage_zone, blue_backstage_zone, ninja_stage])

        zones.extend(
            StuffZone(
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

        self._logger.info("[ARENA:Winter] Initialized")
        self._logger.debug(f"[ARENA:Winter] Dimensions: {self.width}x{self.height}")

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
