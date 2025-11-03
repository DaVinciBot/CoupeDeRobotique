"""Zones that compute speed vectors from enemy movement records."""

from __future__ import annotations

from collections import deque
from typing import TYPE_CHECKING, override

from arena.base_arena.arena_zones.base_arena_zone import BaseArenaZone
from arena.base_arena.arena_zones.structs import (
    Record,
    SpeedVector,
    ZoneAccessibility,
    ZoneType,
)
from geometry import LineString, OrientedPoint
from utils import Utils

if TYPE_CHECKING:
    from collections.abc import Callable

    from loggerplusplus import Logger

    from arena.base_arena.team_color import TeamColor

MIN_RECORDS_FOR_VECTOR = 2


class BaseSpeedVectorAutoCalculateZone(BaseArenaZone):
    """Represent a zone that auto-calculates speed vectors from enemy movement."""

    def __init__(
        self,
        logger: Logger,
        zone_type: ZoneType,
        accessibility: ZoneAccessibility,
        point: OrientedPoint,
        vector_width: float,
        buffer_size: float = 0.0,
        update_callback: Callable | None = None,
        zone_color: str = "#9e9e9e",
        positions_record_size: int = 3,
        no_detection_timeout: float = 4.0,
        positions_recorded: deque[Record] | None = None,
        speed_vector: SpeedVector | None = None,
        vector_factor: float = 25.0,
    ) -> None:
        """Initialize the speed vector auto-calculate zone.

        Args:
            logger (Logger): Logger instance for debugging.
            zone_type (ZoneType): Type of the zone.
            accessibility (ZoneAccessibility): Accessibility properties of the
                zone.
            point (OrientedPoint): Central point of the zone.
            vector_width (float): Width of the vector representation.
            buffer_size (float, optional): Buffer size. Defaults to 0.0.
            update_callback (Callable | None, optional): Function to call when the
                zone updates. Defaults to None.
            zone_color (str, optional): Color representation of the zone. Defaults
                to "#9e9e9e".
            positions_record_size (int, optional): Maximum number of position
                records. Defaults to 3.
            no_detection_timeout (float, optional): Timeout before considering no
                detection. Defaults to 4.0.
            positions_recorded (deque[Record] | None, optional): Queue storing
                recorded positions. Defaults to None.
            speed_vector (SpeedVector | None, optional): Current speed vector.
                Defaults to None.
            vector_factor (float, optional): Scaling factor for vector influence.
                Defaults to 25.0.
        """
        self.point = point
        self.vector_width = vector_width
        self.no_detection_timeout = no_detection_timeout
        self.speed_vector = speed_vector or SpeedVector(0.0, 0.0, 0.0)
        self.speed_vector.factor = vector_factor
        self.positions_record_size = positions_record_size
        self.__positions_recorded: deque[Record] = (
            deque(maxlen=positions_record_size)
            if positions_recorded is None
            else positions_recorded
        )

        # Compute initial robot vector representation
        vector_line = self._compute_vector_line()

        super().__init__(
            logger=logger,
            zone_type=zone_type,
            accessibility=accessibility,
            buffer_size=buffer_size,
            buffered_polygon=vector_line.buffer(self.vector_width),
            update_callback=update_callback,
            zone_color=zone_color,
        )

    def _compute_vector_line(self) -> LineString:
        return LineString(
            [
                self.point,
                OrientedPoint(
                    self.point.x + self.speed_vector.factored_dx,
                    self.point.y + self.speed_vector.factored_dy,
                ),
            ],
        )

    def _compute_enemy_speed_vector(self) -> SpeedVector:
        """Compute the speed vector based on recorded enemy positions.

        Returns:
            SpeedVector: Computed speed vector with magnitude and direction.
        """
        if len(self.__positions_recorded) < MIN_RECORDS_FOR_VECTOR:
            self._logger.debug(
                "Not enough positions recorded to compute speed vector. "
                "Returning zero vector.",
            )
            return SpeedVector(0, 0, 0)

        start_record, end_record = (
            self.__positions_recorded[0],
            self.__positions_recorded[-1],
        )
        timestamp_delta = end_record.timestamp - start_record.timestamp

        if timestamp_delta <= 0 or timestamp_delta > self.no_detection_timeout:
            self._logger.debug(
                "Invalid or outdated time delta. Returning zero vector.",
            )
            return SpeedVector(0, 0, 0)

        dx, dy = (
            end_record.position.x - start_record.position.x,
            end_record.position.y - start_record.position.y,
        )
        distance = start_record.position.distance(end_record.position)
        speed = distance / timestamp_delta if distance else 0

        if not speed:
            self._logger.debug("No displacement detected. Returning zero vector.")
            return SpeedVector(0, 0, 0)

        return SpeedVector(speed, dx / distance, dy / distance)

    @override
    def update(
        self,
        team_color: TeamColor,
        ally_position: OrientedPoint,
        enemy_position: OrientedPoint,
    ) -> None:
        """Update the zone state based on detected enemy movement.

        Args:
            team_color (TeamColor, optional): The color of the team.
            ally_position (OrientedPoint): Position of ally.
            enemy_position (OrientedPoint): Position of enemy.
        """
        super().update(team_color, ally_position, enemy_position)
        self.point = enemy_position
        self.__positions_recorded.append(Record(Utils.get_ts(), enemy_position))
        self.speed_vector = self._compute_enemy_speed_vector()

        vector_line = self._compute_vector_line()

        super().__init__(
            logger=self._logger,
            zone_type=self.zone_type,
            accessibility=self.accessibility,
            buffer_size=self.buffer_size,
            buffered_polygon=vector_line.buffer(self.vector_width),
            update_callback=self.update_callback,
            zone_color=self.zone_color,
            uid=self.uid,  # Avoid reassigning a new uid
        )

    @override
    def __str__(self) -> str:
        """Return a human-readable description of the zone.

        Returns:
            str: Text describing the zone and its speed vector.
        """
        return (
            f"{super().__str__()} Speed: {self.speed_vector.speed}, "
            f"Direction: ({self.speed_vector.dx}, {self.speed_vector.dy})"
        )

    @override
    def __repr__(self) -> str:
        """Return an unambiguous representation of the zone state.

        Returns:
            str: Detailed state string including speed vector information.
        """
        return (
            f"{super().__repr__()} Speed: {self.speed_vector.speed}, "
            f"Direction: ({self.speed_vector.dx}, {self.speed_vector.dy}) "
            f"Vector Factor: {self.speed_vector.factor}, "
            f"Positions Recorded: {list(self.__positions_recorded)}, "
            f"Vector Width: {self.vector_width}, "
            f"No Detection Timeout: {self.no_detection_timeout}, "
            f"Positions Recorded Size: {self.positions_record_size}"
        )

    @override
    def __format__(self, _format_spec: str) -> str:
        """Format the string representation of the zone.

        Args:
            _format_spec (str): Format specification passed to :func:``format``.

        Returns:
            str: Formatted representation.
        """
        return self.__str__()
