# ====== Code Summary ======
# This module defines the BaseArenaZone class, which serves as an abstract base class for zones within an arena.
# It includes attributes for zone geometry, type, accessibility, and visit tracking.
# Additionally, it provides methods for checking accessibility, updating zone status, and handling built-in comparisons.
# The AllyZone class extends BaseArenaZone to represent zones dynamically assigned to allies based on their position.

# ====== Imports ======
# Standard library imports
# ...

# Third-party imports
from loggerplusplus import Logger

# Internal project imports
from geometry import (
    Point,
    OrientedPoint,
    create_straight_rectangle
)
from arena.base_arena.arena_zones.structs import ZoneType, ZoneAccessibility
from arena.base_arena.arena_zones.base_arena_zone import BaseArenaZone


# ====== Ally Zone Class ======
class AllyZone(BaseArenaZone):
    """
    Zone designated for allies, dynamically updated based on their position.

    Attributes:
        logger (Logger): Logger instance for logging messages.
        point (OrientedPoint): Position and orientation of the ally.
        accessibility (ZoneAccessibility): Accessibility type of the zone (defaults to free).
        robot_size (float): Size of the robot.
    """

    def __init__(
            self,
            logger: Logger,
            point: OrientedPoint,
            robot_size: float = 2,  # Assume the robot is a square 2/2 = 1 side length
    ) -> None:
        """
        Initializes the AllyZone with position, size, and accessibility.

        Args:
            logger (Logger): Logger instance for logging messages.
            point (OrientedPoint): Position and orientation of the ally.
            robot_size (float, optional): Size of the robot (defaults to 2).
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
            zone_color="#8af542",
        )

    def update(
            self, team_color: str, ally_position: Point | OrientedPoint, enemy_position: Point | OrientedPoint
    ) -> None:
        """
        Update the zone based on the positions of allies and enemies.

        Args:
            team_color (str): Team color.
            ally_position (Point | OrientedPoint): Position of ally.
            enemy_position (Point | OrientedPoint): Position of enemy.
        """
        super().update(team_color, ally_position, enemy_position)
        self.__init__(
            logger=self.logger,
            point=ally_position,
            robot_size=self.robot_size,
        )

    def __eq__(self, other) -> bool:
        """Checks equality based on oriented point geometry."""
        if not isinstance(other, AllyZone):
            return False
        return self.point == other.point

    def __ne__(self, other) -> bool:
        """Checks inequality based on oriented point geometry."""
        return not self.__eq__(other)
