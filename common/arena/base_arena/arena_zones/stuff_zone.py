"""Zone designated for storing or placing items during matches."""

from __future__ import annotations

from typing import TYPE_CHECKING, override

from arena.base_arena.arena_zones.base_arena_zone import BaseArenaZone
from arena.base_arena.arena_zones.structs import ZoneAccessibility, ZoneType
from geometry import OrientedPoint

if TYPE_CHECKING:
    from collections.abc import Callable

    from loggerplusplus import Logger

    from arena.base_arena.team_color import TeamColor
    from geometry import Polygon


class StuffZone(BaseArenaZone):
    """Zone designated for storage or placement of items."""

    def __init__(
        self,
        logger: Logger,
        buffer_size: float = 0.0,
        polygon: Polygon | None = None,
        buffered_polygon: Polygon | None = None,
        update_callback: Callable | None = None,
        go_to_positions: list[OrientedPoint] | None = None,
    ) -> None:
        """Initializes the StuffZone with geometry, buffer, and accessibility.

        Args:
            logger (Logger): Logger instance for logging messages.
            buffer_size (float, optional):
                Buffer size for geometric adjustments. Defaults to 0.0.
            polygon (Polygon | None, optional):
                Polygon representing the zone geometry. Defaults to None.
            buffered_polygon (Polygon | None, optional):
                Buffered polygon geometry. Defaults to None.
            update_callback (Callable | None, optional):
                Function to be called on updates. Defaults to None.
            go_to_positions (list[OrientedPoint] | None, optional):
                List of go-to positions within the zone. Defaults to None.
        """
        super().__init__(
            logger=logger,
            zone_type=ZoneType.STUFF_ZONE,
            accessibility=ZoneAccessibility.RESTRICTED,
            buffer_size=buffer_size,
            polygon=polygon,
            buffered_polygon=buffered_polygon,
            update_callback=update_callback,
            zone_color="#0FEE9C",
            go_to_positions=go_to_positions,
        )

    @override
    def update(
        self,
        team_color: TeamColor,
        ally_position: OrientedPoint,
        enemy_position: OrientedPoint,
    ) -> None:
        """Updates the zone accessibility based on the positions of allies and enemies.

        Args:
            team_color (TeamColor): The color of the team.
            ally_position (OrientedPoint): Position of an ally.
            enemy_position (OrientedPoint): Position of an enemy.
        """
        super().update(team_color, ally_position, enemy_position)

        # Update accessibility to free if an ally or enemy is within the zone
        if (
            self.buffered_polygon.contains(ally_position)
            or self.buffered_polygon.contains(enemy_position)
        ) and self.accessibility != ZoneAccessibility.FREE:
            self._make_accessible()

    @override
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
        if self.accessibility == ZoneAccessibility.FORBIDDEN:
            self.logger.debug(
                f"GoTo position request: Zone {self.zone_type} is not accessible.",
            )
            return None

        # If no specific go-to positions are defined, return the centroid of the zone
        if not self.go_to_positions:
            self.logger.debug(
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
        self.logger.debug(msg)

        return nearest_position
