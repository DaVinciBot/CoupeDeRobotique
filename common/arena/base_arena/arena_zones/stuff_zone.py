# ====== Code Summary ======
# This module defines the StuffZone class, a zone designated for storage or item placement.
# It extends BaseArenaZone and updates its accessibility based on the presence of allies or enemies.

# ====== Imports ======
# Standard library imports
# ...

# Third-party imports
from loggerplusplus import Logger

# Local imports
from geometry import (
    Point,
    Polygon,
    OrientedPoint,
)

# Internal project imports
from arena.base_arena.grid_manager import GridManager
from arena.base_arena.arena_zones.structs import ZoneType, ZoneAccessibility
from arena.base_arena.arena_zones.base_arena_zone import BaseArenaZone
from arena.base_arena.team_color import TeamColor


# ====== Stuff Zone Part ======
class StuffZone(BaseArenaZone):
    """
    Zone designated for storage or placement of items.

    Attributes:
        logger (Logger): Logger instance for logging messages.
        accessibility (ZoneAccessibility): Accessibility type of the zone (defaults to restricted).
        buffer_size (float): Buffer size for geometric adjustments.
        polygon (Polygon): Polygon representing the zone geometry.
        buffered_polygon (Polygon): Buffered polygon geometry.
        update_callback (callable): Function to be called on updates.
        index (int): Index identifier for the StuffZone.
    """

    def __init__(
        self,
        logger: Logger,
        buffer_size: float = 0.0,
        polygon: Polygon = None,
        buffered_polygon: Polygon = None,
        update_callback: callable = None,
        go_to_positions: list[OrientedPoint | Point] = None,
    ) -> None:
        """
        Initializes the StuffZone with geometry, buffer, and accessibility.

        Args:
            logger (Logger): Logger instance for logging messages.
            buffer_size (float, optional): Buffer size for geometric adjustments (defaults to 0.0).
            polygon (Polygon, optional): Polygon representing the zone geometry.
            buffered_polygon (Polygon, optional): Buffered polygon geometry.
            update_callback (callable, optional): Function to be called on updates.
            go_to_positions (list[OrientedPoint | Point], optional): List of go-to positions within the zone.
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

    def update(
        self,
        team_color: TeamColor,
        ally_position: Point | OrientedPoint,
        enemy_position: Point | OrientedPoint,
    ) -> None:
        """
        Updates the zone accessibility based on the positions of allies and enemies.

        Args:
            team_color (TeamColor): The color of the team.
            ally_position (Point | OrientedPoint): Position of an ally.
            enemy_position (Point | OrientedPoint): Position of an enemy.
        """
        super().update(team_color, ally_position, enemy_position)

        # Update accessibility to free if an ally or enemy is within the zone
        if self.buffered_polygon.contains(
            ally_position
        ) or self.buffered_polygon.contains(enemy_position):
            self.accessibility = ZoneAccessibility.FREE
            grid_manager: GridManager = self.update_callback()
            grid_manager.remove_forbidden_static_zone(self.buffered_polygon)

            self.logger.debug(f"{self.zone_type} zone is now accessible")

    def get_go_to_position(
        self, ally_position: OrientedPoint, team_color: TeamColor
    ) -> OrientedPoint | Point | None:
        """
        Determines the best go-to position for an ally in the given zone.

        Args:
            ally_position (OrientedPoint): The position of the ally.
            team_color (TeamColor): The team color to check accessibility.

        Returns:
            OrientedPoint | Point | None: The best go-to position, or None if the zone is not accessible.
        """
        # If no go-to positions are defined, return the centroid of the zone
        if self.go_to_positions is None:
            self.logger.debug(
                f"GoTo position request: No go-to positions defined for zone {self.zone_type}, "
                f"returning centroid [{self.polygon.centroid}]"
            )
            return self.polygon.centroid

        # Find the nearest go-to position to the ally if positions are available
        if self.go_to_positions:
            nearest_position = min(
                self.go_to_positions, key=lambda p: ally_position.distance(p)
            )
            self.logger.debug(
                f"GoTo position request: Nearest go-to position to ally [{ally_position}] is [{nearest_position}]"
            )
            return nearest_position

        self.logger.debug(
            "GoTo position request: Unknown case encountered, returning None."
        )
        return None
