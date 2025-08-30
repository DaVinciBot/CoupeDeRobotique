"""Enemy zone with automatic speed vector calculation."""

from loggerplusplus import Logger

from arena.base_arena.arena_zones.speed_vector_auto_calculate_zones import (
    base_speed_vector_auto_calculate_zone as _base_zone,
)
from arena.base_arena.arena_zones.structs import ZoneAccessibility, ZoneType
from geometry import OrientedPoint, Point


class EnemyZone(_base_zone.BaseSpeedVectorAutoCalculateZone):
    """Represents an enemy zone in the arena where enemy movements are tracked.

    The zone calculates and updates a speed vector based on detected enemy positions.

    """

    def __init__(
        self,
        logger: Logger,
        point: Point | OrientedPoint,
        robot_size: float = 10,
        positions_record_size: int = 3,
        no_detection_timeout: float = 4.0,
        vector_factor: float = 25.0,
    ) -> None:
        """Initialize an ``EnemyZone`` with given parameters.

        Args:
            logger (Logger): Logger instance for debugging.
            point (Point | OrientedPoint): The central point of the enemy zone.
            robot_size (float, optional): The assumed size of the robot. Defaults to 10.
            positions_record_size (int, optional):
                Maximum number of recorded positions. Defaults to 3.
            no_detection_timeout (float, optional):
                Timeout for detecting no movement. Defaults to 4.0.
            vector_factor (float, optional):
                Scaling factor for speed vector influence. Defaults to 25.0.

        """
        super().__init__(
            logger=logger,
            zone_type=ZoneType.ENEMY,
            accessibility=ZoneAccessibility.FORBIDDEN,
            point=point,
            vector_width=robot_size,
            buffer_size=0.0,
            update_callback=None,
            zone_color="#EE0505",
            positions_record_size=positions_record_size,
            no_detection_timeout=no_detection_timeout,
            vector_factor=vector_factor,
        )
