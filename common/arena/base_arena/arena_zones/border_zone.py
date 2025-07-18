# ====== Code Summary ======
# This module defines the BorderZone class, representing the outer boundaries of the arena.
# It extends BaseArenaZone and is characterized by its restricted accessibility.


from loggerplusplus import Logger

from arena.base_arena.arena_zones.base_arena_zone import BaseArenaZone
from arena.base_arena.arena_zones.structs import ZoneAccessibility, ZoneType
from geometry import Polygon


class BorderZone(BaseArenaZone):
    """Represents the border zone of the arena, which is typically inaccessible."""

    def __init__(
        self,
        logger: Logger,
        buffer_size: float = 0.0,
        polygon: Polygon | None = None,
        buffered_polygon: Polygon | None = None,
        update_callback: callable | None = None,
    ) -> None:
        """Initializes the BorderZone with its geometry and accessibility settings.

        Args:
            logger (Logger): Logger instance for logging messages.
            buffer_size (float, optional): Buffer size for geometric adjustments. Defaults to 0.0.
            polygon (Polygon | None, optional): Polygon representing the zone geometry. Defaults to None.
            buffered_polygon (Polygon | None, optional): Buffered polygon geometry. Defaults to None.
            update_callback (callable | None, optional): Function to be called on updates. Defaults to None.
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
