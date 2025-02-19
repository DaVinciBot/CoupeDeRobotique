# ====== Code Summary ======
# This module defines the ColorReservedZone class, which represents a restricted zone
# in an arena. The accessibility of this zone depends on a predefined team color. The class
# extends BaseArenaZone and dynamically updates zone accessibility based on detected enemy
# movement and team color conditions.

# ====== Imports ======
# Standard library imports
from typing import Callable, Union

# Third-party imports
from loggerplusplus import Logger

# Internal project imports
from geometry import Point, Polygon, OrientedPoint
from arena.base_arena.grid_manager import GridManager
from arena.base_arena.arena_zones.structs import ZoneType, ZoneAccessibility
from arena.base_arena.arena_zones.base_arena_zone import BaseArenaZone


# ====== Base Color Reserved Zone Class ======
class BaseColorReservedZone(BaseArenaZone):
    """
    Represents a zone restricted to a specific team color.
    The zone becomes accessible if the team's color matches the predefined color values.
    """

    def __init__(
            self,
            logger: Logger,
            zone_type: ZoneType,
            color: str,
            accessibility: ZoneAccessibility = ZoneAccessibility.RESTRICTED,
            buffer_size: float = 0.0,
            polygon: Polygon = None,
            buffered_polygon: Polygon = None,
            update_callback: Callable[[], GridManager] = None,
            zone_color: str = "#9e9e9e",
            go_to_positions: list[OrientedPoint | Point] = None
    ) -> None:
        """
        Initializes the ColorReservedZone.

        Args:
            logger (Logger): Logger instance for debugging and tracking.
            zone_type (ZoneType): Type of the zone.
            color (str): Primary color determining access.
            accessibility (ZoneAccessibility): Initial accessibility state of the zone.
            buffer_size (float): Size of the buffer for zone expansion.
            polygon (Polygon, optional): The base polygon defining the zone's shape.
            buffered_polygon (Polygon, optional): Buffered version of the polygon.
            update_callback (Callable, optional): Function to retrieve the GridManager instance.
            zone_color (str): Hex code representing the zone color.
            go_to_positions (list[OrientedPoint | Point], optional): List of go-to positions within the zone.
        """
        self.color_values: list[str] = [color.lower(), color[0].lower()]

        super().__init__(
            logger=logger,
            zone_type=zone_type,
            accessibility=accessibility,
            buffer_size=buffer_size,
            polygon=polygon,
            buffered_polygon=buffered_polygon,
            update_callback=update_callback,
            zone_color=zone_color,
            go_to_positions=go_to_positions
        )

    def _team_color_is_zone_color(self, team_color: str) -> bool:
        """
        Checks if the given team color matches the predefined zone colors.

        Args:
            team_color (str): The color assigned to the team.

        Returns:
            bool: True if the team color is allowed, False otherwise.
        """
        return team_color is not None and team_color.lower() in self.color_values

    def is_accessible(self, team_color: str = None) -> bool:
        """
        Determines if the zone is accessible based on the team color.

        Args:
            team_color (str, optional): The color assigned to the team.

        Returns:
            bool: True if the zone is accessible, False otherwise.
        """
        return super().is_accessible() and self._team_color_is_zone_color(team_color)

    def update(
            self, team_color: str, ally_position: Union[Point, OrientedPoint],
            enemy_position: Union[Point, OrientedPoint]
    ) -> None:
        """
        Updates the zone state based on detected enemy movement and team color validation.

        Args:
            team_color (str): The color assigned to the team.
            ally_position (Point | OrientedPoint): The position of the ally.
            enemy_position (Point | OrientedPoint): The position of the enemy.
        """
        super().update(team_color, ally_position, enemy_position)

        # Update accessibility based on team color
        if self.accessibility != ZoneAccessibility.FREE and self._team_color_is_zone_color(team_color):
            self.accessibility = ZoneAccessibility.FREE

            # Get grid manager from arena callback function
            grid_manager: GridManager = self.update_callback()
            grid_manager.remove_forbidden_static_zone(self.buffered_polygon)

            self.logger.debug(f"{self.zone_type} zone is now accessible")
