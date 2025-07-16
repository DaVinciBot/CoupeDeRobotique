from navigation.avoidance.acs_detection_profiles.base_acs_detection_profils import (
    BaseAcsDetectionProfileParams,
)
from navigation.avoidance.acs_detection_profiles.struct import AcsDetectionProfile


class NoProjectionAcsDetectionProfileParams(BaseAcsDetectionProfileParams):
    def __init__(self, acs_distance: float) -> None:
        super().__init__(
            acs_detection_profile=AcsDetectionProfile.NO_PROJECTION,
            acs_distance=acs_distance,
        )
