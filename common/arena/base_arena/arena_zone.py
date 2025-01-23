# ====== Code Summary ======
# The code defines a framework for managing zones in an arena. It includes:
# - Enumerations for zone types (`ZoneType`) and their accessibility (`ZoneAccessibility`).
# - A base class (`BaseArenaZone`) to represent a generic zone
#   with attributes for geometry, type, color, and visit counters.
# - Specialized classes derived from `BaseArenaZone` for specific zone types such as `EnemyZone`, `StuffZone`, etc.
#   Each class provides default settings and configurations relevant to its purpose.

# ====== Imports ======
# Standard library imports
from abc import ABC, abstractmethod
from dataclasses import dataclass
from collections import deque
from enum import Enum, auto

# Internal project imports
from logger import Logger, LogLevels
from arena.base_arena import GridManager
from utils import Utils
from geometry import (
    Polygon,
    BufferCapStyle,
    BufferJoinStyle,
    Point,
    OrientedPoint,
    LineString,
    create_straight_rectangle,
)


# ====== Enums ======
class ZoneType(Enum):
    """Enumeration for different types of zones in the arena."""

    YELLOW_RESERVED = auto()
    BLUE_RESERVED = auto()
    FORBIDDEN = auto()
    STUFF_ZONE = auto()
    ENEMY = auto()
    ALLY = auto()
    BORDER_ZONE = auto()


