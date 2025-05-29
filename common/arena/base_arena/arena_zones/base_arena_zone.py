# ====== Code Summary ======
# This module defines the BaseArenaZone class, which serves as an abstract base class for zones within an arena.
# It includes attributes for zone geometry, type, accessibility, and visit tracking.
# Additionally, it provides methods for checking accessibility, updating zone status, and handling built-in comparisons.

# ====== Imports ======
# Standard library imports
from abc import ABC

# Third-party imports
from loggerplusplus import Logger

# Local imports
from utils import Utils
from geometry import Polygon, BufferCapStyle, BufferJoinStyle, Point, OrientedPoint

# Internal project imports
from arena.base_arena.arena_zones.structs import ZoneType, ZoneAccessibility
from arena.base_arena.team_color import TeamColor


# ====== Base Zone Class ======
class BaseArenaZone(ABC):
    """
    Represents a zone within an arena with attributes for geometry, type, color, and navigability.

    Attributes:
        polygon (Polygon): The geometric shape of the zone.
        zone_type (ZoneType): The type/category of the zone.
        accessibility (ZoneAccessibility): The navigability of the zone.
        zone_color (str): The color representation of the zone.
        enemy_visits (int): Count of opponent visits.
        ally_visits (int): Count of self visits.
    """

    zones_uid: list[int] = []

    def __init__(
        self,
        logger: Logger,
        zone_type: ZoneType,
        accessibility: ZoneAccessibility,
        buffer_size: float = 0.0,
        polygon: Polygon = None,
        buffered_polygon: Polygon = None,
        update_callback: callable = None,
        zone_color: str = "#9e9e9e",
        go_to_positions: list[OrientedPoint | Point] = None,
        uid: int = None,
    ) -> None:
        """
        Initializes the BaseArenaZone with geometry, type, color, and accessibility.

        Args:
            logger (Logger): Logger instance for logging messages.
            zone_type (ZoneType): The type/category of the zone.
            accessibility (ZoneAccessibility): Accessibility of the zone.
            buffer_size (float): Buffer size for geometric adjustments.
            polygon (Polygon, optional): Polygon representing the zone geometry.
            buffered_polygon (Polygon, optional): Buffered polygon geometry.
            update_callback (callable, optional): Function to be called on updates.
            zone_color (str): Color associated with the zone.
            go_to_positions (list[OrientedPoint | Point], optional): List of go-to positions within the zone.
        """
        self.logger: Logger = logger
        self.zone_type: ZoneType = zone_type
        self.accessibility: ZoneAccessibility = accessibility

        if polygon is None and buffered_polygon is None:
            self.logger.error("No polygon provided for zone")
        elif polygon is not None and buffered_polygon is None:
            buffered_polygon = self.add_buffer_to_zone(polygon, buffer_size)
        elif polygon is None and buffered_polygon is not None:
            polygon = self.add_buffer_to_zone(buffered_polygon, -buffer_size)

        self.buffer_size: float = buffer_size
        self.polygon: Polygon = polygon
        self.buffered_polygon: Polygon = buffered_polygon

        self.update_callback = update_callback
        self.go_to_positions = go_to_positions

        self.zone_color: str = zone_color
        self.enemy_visits: int = 0
        self.ally_visits: int = 0
        self.last_update_time: float = 0.0

        self.uid = BaseArenaZone.get_new_uid(uid)

    @classmethod
    def get_new_uid(cls, input_uid: None | int) -> int:
        if input_uid is not None:
            cls.zones_uid.append(input_uid)
            return input_uid

        if cls.zones_uid:
            cls.zones_uid.append(cls.zones_uid[-1] + 1)
        else:
            cls.zones_uid.append(0)
        return cls.zones_uid[-1]

    @staticmethod
    def add_buffer_to_zone(polygon: Polygon, buffer: float) -> Polygon:
        """
        Adds a buffer around a zone to account for obstacle or border spacing.
        The buffer uses a square cap style to match the grid structure.

        Args:
            polygon (Polygon): The polygon to buffer.
            buffer (float): The buffer size to apply.

        Returns:
            Polygon: The buffered polygon.
        """
        return polygon.buffer(
            buffer, cap_style=BufferCapStyle.flat, join_style=BufferJoinStyle.mitre
        )

    """ Accessibility methods """

    def is_accessible(self, team_color: TeamColor = TeamColor.UNDEFINED) -> bool:
        """
        Determines if the zone is accessible for a given team color.

        Args:
            team_color (TeamColor, optional): The color of the team.

        Returns:
            bool: True if accessible, False otherwise.
        """
        return self.accessibility not in [
            ZoneAccessibility.FORBIDDEN,
            ZoneAccessibility.RESTRICTED,
        ]

    def is_accessible_for_emergency(
        self, team_color: TeamColor = TeamColor.UNDEFINED
    ) -> bool:
        """
        Determines if the zone is accessible in an emergency.

        Args:
            team_color (TeamColor, optional): The color of the team.

        Returns:
            bool: True if accessible in emergencies, False otherwise.
        """
        return self.accessibility != ZoneAccessibility.FORBIDDEN

    def get_go_to_position(
        self, ally_position: OrientedPoint, team_color: TeamColor
    ) -> OrientedPoint | None:
        """
        Determines the best go-to position for an ally in the given zone.

        Args:
            ally_position (OrientedPoint): The position of the ally.
            team_color (TeamColor): The color of the team.

        Returns:
            OrientedPoint | None: The best go-to position, or None if the zone is not accessible.
        """
        if not self.is_accessible(team_color):
            self.logger.debug(
                f"GoTo position request: Zone {self.zone_type} is not accessible."
            )
            return None

        # If no specific go-to positions are defined, return the centroid of the zone
        if not self.go_to_positions:
            self.logger.debug(
                f"GoTo position request: No defined go-to positions for zone {self.zone_type}, "
                f"returning centroid [{self.polygon.centroid}]"
            )
            return self.polygon.centroid

        # Find the nearest go-to position to the ally
        nearest_position = min(
            self.go_to_positions, key=lambda p: ally_position.distance(p)
        )
        self.logger.debug(
            f"GoTo position request: Nearest go-to position to ally [{ally_position}] is [{nearest_position}]"
        )
        return nearest_position

    """ Update methods """

    def update(
        self,
        team_color: TeamColor,
        ally_position: Point | OrientedPoint,
        enemy_position: Point | OrientedPoint,
    ) -> None:
        """
        Update the zone based on the positions of allies and enemies.

        Args:
            team_color (TeamColor): The color of the team.
            ally_position (Point | OrientedPoint): Position of ally.
            enemy_position (Point | OrientedPoint): Position of enemy.
        """

        # Update visit counts
        # if self.polygon.contains(enemy_position):  # Don't consider the buffer
        #     self.enemy_visits += 1
        #     self.logger.debug(f"Enemy visited {self.zone_type} zone")
        #
        # if self.polygon.contains(enemy_position):  # Don't consider the buffer
        #     self.ally_visits += 1
        #     self.logger.debug(f"Ally visited {self.zone_type} zone")

        self.last_update_time = Utils.get_ts()

    """ Built-in methods """

    def __instancecheck__(self, other) -> bool:
        """Checks if two objects are instances of the same class."""
        return type(self) == type(other) and (
            isinstance(self, type(other))
            or isinstance(other, type(self))
            or isinstance(self, other)
        )

    def __eq__(self, other) -> bool:
        """Checks equality based on polygon geometry and accessibility."""
        if not isinstance(self, type(other)):
            return False
        return (
            self.polygon == getattr(other, "polygon", None)
            and self.buffered_polygon == getattr(other, "buffered_polygon", None)
            and self.accessibility == getattr(other, "accessibility", None)
        )

    def __ne__(self, other) -> bool:
        """Checks inequality based on polygon geometry and accessibility."""
        return not self.__eq__(other)

    def __str__(self) -> str:
        """Provides a string representation of the zone."""
        return (
            f"{self.zone_type}: {self.buffered_polygon.centroid} -> {self.accessibility}, "
            f"ally visits: {self.ally_visits}, enemy visits: {self.enemy_visits}, "
            f"last update: {self.last_update_time}, "
            f"go-to positions: {self.go_to_positions}"
        )

    def __repr__(self) -> str:
        """Provides the official string representation of the zone."""
        return self.__str__()

    def __format__(self, format_spec):
        """Formats the zone as a string."""
        return self.__str__()
