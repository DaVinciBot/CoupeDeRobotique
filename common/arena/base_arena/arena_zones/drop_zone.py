"""Zone designated to deposit jengas."""

from __future__ import annotations

from typing import TYPE_CHECKING, override

from arena.base_arena.arena_zones.base_arena_zone import BaseArenaZone
from arena.base_arena.arena_zones.structs import ZoneAccessibility, ZoneType

if TYPE_CHECKING:
    from collections.abc import Callable

    from loggerplusplus import Logger

    from arena.base_arena.team_color import TeamColor
    from geometry import OrientedPoint, Point, Polygon


class DropZone(BaseArenaZone):
    """Zone designated for storage or placement of items."""
    def __init__(
            self,
            logger: Logger,
            buffer_size: float = 0.0,
            polygon: Polygon | None = None,
            buffered_polygon: Polygon | None = None,
            update_callback: Callable | None = None,
            go_to_positions: list[OrientedPoint | Point] | None = None,
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
            go_to_positions (list[OrientedPoint | Point] | None, optional):
                List of go-to positions within the zone. Defaults to None.
        """
        super().__init__(
            logger=logger,
            zone_type=ZoneType.DEPOSIT_ZONE,
            accessibility=ZoneAccessibility.FREE,
            buffer_size=buffer_size,
            polygon=polygon,
            buffered_polygon=buffered_polygon,
            update_callback=update_callback,
            zone_color="#008000",
            go_to_positions=go_to_positions,
        )

    @override
    def update(
            self,
            team_color: TeamColor,
            ally_position: Point | OrientedPoint,
            enemy_position: Point | OrientedPoint,
    ) -> None:
        """Updates the zone accessibility based on the positions of allies and enemies.

        Args:
            team_color (TeamColor): The color of the team.
            ally_position (Point | OrientedPoint): Position of an ally.
            enemy_position (Point | OrientedPoint): Position of an enemy.
        """
        super().update(team_color, ally_position, enemy_position)

        # Update accessibility to free if an ally or enemy is within the zone
        if (
                self.buffered_polygon.contains(ally_position)
                or self.buffered_polygon.contains(enemy_position)
        ) and self.accessibility != ZoneAccessibility:
            self._restrict_accessibility()
