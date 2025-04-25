# ====== Code Summary ======
# This module defines the BlueReservedZone class, a specialized zone restricted to the blue team.
# It inherits from BaseColorReservedZone and manages accessibility based on predefined conditions.

# ====== Imports ======
# Standard library imports
# ...

# Third-party imports
from loggerplusplus import Logger

# Local imports
from geometry import Polygon, Point, OrientedPoint

# Internal project imports
from arena.base_arena.arena_zones.structs import ZoneType, ZoneAccessibility
from arena.base_arena.arena_zones.color_reserved_zones.base_color_reserved_zone import BaseColorReservedZone
from arena.base_arena.team_color import TeamColor


# ====== Blue Reserved Zone Class ======
class BlueReservedZone(BaseColorReservedZone):
    """
    A reserved zone specifically for the blue team.
    This class ensures that only blue team members have access based on predefined conditions.
    """

    def __init__(
            self,
            logger: Logger,
            buffer_size: float = 0.0,
            polygon: Polygon = None,
            buffered_polygon: Polygon = None,
            update_callback: callable = None,
            go_to_positions: list[OrientedPoint | Point] = None
    ) -> None:
        """
        Initializes the BlueReservedZone with geometry and accessibility settings.

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
            zone_type=ZoneType.BLUE_RESERVED,
            color=TeamColor.BLUE,
            accessibility=ZoneAccessibility.RESTRICTED,
            buffer_size=buffer_size,
            polygon=polygon,
            buffered_polygon=buffered_polygon,
            update_callback=update_callback,
            zone_color="#097D8D",
            go_to_positions=go_to_positions
        )
