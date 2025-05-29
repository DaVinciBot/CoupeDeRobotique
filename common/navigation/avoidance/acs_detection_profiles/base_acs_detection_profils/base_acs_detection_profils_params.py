from navigation.avoidance.acs_detection_profiles.struct import AcsDetectionProfile


class BaseAcsDetectionProfileParams:
    def __init__(self, acs_detection_profile: AcsDetectionProfile, acs_distance: float):
        self.acs_detection_profile: AcsDetectionProfile = acs_detection_profile
        self.acs_distance: float = acs_distance

    @classmethod
    def from_config(cls, acs_detection_profile: str, acs_distance: float):
        return cls(
            acs_detection_profile=AcsDetectionProfile[acs_detection_profile.upper()],
            acs_distance=acs_distance,
        )
