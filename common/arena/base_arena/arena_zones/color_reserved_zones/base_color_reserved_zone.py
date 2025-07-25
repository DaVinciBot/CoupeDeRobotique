# ====== Code Summary ======
# This module defines the ColorReservedZone class, which represents a restricted zone
# in an arena. The accessibility of this zone depends on a predefined team color. The class
# extends BaseArenaZone and dynamically updates zone accessibility based on detected enemy
# movement and team color conditions.


from collections.abc import Callable

from loggerplusplus import Logger

from arena.base_arena.arena_zones.base_arena_zone import BaseArenaZone
from arena.base_arena.arena_zones.structs import ZoneAccessibility, ZoneType
from arena.base_arena.grid_manager import GridManager
from arena.base_arena.team_color import TeamColor
from geometry import OrientedPoint, Point, Polygon


class BaseColorReservedZone(BaseArenaZone):
    """Represents a zone restricted to a specific team color.
    The zone becomes accessible if the team's color matches the predefined color values.

    """

    def __init__(
        self,
        logger: Logger,
        zone_type: ZoneType,
        color: TeamColor,
        accessibility: ZoneAccessibility = ZoneAccessibility.RESTRICTED,
        buffer_size: float = 0.0,
        polygon: Polygon | None = None,
        buffered_polygon: Polygon | None = None,
        update_callback: Callable[[], GridManager] | None = None,
        zone_color: str = "#9e9e9e",
        go_to_positions: list[OrientedPoint | Point] | None = None,
    ) -> None:
        """Initializes the ColorReservedZone.

        Args:
            logger (Logger): Logger instance for debugging and tracking.
            zone_type (ZoneType): Type of the zone.
            color (TeamColor): Primary color determining access.
            accessibility (ZoneAccessibility, optional): Initial accessibility state of the zone. Defaults to ZoneAccessibility.RESTRICTED.
            buffer_size (float, optional): Size of the buffer for zone expansion. Defaults to 0.0.
            polygon (Polygon | None, optional): The base polygon defining the zone's shape. Defaults to None.
            buffered_polygon (Polygon | None, optional): Buffered version of the polygon. Defaults to None.
            update_callback (Callable[[], GridManager] | None, optional):
                Function returning the grid manager instance. Defaults to None.
            zone_color (str, optional): Hex code representing the zone color. Defaults to "#9e9e9e".
            go_to_positions (list[OrientedPoint | Point] | None, optional): List of go-to positions within the zone. Defaults to None.

        """
        self.color: TeamColor = color

        super().__init__(
            logger=logger,
            zone_type=zone_type,
            accessibility=accessibility,
            buffer_size=buffer_size,
            polygon=polygon,
            buffered_polygon=buffered_polygon,
            update_callback=update_callback,
            zone_color=zone_color,
            go_to_positions=go_to_positions,
        )

    def is_accessible(self, team_color: TeamColor = TeamColor.UNDEFINED) -> bool:
        """Determines if the zone is accessible based on the team color.

        Args:
            team_color (TeamColor, optional): The color assigned to the team. Defaults to TeamColor.UNDEFINED.

        Returns:
            bool: ``True`` if the zone is accessible, ``False`` otherwise.

        """
        return super().is_accessible() and self.color == team_color

    def update(
        self,
        team_color: TeamColor,
        ally_position: Point | OrientedPoint,
        enemy_position: Point | OrientedPoint,
    ) -> None:
        """Updates the zone state based on detected enemy movement and team color validation.

        Args:
            team_color (TeamColor): The color assigned to the team.
            ally_position (Point | OrientedPoint): The position of the ally.
            enemy_position (Point | OrientedPoint): The position of the enemy.

        """
        super().update(team_color, ally_position, enemy_position)

        # Update accessibility based on team color
        if self.accessibility != ZoneAccessibility.FREE and self.color == team_color:
            self.accessibility = ZoneAccessibility.FREE

            # Get grid manager from arena callback function
            grid_manager: GridManager = self.update_callback()
            grid_manager.remove_forbidden_static_zone(self.buffered_polygon)

            self.logger.debug(f"{self.zone_type} zone is now accessible")