class ZoneAccessibility(Enum):
    """Enumeration for zone accessibility types in the arena."""

    FREE = auto()  # Free to navigate
    RESTRICTED = auto()  # Restricted access; emergencies only
    FORBIDDEN = auto()  # Forbidden access; cannot be entered


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
        self_visits (int): Count of self visits.
    """

    def __init__(
            self,
            logger: Logger,
            zone_type: ZoneType,
            accessibility: ZoneAccessibility,
            buffer_size: float = 0.0,
            polygon: Polygon = None,
            buffered_polygon: Polygon = None,
            update_callback: callable = None,
            zone_color: str = "#f0aef2",
    ) -> None:
        self.logger: Logger = logger
        self.zone_type: ZoneType = zone_type
        self.accessibility: ZoneAccessibility = accessibility

        if polygon is None and buffered_polygon is None:
            self.logger.log("No polygon provided for zone", LogLevels.ERROR)

        elif polygon is not None and buffered_polygon is None:
            buffered_polygon = self.add_buffer_to_zone(polygon, buffer_size)
        elif polygon is None and buffered_polygon is not None:
            polygon = self.add_buffer_to_zone(buffered_polygon, -buffer_size)

        self.buffer_size: float = buffer_size
        self.polygon: Polygon = polygon
        self.buffered_polygon: Polygon = buffered_polygon

        self.update_callback = update_callback

        self.zone_color: str = zone_color
        self.enemy_visits: int = 0
        self.ally_visits: int = 0
        self.last_update_time: float = 0.0

    @staticmethod
    def add_buffer_to_zone(polygon: Polygon, buffer: float) -> Polygon:
        """
        Adds a buffer around a zone to account for obstacle or border spacing.
        The buffer uses a square cap style to match the grid structure.
        """
        return polygon.buffer(
            buffer, cap_style=BufferCapStyle.flat, join_style=BufferJoinStyle.mitre
        )

    def is_accessible(self, team_color=None) -> bool:
        """Determines if the zone is accessible for a given team color."""
        return self.accessibility not in [
            ZoneAccessibility.FORBIDDEN,
            ZoneAccessibility.RESTRICTED,
        ]

    def is_accessible_for_emergency(self, team_color=None) -> bool:
        """Determines if the zone is accessible in an emergency."""
        return self.accessibility != ZoneAccessibility.FORBIDDEN

    def __eq__(self, other):
        if not self.is_instance(other):
            return False

        if hasattr(other, "polygon"):
            return self.polygon == other.polygon

        return True

    def __ne__(self, other):
        return not self.__eq__(other)

    def is_instance(self, other):
        return (
                isinstance(self, type(other))
                or isinstance(other, type(self))
                or isinstance(self, other)
        )

    def __str__(self) -> str:
        return (
            f"{self.zone_type}: {self.buffered_polygon.centroid} -> {self.accessibility}, "
            f"ally visits: {self.ally_visits}, enemy visits: {self.enemy_visits}, "
            f"last update: {self.last_update_time}"
        )

    def __repr__(self) -> str:
        return self.__str__()

    def update(
            self, color_team: str, ally_positions: list[Point], enemy_positions: list[Point]
    ) -> None:
        """Update the zone based on the positions of allies and enemies."""

        # Update visit counts
        for position in enemy_positions:
            if self.polygon.contains(position):  # Don't consider the buffer
                self.enemy_visits += 1
                self.logger.log(f"Enemy visited {self.zone_type} zone", LogLevels.DEBUG)

        for position in ally_positions:
            if self.polygon.contains(position):  # Don't consider the buffer
                self.ally_visits += 1
                self.logger.log(f"Ally visited {self.zone_type} zone", LogLevels.DEBUG)

        self.last_update_time = Utils.get_ts()


# ====== Specific Zone Classes ======
class ForbiddenZone(BaseArenaZone):
    """Zone that is strictly forbidden."""

    def __init__(
            self,
            logger: Logger,
            accessibility: ZoneAccessibility = ZoneAccessibility.FORBIDDEN,
            buffer_size: float = 0.0,
            polygon: Polygon = None,
            buffered_polygon: Polygon = None,
            update_callback: callable = None,
    ) -> None:
        super().__init__(
            logger=logger,
            zone_type=ZoneType.FORBIDDEN,
            accessibility=accessibility,
            buffer_size=buffer_size,
            polygon=polygon,
            buffered_polygon=buffered_polygon,
            update_callback=update_callback,
            zone_color="#2b2b2b",
        )


@dataclass
class Record:
    timestamp: float
    position: Point


@dataclass
class SpeedVector:
    speed: float
    dx: float
    dy: float
    factor: float = 1.0

    @property
    def factored_dx(self):
        return self.dx * self.factor

    @property
    def factored_dy(self):
        return self.dy * self.factor


class EnemyZone(BaseArenaZone):
    """Zone designated for enemies, dynamically updated based on their position."""

    def __init__(
            self,
            logger: Logger,
            point: Point,
            accessibility: ZoneAccessibility = ZoneAccessibility.FORBIDDEN,
            robot_size: float = 10,
            positions_record_size: int = 3,
            no_detection_timeout: float = 4.0,
            positions_recorded: deque = None,
            speed_vector: SpeedVector = SpeedVector(0.0, 0.0, 0.0),
            vector_factor: float = 50.0,
            # taille du vecteur de déplacement, on peur choisir à quelle point on donne de l'importance à la direction
    ) -> None:
        self.point = point
        self.robot_size = robot_size
        self.no_detection_timeout = no_detection_timeout

        self.speed_vector: SpeedVector = speed_vector
        self.speed_vector.factor = vector_factor

        self.positions_record_size: int = positions_record_size
        if positions_recorded is None:
            self.__positions_recorded: deque = deque(maxlen=positions_record_size)
        else:
            self.__positions_recorded = positions_recorded

        # Compute robot vector
        vector_line = LineString(
            [
                self.point,
                Point(
                    self.point.x + self.speed_vector.factored_dx,
                    self.point.y + self.speed_vector.factored_dy
                )
            ]
        )
        buffered_vector_line: Polygon = vector_line.buffer(self.robot_size)

        super().__init__(
            logger=logger,
            zone_type=ZoneType.FORBIDDEN,
            accessibility=accessibility,
            buffer_size=0.0,
            buffered_polygon=buffered_vector_line,
            update_callback=None,
            zone_color="#EE0505",
        )

    def _compute_enemy_speed_vector(self) -> SpeedVector:
        """
        Computes the speed (magnitude of velocity) and direction (unit vector)
        of the enemy based on the recorded positions.

        Returns:
            speed: float
                The speed magnitude (distance / time).
            direction: tuple(float, float)
                The unit vector (dx, dy) indicating the velocity direction.
                (0.0, 0.0) if the speed is zero or if there is insufficient data.
        """
        self.logger.log("Starting computation of enemy speed vector.", LogLevels.DEBUG)

        # At least two positions are required to calculate speed
        if len(self.__positions_recorded) < 2:
            self.logger.log("Not enough positions recorded to compute speed vector.", LogLevels.DEBUG)
            return SpeedVector(0, 0, 0)

        # First and last recorded positions
        start_record = self.__positions_recorded[0]
        end_record = self.__positions_recorded[-1]
        self.logger.log(
            f"Start position: {start_record.position}, End position: {end_record.position}.",
            LogLevels.DEBUG
        )

        # Compute the time delta
        timestamp_delta = end_record.timestamp - start_record.timestamp
        self.logger.log(f"Time delta: {timestamp_delta} seconds.", LogLevels.DEBUG)

        if timestamp_delta <= 0:
            self.logger.log("Invalid or zero time delta. Aborting computation.", LogLevels.DEBUG)
            return SpeedVector(0, 0, 0)

        # Check for no_detection_timeout
        if timestamp_delta > self.no_detection_timeout:
            self.logger.log(
                f"Time delta exceeds no_detection_timeout ({self.no_detection_timeout}s). Returning zero vector.",
                LogLevels.DEBUG
            )
            return SpeedVector(0, 0, 0)

        # Compute the displacement vector
        dx = end_record.position.x - start_record.position.x
        dy = end_record.position.y - start_record.position.y
        self.logger.log(f"Displacement vector: dx={dx}, dy={dy}.", LogLevels.DEBUG)

        # Compute the distance traveled
        distance = start_record.position.distance(end_record.position)
        self.logger.log(f"Distance traveled: {distance}.", LogLevels.DEBUG)

        # Calculate the scalar speed
        speed = distance / timestamp_delta
        self.logger.log(f"Calculated speed: {speed}.", LogLevels.DEBUG)

        if distance == 0.0:
            self.logger.log("No displacement detected. Returning zero vector.", LogLevels.DEBUG)
            return SpeedVector(0, 0, 0)

        # Compute the direction (unit vector)
        dir_x = dx / distance
        dir_y = dy / distance
        self.logger.log(f"Direction vector: dir_x={dir_x}, dir_y={dir_y}.", LogLevels.DEBUG)

        self.logger.log("Speed vector computation completed successfully.", LogLevels.DEBUG)
        return SpeedVector(speed, dir_x, dir_y)

    def update(
            self, team_color: str, ally_positions: list[Point], enemy_positions: list[Point]
    ) -> None:
        super().update(team_color, ally_positions, enemy_positions)
        self.__positions_recorded.append(Record(Utils.get_ts(), enemy_positions[0]))

        self.speed_vector: SpeedVector = self._compute_enemy_speed_vector()

        self.__init__(
            logger=self.logger,
            point=enemy_positions[0],  # Assume there is only 1 enemy
            accessibility=self.accessibility,
            robot_size=self.robot_size,
            positions_record_size=self.positions_record_size,
            no_detection_timeout=self.no_detection_timeout,
            positions_recorded=self.__positions_recorded,
            speed_vector=self.speed_vector,
        )

    def __str__(self):
        return (
                super().__str__() +
                f" Speed: {self.speed_vector.speed}, "
                f"Direction: ({self.speed_vector.dx}, {self.speed_vector.dy})"
        )

    def __repr__(self):
        return self.__str__()


class AllyZone(BaseArenaZone):
    """Zone designated for ally, dynamically updated based on their position."""

    def __init__(
            self,
            logger: Logger,
            point: OrientedPoint,
            accessibility: ZoneAccessibility = ZoneAccessibility.FREE,
            robot_size: float = 2,  # Assume the robot is a square 2/2 = 1 side length
    ) -> None:
        position_based_polygon = create_straight_rectangle(
            Point(point.x - robot_size, point.y - robot_size),
            Point(point.x + robot_size, point.y + robot_size),
        )

        self.point: OrientedPoint = point
        self.robot_size: float = robot_size
        super().__init__(
            logger=logger,
            zone_type=ZoneType.ALLY,
            accessibility=accessibility,
            buffer_size=0.0,
            polygon=position_based_polygon,
            buffered_polygon=None,
            update_callback=None,
            zone_color="#8af542",
        )

    def update(
            self, team_color: str, ally_positions: list[OrientedPoint | Point], enemy_positions: list[Point]
    ) -> None:
        super().update(team_color, ally_positions, enemy_positions)
        self.__init__(
            logger=self.logger,
            point=ally_positions[0],  # Assume there is only 1 ally
            accessibility=self.accessibility,
            robot_size=self.robot_size,
        )


class StuffZone(BaseArenaZone):
    """Zone designated for storage or placement of items."""

    def __init__(
            self,
            logger: Logger,
            accessibility: ZoneAccessibility = ZoneAccessibility.RESTRICTED,
            buffer_size: float = 0.0,
            polygon: Polygon = None,
            buffered_polygon: Polygon = None,
            update_callback: callable = None,
            index: int = 0
    ) -> None:
        self.index = index
        super().__init__(
            logger=logger,
            zone_type=ZoneType.STUFF_ZONE,
            accessibility=accessibility,
            buffer_size=buffer_size,
            polygon=polygon,
            buffered_polygon=buffered_polygon,
            update_callback=update_callback,
            zone_color="#0FEE9C",
        )

    def update(
            self, team_color: str, ally_positions: list[Point], enemy_positions: list[Point]
    ) -> None:
        super().update(team_color, ally_positions, enemy_positions)


class BlueReservedZone(BaseArenaZone):
    """Zone reserved for operations of the blue team."""

    def __init__(
            self,
            logger: Logger,
            accessibility: ZoneAccessibility = ZoneAccessibility.RESTRICTED,
            buffer_size: float = 0.0,
            polygon: Polygon = None,
            buffered_polygon: Polygon = None,
            update_callback: callable = None,
    ) -> None:
        super().__init__(
            logger=logger,
            zone_type=ZoneType.BLUE_RESERVED,
            accessibility=accessibility,
            buffer_size=buffer_size,
            polygon=polygon,
            buffered_polygon=buffered_polygon,
            update_callback=update_callback,
            zone_color="#097D8D",
        )

    def is_accessible(self, team_color=None) -> bool:
        """Determines if the zone is accessible specifically for the blue team."""
        return super().is_accessible(team_color) and (
                team_color is None or team_color.lower() in ["blue", "b"]
        )

    def update(
            self, team_color: str, ally_positions: list[Point], enemy_positions: list[Point]
    ) -> None:
        """Update the zone based on the positions of allies and enemies."""
        super().update(team_color, ally_positions, enemy_positions)

        # Update accessibility based on team color
        if self.accessibility != ZoneAccessibility.FREE and (
                team_color is None or team_color.lower() in ["blue", "b"]
        ):
            self.accessibility = ZoneAccessibility.FREE

            # Get grid manager from arena callback function
            grid_manager: GridManager = self.update_callback()
            grid_manager.remove_forbidden_static_zone(self.buffered_polygon)

            self.logger.log(f"{self.zone_type} zone is now accessible", LogLevels.DEBUG)


class YellowReservedZone(BaseArenaZone):
    """Zone reserved for operations of the yellow team."""

    def __init__(
            self,
            logger: Logger,
            accessibility: ZoneAccessibility = ZoneAccessibility.RESTRICTED,
            buffer_size: float = 0.0,
            polygon: Polygon = None,
            buffered_polygon: Polygon = None,
            update_callback: callable = None,
    ) -> None:
        super().__init__(
            logger=logger,
            zone_type=ZoneType.YELLOW_RESERVED,
            accessibility=accessibility,
            buffer_size=buffer_size,
            polygon=polygon,
            buffered_polygon=buffered_polygon,
            update_callback=update_callback,
            zone_color="#ECC92E",
        )

    def is_accessible(self, team_color=None) -> bool:
        """Determines if the zone is accessible specifically for the yellow team."""
        return super().is_accessible(team_color) and team_color.lower() in [
            "yellow",
            "y",
        ]

    def update(
            self, team_color: str, ally_positions: list[Point], enemy_positions: list[Point]
    ) -> None:
        """Update the zone based on the positions of allies and enemies."""
        super().update(team_color, ally_positions, enemy_positions)

        # Update accessibility based on team color
        if self.accessibility != ZoneAccessibility.FREE and (
                team_color is None or team_color.lower() in ["yellow", "y"]
        ):
            self.accessibility = ZoneAccessibility.FREE
            # Get grid manager from arena callback function
            grid_manager: GridManager = self.update_callback()
            grid_manager.remove_forbidden_static_zone(self.buffered_polygon)

            self.logger.log(f"{self.zone_type} zone is now accessible", LogLevels.DEBUG)


class BorderZone(BaseArenaZone):
    """Zone representing the borders of the arena."""

    def __init__(
            self,
            logger: Logger,
            accessibility: ZoneAccessibility = ZoneAccessibility.FORBIDDEN,
            buffer_size: float = 0.0,
            polygon: Polygon = None,
            buffered_polygon: Polygon = None,
            update_callback: callable = None,
    ) -> None:
        super().__init__(
            logger=logger,
            zone_type=ZoneType.BORDER_ZONE,
            accessibility=accessibility,
            buffer_size=buffer_size,
            polygon=polygon,
            buffered_polygon=buffered_polygon,
            update_callback=update_callback,
            zone_color="#EF0D0D",
        )
