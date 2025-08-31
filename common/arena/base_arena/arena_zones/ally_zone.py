"""Dynamic zone representing the ally robot.

The :class:`AllyZone` is recalculated based on the ally position and is used to
track its current location within the arena.

"""

from __future__ import annotations

from typing import TYPE_CHECKING, override

from arena.base_arena.arena_zones.base_arena_zone import BaseArenaZone
from arena.base_arena.arena_zones.structs import ZoneAccessibility, ZoneType
from geometry import OrientedPoint, Point, create_straight_rectangle

if TYPE_CHECKING:
    from loggerplusplus import Logger

    from arena.base_arena.team_color import TeamColor


class AllyZone(BaseArenaZone):
    """Zone designated for allies, dynamically updated based on their position."""

    def __init__(
        self,
        logger: Logger,
        point: OrientedPoint,
        robot_size: float = 2,  # Assume the robot is a square 2/2 = 1 side length
    ) -> None:
        """Initializes the AllyZone with position, size, and accessibility.

        Args:
            logger (Logger): Logger instance for logging messages.
            point (OrientedPoint): Position and orientation of the ally.
            robot_size (float, optional): Size of the robot. Defaults to 2.

        """
        position_based_polygon = create_straight_rectangle(
            Point(point.x - robot_size, point.y - robot_size),
            Point(point.x + robot_size, point.y + robot_size),
        )

        self.point: OrientedPoint = point
        self.robot_size: float = robot_size
        super().__init__(
            logger=logger,
            zone_type=ZoneType.ALLY,
            accessibility=ZoneAccessibility.FREE,
            buffer_size=0.0,
            polygon=position_based_polygon,
            buffered_polygon=None,
            update_callback=None,
            zone_color="#2ea100",
        )

    @override
    def update(
        self,
        team_color: TeamColor,
        ally_position: Point | OrientedPoint,
        enemy_position: Point | OrientedPoint,
    ) -> None:
        """Update the zone based on the positions of allies and enemies.

        Args:
            team_color (TeamColor, optional): The color of the team.
            ally_position (Point | OrientedPoint): Position of ally.
            enemy_position (Point | OrientedPoint): Position of enemy.

        """
        super().update(team_color, ally_position, enemy_position)
        self.__init__(
            logger=self.logger,
            point=(
                ally_position
                if isinstance(ally_position, OrientedPoint)
                else OrientedPoint.from_point(ally_position)
            ),
            robot_size=self.robot_size,
        )

    @override
    def __eq__(self, other: object) -> bool:
        """Return ``True`` if zones represent the same oriented point.

        Args:
            other (object): Object to compare against.

        Returns:
            bool: ``True`` if ``other`` is an :class:``AllyZone`` with the same
            point.

        """
        if not isinstance(other, AllyZone):
            return False
        return self.point == other.point

    @override
    def __ne__(self, other: object) -> bool:
        """Return ``True`` if zones do not represent the same oriented point.

        Args:
            other (object): Object to compare against.

        Returns:
            bool: ``True`` if ``other`` is not an equal :class:``AllyZone``.

        """
        return not self.__eq__(other)

    @override
    def __hash__(self) -> int:
        """Return a hash based on the zone's position and size.

        Returns:
            int: Hash of the ally zone.

        """
        return hash((self.point.x, self.point.y, self.point.theta, self.robot_size))
