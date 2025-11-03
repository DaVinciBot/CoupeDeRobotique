"""Generic arena zone with geometry and accessibility handling.

Provides utilities to manage zone geometry, accessibility, visit tracking, and
common built-in comparisons.
"""

from __future__ import annotations

from abc import ABC
from typing import TYPE_CHECKING, ClassVar, override

from arena.base_arena.arena_zones.structs import ZoneAccessibility, ZoneType
from arena.base_arena.team_color import TeamColor
from geometry import BufferCapStyle, BufferJoinStyle, OrientedPoint, Polygon
from utils import Utils

if TYPE_CHECKING:
    from collections.abc import Callable

    from loggerplusplus import Logger

    from arena.base_arena.grid_manager import GridManager


class BaseArenaZone(ABC):
    """Represent a zone within an arena with geometry, type, and accessibility.

    Attributes:
        zones_uid (ClassVar[list[int]]): Sequence of used identifiers for zones.
    """

    zones_uid: ClassVar[list[int]] = []

    def __init__(
        self,
        logger: Logger,
        zone_type: ZoneType,
        accessibility: ZoneAccessibility,
        buffer_size: float = 0.0,
        polygon: Polygon | None = None,
        buffered_polygon: Polygon | None = None,
        update_callback: Callable | None = None,
        zone_color: str = "#9e9e9e",
        go_to_positions: list[OrientedPoint] | None = None,
        uid: int | None = None,
    ) -> None:
        """Initialize the zone with geometry, type, color, and accessibility.

        Args:
            logger (Logger): Logger instance for logging messages.
            zone_type (ZoneType): Category of the zone.
            accessibility (ZoneAccessibility): Accessibility of the zone.
            buffer_size (float, optional):
                Buffer size for geometric adjustments. Defaults to 0.0.
            polygon (Polygon | None, optional):
                Polygon representing the zone geometry. Defaults to None.
            buffered_polygon (Polygon | None, optional):
                Buffered polygon geometry. Defaults to None.
            update_callback (Callable | None, optional):
                Function called on updates. Defaults to None.
            zone_color (str, optional):
                Color associated with the zone. Defaults to "#9e9e9e".
            go_to_positions (list[OrientedPoint] | None, optional):
                List of go-to positions within the zone. Defaults to None.
            uid (int | None, optional):
                Unique identifier for the zone instance. Defaults to None.

        Raises:
            ValueError: If neither polygon nor buffered_polygon is provided.
        """
        self._logger: Logger = logger
        self.zone_type: ZoneType = zone_type
        self.accessibility: ZoneAccessibility = accessibility

        if polygon is None and buffered_polygon is None:
            self._logger.error("No polygon provided for zone")
            msg = "At least one of polygon or buffered_polygon must be provided"
            raise ValueError(msg)
        if polygon is not None and buffered_polygon is None:
            buffered_polygon = self.add_buffer_to_zone(polygon, buffer_size)
        elif polygon is None and buffered_polygon is not None:
            polygon = self.add_buffer_to_zone(buffered_polygon, -buffer_size)

        assert polygon is not None, "Polygon should be defined here"  # noqa: S101
        assert buffered_polygon is not None, "Buffered polygon should be defined here"  # noqa: S101

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
    def get_new_uid(cls, input_uid: int | None) -> int:
        """Return a unique identifier for a zone.

        Args:
            input_uid (int | None): Requested identifier. Defaults to None.

        Returns:
            int: Newly generated identifier.
        """
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
        """Add a buffer around a zone.

        The buffer uses a square cap style to match the grid structure.

        Args:
            polygon (Polygon): Polygon to buffer.
            buffer (float): Buffer size to apply.

        Returns:
            Polygon: Buffered polygon.
        """
        return polygon.buffer(
            buffer,
            cap_style=BufferCapStyle.flat,
            join_style=BufferJoinStyle.mitre,
        )

    # region ====== Accessibility methods ======

    def is_accessible(
        self,
        team_color: TeamColor = TeamColor.UNDEFINED,  # noqa:ARG002
    ) -> bool:
        """Determine if the zone is accessible for a given team color.

        Args:
            team_color (TeamColor, optional):
                Color of the team. Defaults to TeamColor.UNDEFINED.

        Returns:
            bool: ``True`` if accessible, ``False`` otherwise.
        """
        return self.accessibility not in {
            ZoneAccessibility.FORBIDDEN,
            ZoneAccessibility.RESTRICTED,
        }

    def is_accessible_for_emergency(
        self,
        team_color: TeamColor = TeamColor.UNDEFINED,  # noqa: ARG002
    ) -> bool:
        """Determine if the zone is accessible in an emergency.

        Args:
            team_color (TeamColor, optional): Color of the team.
                Defaults to TeamColor.UNDEFINED.

        Returns:
            bool: ``True`` if accessible in emergencies, ``False`` otherwise.
        """
        return self.accessibility != ZoneAccessibility.FORBIDDEN

    def get_go_to_position(
        self,
        ally_position: OrientedPoint,
        team_color: TeamColor,
    ) -> OrientedPoint | None:
        """Determine the best go-to position for an ally in the given zone.

        Args:
            ally_position (OrientedPoint): Position of the ally.
            team_color (TeamColor): Color of the team.

        Returns:
            OrientedPoint | None:
                Best go-to position, or ``None`` if inaccessible.
        """
        if not self.is_accessible(team_color):
            self._logger.debug(
                f"GoTo position request: Zone {self.zone_type} is not accessible.",
            )
            return None

        # If no specific go-to positions are defined, return the centroid of the zone
        if not self.go_to_positions:
            self._logger.debug(
                "GoTo position request: "
                f"No defined go-to positions for zone {self.zone_type}, "
                f"returning centroid [{self.polygon.centroid}]",
            )
            return OrientedPoint.from_point(self.polygon.centroid)

        nearest_position = min(
            self.go_to_positions,
            key=ally_position.distance,
        )
        msg = (
            "GoTo position request: Nearest go-to position to ally "
            f"[{ally_position}] is [{nearest_position}]"
        )
        self._logger.debug(msg)

        return nearest_position

    # endregion

    # region ====== Update methods ======

    def update(
        self,
        team_color: TeamColor,  # noqa: ARG002
        ally_position: OrientedPoint,
        enemy_position: OrientedPoint,
    ) -> None:
        """Update the zone based on the positions of allies and enemies.

        Args:
            team_color (TeamColor): Color of the team.
            ally_position (OrientedPoint): Position of the ally.
            enemy_position (OrientedPoint): Position of the enemy.
        """
        # Update visit counts
        if self.polygon.contains(enemy_position):  # Don't consider the buffer
            self.enemy_visits += 1
            self._logger.debug(f"Enemy visited {self.zone_type} zone")

        if self.polygon.contains(ally_position):  # Don't consider the buffer
            self.ally_visits += 1
            self._logger.debug(f"Ally visited {self.zone_type} zone")

        self.last_update_time = Utils.get_ts()

    def _make_accessible(self) -> None:
        """Mark the zone as accessible and update the grid manager."""
        self.accessibility = ZoneAccessibility.FREE
        grid_manager: GridManager = self.update_callback()  # type: ignore[call-arg]
        grid_manager.remove_forbidden_static_zone(self.buffered_polygon)
        self._logger.debug(f"{self.zone_type} zone is now accessible")

    def _restrict_accessibility(self) -> None:
        """Mark the zone as restricted and update the grid manager."""
        self.accessibility = ZoneAccessibility.RESTRICTED
        grid_manager: GridManager = self.update_callback()  # type: ignore[call-arg]
        grid_manager.add_forbidden_static_zone(self.buffered_polygon)
        self._logger.debug(f"{self.zone_type} zone is now restricted")

    # endregion

    # region ====== Built-in methods ======

    def __instancecheck__(self, other: object) -> bool:
        """Return ``True`` if ``other`` is an instance of the same class.

        Args:
            other (object): Object to compare against.

        Returns:
            bool: ``True`` if ``other`` shares this class type.
        """
        return type(self) is type(other) and (
            isinstance(self, type(other)) or isinstance(other, type(self))
        )

    @override
    def __eq__(self, other: object) -> bool:
        """Return ``True`` if ``other`` has the same geometry and accessibility.

        Args:
            other (object): Object to compare against.

        Returns:
            bool: ``True`` if polygons and accessibility match.
        """
        if not isinstance(self, type(other)):
            return False
        return (
            self.polygon == getattr(other, "polygon", None)
            and self.buffered_polygon == getattr(other, "buffered_polygon", None)
            and self.accessibility == getattr(other, "accessibility", None)
        )

    @override
    def __ne__(self, other: object) -> bool:
        """Return ``True`` if ``other`` differs in geometry or accessibility.

        Args:
            other (object): Object to compare against.

        Returns:
            bool: ``True`` if zones are not equal.
        """
        return not self.__eq__(other)

    @override
    def __str__(self) -> str:
        """Return a concise string representation of the zone.

        Returns:
            str: Human-readable information about the zone.
        """
        return (
            f"{self.zone_type}: {self.buffered_polygon.centroid} -> "
            f"{self.accessibility}, ally visits: {self.ally_visits}, "
            f"enemy visits: {self.enemy_visits}, last update: {self.last_update_time}, "
            f"go-to positions: {self.go_to_positions}"
        )

    @override
    def __repr__(self) -> str:
        """Return the official string representation of the zone.

        Returns:
            str: Formal representation of the zone.
        """
        return self.__str__()

    @override
    def __hash__(self) -> int:
        """Return a hash based on the zone unique identifier.

        Returns:
            int: Hash value for the zone.
        """
        return hash(self.uid)

    @override
    def __format__(self, _format_spec: str) -> str:
        """Format the zone as a string.

        Args:
            _format_spec (str): Formatting specification.

        Returns:
            str: Formatted representation.
        """
        return self.__str__()

    # endregion
