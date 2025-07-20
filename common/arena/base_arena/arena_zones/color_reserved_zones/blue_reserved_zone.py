# ====== Code Summary ======
# This module defines the BlueReservedZone class, a specialized zone restricted to the blue team.
# It inherits from BaseColorReservedZone and manages accessibility based on predefined conditions.

from collections.abc import Callable

from loggerplusplus import Logger

from arena.base_arena.arena_zones.color_reserved_zones.base_color_reserved_zone import (
    BaseColorReservedZone,
)
from arena.base_arena.arena_zones.structs import ZoneAccessibility, ZoneType
from arena.base_arena.team_color import TeamColor
from geometry import OrientedPoint, Point, Polygon


class BlueReservedZone(BaseColorReservedZone):
    """A reserved zone specifically for the blue team.
    This class ensures that only blue team members have access based on predefined conditions.
    """

    def __init__(
        self,
        logger: Logger,
        buffer_size: float = 0.0,
        polygon: Polygon | None = None,
        buffered_polygon: Polygon | None = None,
        update_callback: Callable | None = None,
        go_to_positions: list[OrientedPoint | Point] | None = None,
    ) -> None:
        """Initializes the BlueReservedZone with geometry and accessibility settings.

        Args:
            logger (Logger): Logger instance for logging messages.
            buffer_size (float, optional): Buffer size for geometric adjustments (defaults to 0.0).
            polygon (Polygon | None, optional): Polygon representing the zone geometry. Defaults to None.
            buffered_polygon (Polygon | None, optional): Buffered polygon geometry. Defaults to None.
            update_callback (Callable | None, optional): Function to be called on updates. Defaults to None.
            go_to_positions (list[OrientedPoint | Point] | None, optional): List of go-to positions within the zone. Defaults to None.
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
            go_to_positions=go_to_positions,
        )
