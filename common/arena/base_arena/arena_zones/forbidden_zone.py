# ====== Code Summary ======
# This module defines the ForbiddenZone class, which represents a strictly restricted zone within an arena.
# The class extends BaseArenaZone and ensures that access remains forbidden unless explicitly modified.


# ====== Imports ======
# Standard library imports
# ...

# Third-party imports
from loggerplusplus import Logger

# Internal project imports
from geometry import Polygon

from arena.base_arena.arena_zones.structs import ZoneType, ZoneAccessibility
from arena.base_arena.arena_zones.base_arena_zone import BaseArenaZone


# ====== Forbidden Zone Class ======
class ForbiddenZone(BaseArenaZone):
    """
    Zone that is strictly forbidden.

    Attributes:
        logger (Logger): Logger instance for logging messages.
        accessibility (ZoneAccessibility): Accessibility type of the zone (defaults to forbidden).
        buffer_size (float): Buffer size for geometric adjustments.
        polygon (Polygon): Polygon representing the zone geometry.
        buffered_polygon (Polygon): Buffered polygon geometry.
        update_callback (callable): Function to be called on updates.
    """

    def __init__(
            self,
            logger: Logger,
            accessibility: ZoneAccessibility = ZoneAccessibility.FORBIDDEN,
            buffer_size: float = 0.0,
            polygon: Polygon = None,
            buffered_polygon: Polygon = None,
            update_callback: callable = None,
    ) -> None:
        """
        Initializes a ForbiddenZone with the specified parameters.

        Args:
            logger (Logger): Logger instance for logging messages.
            accessibility (ZoneAccessibility): Accessibility of the zone.
            buffer_size (float): Buffer size for geometric adjustments.
            polygon (Polygon): Polygon representing the zone geometry.
            buffered_polygon (Polygon): Buffered polygon geometry.
            update_callback (callable): Function to be called on updates.
        """
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
