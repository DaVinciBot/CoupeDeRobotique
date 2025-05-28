from navigation.avoidance.acs_detection_profiles.struct import AcsDetectionProfile


class BaseAcsDetectionProfileParams:

    def __init__(self, acs_detection_profile: AcsDetectionProfile, acs_distance: float):
        if isinstance(acs_detection_profile, str):
            acs_detection_profile: AcsDetectionProfile = AcsDetectionProfile(
                acs_detection_profile
            )
        else:
            self.acs_detection_profile: AcsDetectionProfile = acs_detection_profile
        self.acs_distance: float = acs_distance

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            acs_detection_profile=AcsDetectionProfile(data["acs_detection_profile"]),
            acs_distance=data["acs_distance"],
        )
