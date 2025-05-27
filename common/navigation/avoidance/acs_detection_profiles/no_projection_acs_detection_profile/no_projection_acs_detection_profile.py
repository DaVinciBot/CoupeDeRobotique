from navigation.avoidance.acs_detection_profiles.base_acs_detection_profils import (
    BaseAcsDetectionProfile,
)

from navigation.avoidance.acs_detection_profiles.no_projection_acs_detection_profile.no_projection_acs_detection_profile_params import (
    NoProjectionAcsDetectionProfileParams,
)
from arena import AllyZone, EnemyZone


class NoProjectionAcsDetectionProfile(
    BaseAcsDetectionProfile[NoProjectionAcsDetectionProfileParams]
):
    def __init__(self, params: NoProjectionAcsDetectionProfileParams):
        super().__init__(params)

    def is_acs_triggered(self, ally_zone: AllyZone, enemy_zone: EnemyZone) -> bool:
        return ally_zone.point.distance(enemy_zone.point) <= self.params.acs_distance
