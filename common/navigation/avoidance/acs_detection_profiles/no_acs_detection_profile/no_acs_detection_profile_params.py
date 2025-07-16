from navigation.avoidance.acs_detection_profiles.base_acs_detection_profils import (
    BaseAcsDetectionProfileParams,
)
from navigation.avoidance.acs_detection_profiles.struct import AcsDetectionProfile


class NoAcsDetectionProfileParams(BaseAcsDetectionProfileParams):
    def __init__(self, acs_distance: float = 0.0):
        super().__init__(
            acs_detection_profile=AcsDetectionProfile.NO,
            acs_distance=acs_distance,
        )
