"""Zone reserved exclusively for the yellow team."""

from __future__ import annotations

from typing import TYPE_CHECKING

from arena.base_arena.arena_zones.color_reserved_zones.base_color_reserved_zone import (
    BaseColorReservedZone,
)
from arena.base_arena.arena_zones.structs import ZoneAccessibility, ZoneType
from arena.base_arena.team_color import TeamColor

if TYPE_CHECKING:
    from collections.abc import Callable

    from loggerplusplus import Logger

    from geometry import OrientedPoint, Point, Polygon


class YellowReservedZone(BaseColorReservedZone):
    """Reserved zone specifically for the yellow team.

    Only yellow team members have access based on predefined conditions.

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
        """Initialize the YellowReservedZone with geometry and accessibility.

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
            go_to_positions (list[OrientedPoint | Point] | None, optional):
                List of go-to positions within the zone. Defaults to None.

        """
        super().__init__(
            logger=logger,
            zone_type=ZoneType.YELLOW_RESERVED,
            color=TeamColor.YELLOW,
            accessibility=ZoneAccessibility.RESTRICTED,
            buffer_size=buffer_size,
            polygon=polygon,
            buffered_polygon=buffered_polygon,
            update_callback=update_callback,
            zone_color="#ECC92E",
            go_to_positions=go_to_positions,
        )
