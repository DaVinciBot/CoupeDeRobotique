from math import atan2

from loggerplusplus import Logger

from arena import AllyZone, EnemyZone
from navigation.avoidance.acs_detection_profiles.angular_restrict_projection_acs_detection_profile.angular_restrict_projection_acs_detection_profile_params import (
    AngularRestrictProjectionAcsDetectionProfileParams,
)
from navigation.avoidance.acs_detection_profiles.base_acs_detection_profils import (
    BaseAcsDetectionProfile,
)


class AngularRestrictProjectionAcsDetectionProfile(
    BaseAcsDetectionProfile[AngularRestrictProjectionAcsDetectionProfileParams],
):
    def __init__(
        self,
        params: AngularRestrictProjectionAcsDetectionProfileParams,
        logger: Logger | None = None,
    ):
        super().__init__(params, logger)

    def is_acs_triggered(self, ally_zone: AllyZone, enemy_zone: EnemyZone) -> bool:
        angle = (
            atan2(
                enemy_zone.point.y - ally_zone.point.y,
                enemy_zone.point.x - ally_zone.point.x,
            )
            - ally_zone.point.theta
        )
        if abs(angle) <= self.params.half_angle_view:
            self.logger.info(
                f"ACS triggered. Distance: {ally_zone.point.distance(enemy_zone.point)}",
            )
            return True
        return False
