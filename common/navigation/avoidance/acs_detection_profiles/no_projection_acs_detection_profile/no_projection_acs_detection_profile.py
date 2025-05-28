from navigation.avoidance.acs_detection_profiles.base_acs_detection_profils import (
    BaseAcsDetectionProfile,
)

from navigation.avoidance.acs_detection_profiles.no_projection_acs_detection_profile.no_projection_acs_detection_profile_params import (
    NoProjectionAcsDetectionProfileParams,
)
from arena import AllyZone, EnemyZone
from loggerplusplus import Logger


class NoProjectionAcsDetectionProfile(
    BaseAcsDetectionProfile[NoProjectionAcsDetectionProfileParams]
):
    def __init__(
        self,
        params: NoProjectionAcsDetectionProfileParams,
        logger: Logger | None = None,
    ):
        super().__init__(params, logger)

    def is_acs_triggered(self, ally_zone: AllyZone, enemy_zone: EnemyZone) -> bool:
        distance = ally_zone.point.distance(enemy_zone.point)
        if distance <= self.params.acs_distance:
            self.logger.info(f"ACS triggered. Distance: {distance}")
            return True
        return False
