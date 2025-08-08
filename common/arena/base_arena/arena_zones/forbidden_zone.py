"""Strictly forbidden arena zone."""

from collections.abc import Callable

from loggerplusplus import Logger

from arena.base_arena.arena_zones.base_arena_zone import BaseArenaZone
from arena.base_arena.arena_zones.structs import ZoneAccessibility, ZoneType
from geometry import Polygon


class ForbiddenZone(BaseArenaZone):
    """Zone that is strictly forbidden."""

    def __init__(
        self,
        logger: Logger,
        accessibility: ZoneAccessibility = ZoneAccessibility.FORBIDDEN,
        buffer_size: float = 0.0,
        polygon: Polygon | None = None,
        buffered_polygon: Polygon | None = None,
        update_callback: Callable | None = None,
    ) -> None:
        """Initialize a ForbiddenZone with the specified parameters.

        Args:
            logger (Logger): Logger instance for logging messages.
            accessibility (ZoneAccessibility, optional): Accessibility of the
                zone. Defaults to ZoneAccessibility.FORBIDDEN.
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
            zone_type=ZoneType.FORBIDDEN,
            accessibility=accessibility,
            buffer_size=buffer_size,
            polygon=polygon,
            buffered_polygon=buffered_polygon,
            update_callback=update_callback,
            zone_color="#2b2b2b",
        )
