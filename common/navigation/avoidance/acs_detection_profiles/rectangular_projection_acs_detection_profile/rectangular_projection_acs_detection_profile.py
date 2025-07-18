import math

from loggerplusplus import Logger

from arena import AllyZone, EnemyZone
from geometry import Polygon, rotate, translate
from navigation.avoidance.acs_detection_profiles.base_acs_detection_profils import (
    BaseAcsDetectionProfile,
)
from navigation.avoidance.acs_detection_profiles.rectangular_projection_acs_detection_profile.rectangular_projection_acs_detection_profile_params import (
    RectangularProjectionAcsDetectionProfileParams,
)


class RectangularProjectionAcsDetectionProfile(
    BaseAcsDetectionProfile[RectangularProjectionAcsDetectionProfileParams],
):
    """Rectangular projection ACS detection profile."""

    def __init__(
        self,
        params: RectangularProjectionAcsDetectionProfileParams,
        logger: Logger | None = None,
    ) -> None:
        """Initializes the RectangularProjectionAcsDetectionProfile.

        Args:
            params (RectangularProjectionAcsDetectionProfileParams): Parameters for the rectangular projection ACS detection profile.
            logger (Logger | None, optional): Logger instance for debugging. Defaults to None.
        """
        super().__init__(params, logger)

    def _create_rectangular_projection(self, ally_zone: AllyZone) -> Polygon:
        rectangle = Polygon(
            [
                (-self.params.half_length_view, -self.params.half_width_view),
                (+self.params.half_length_view, -self.params.half_width_view),
                (+self.params.half_length_view, +self.params.half_width_view),
                (-self.params.half_length_view, +self.params.half_width_view),
            ],
        )
        rotated_rectangle = rotate(
            rectangle,
            ally_zone.point.theta,
            origin=(0, 0),
            use_radians=True,
        )

        dx = ally_zone.point.x + self.params.half_length_view * math.cos(
            ally_zone.point.theta,
        )
        dy = ally_zone.point.y + self.params.half_length_view * math.sin(
            ally_zone.point.theta,
        )
        return translate(rotated_rectangle, xoff=dx, yoff=dy)

    def is_acs_triggered(self, ally_zone: AllyZone, enemy_zone: EnemyZone) -> bool:
        projection = self._create_rectangular_projection(ally_zone)
        if projection.contains(enemy_zone.point):
            self.logger.info(
                f"ACS triggered. Distance: {ally_zone.point.distance(enemy_zone.point)}",
            )
            return True
        return False
