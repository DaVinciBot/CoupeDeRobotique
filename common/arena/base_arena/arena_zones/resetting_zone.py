"""Arena border zone definitions."""

from __future__ import annotations

from typing import TYPE_CHECKING

from arena.base_arena.arena_zones.base_arena_zone import BaseArenaZone
from arena.base_arena.arena_zones.structs import ZoneAccessibility, ZoneType

if TYPE_CHECKING:
    from collections.abc import Callable

    from loggerplusplus import Logger

    from geometry import Polygon


class ResettingZone(BaseArenaZone):
    """Represent the resetting zone of the arena, which is accessible."""

    def __init__(
        self,
        logger: Logger,
        buffer_size: float = 0.0,
        polygon: Polygon | None = None,
        buffered_polygon: Polygon | None = None,
        update_callback: Callable | None = None,
    ) -> None:
        """Initialize the border zone with geometry and accessibility.

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
        """
        super().__init__(
            logger=logger,
            zone_type=ZoneType.RESETTING_ZONE,
            accessibility=ZoneAccessibility.FREE,
            buffer_size=buffer_size,
            polygon=polygon,
            buffered_polygon=buffered_polygon,
            update_callback=update_callback,
            zone_color="#808080",
        )
