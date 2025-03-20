# ====== Code Summary ======
# This module defines the BorderZone class, representing the outer boundaries of the arena.
# It extends BaseArenaZone and is characterized by its restricted accessibility.

# ====== Imports ======
# Standard library imports
# ...

# Third-party imports
from loggerplusplus import Logger

# Local imports
from geometry import Polygon

# Internal project imports
from arena.base_arena.arena_zones.structs import ZoneType, ZoneAccessibility
from arena.base_arena.arena_zones.base_arena_zone import BaseArenaZone


# ====== Border Zone Class ======
class BorderZone(BaseArenaZone):
    """
    Represents the border zone of the arena, which is typically inaccessible.
    This class defines the zone's geometry and ensures it remains restricted.

    Attributes:
        logger (Logger): Logger instance for logging messages.
        buffer_size (float): Buffer size for geometric adjustments.
        polygon (Polygon): Polygon representing the zone geometry.
        buffered_polygon (Polygon): Buffered polygon geometry.
        update_callback (callable): Function to be called on updates.
    """

    def __init__(
            self,
            logger: Logger,
            buffer_size: float = 0.0,
            polygon: Polygon = None,
            buffered_polygon: Polygon = None,
            update_callback: callable = None,
    ) -> None:
        """
        Initializes the BorderZone with its geometry and accessibility settings.

        Args:
            logger (Logger): Logger instance for logging messages.
            buffer_size (float, optional): Buffer size for geometric adjustments (defaults to 0.0).
            polygon (Polygon, optional): Polygon representing the zone geometry.
            buffered_polygon (Polygon, optional): Buffered polygon geometry.
            update_callback (callable, optional): Function to be called on updates.
        """
        super().__init__(
            logger=logger,
            zone_type=ZoneType.BORDER_ZONE,
            accessibility=ZoneAccessibility.FORBIDDEN,
            buffer_size=buffer_size,
            polygon=polygon,
            buffered_polygon=buffered_polygon,
            update_callback=update_callback,
            zone_color="#EF0D0D",
        )
