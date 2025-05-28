from navigation.avoidance.acs_detection_profiles.base_acs_detection_profils import (
    BaseAcsDetectionProfile,
)

from navigation.avoidance.acs_detection_profiles.no_acs_detection_profile.no_acs_detection_profile_params import (
    NoAcsDetectionProfileParams,
)
from arena import AllyZone, EnemyZone


class NoAcsDetectionProfile(BaseAcsDetectionProfile[NoAcsDetectionProfileParams]):
    def __init__(self, params: NoAcsDetectionProfileParams):
        super().__init__(params)

    def is_acs_triggered(self, ally_zone: AllyZone, enemy_zone: EnemyZone) -> bool:
        return False
