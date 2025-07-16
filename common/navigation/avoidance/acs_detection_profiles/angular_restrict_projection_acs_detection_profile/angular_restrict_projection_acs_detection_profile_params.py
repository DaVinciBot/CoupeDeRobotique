from navigation.avoidance.acs_detection_profiles.base_acs_detection_profils import (
    BaseAcsDetectionProfileParams,
)
from navigation.avoidance.acs_detection_profiles.struct import AcsDetectionProfile


class AngularRestrictProjectionAcsDetectionProfileParams(BaseAcsDetectionProfileParams):
    def __init__(self, acs_distance: float, angle_view: float) -> None:
        """Parameters for the Restrict Projection ACS Detection Profile.

        Args:
            acs_distance (float): The distance in centimeters for the ACS detection.
            angle_view (float): The angle view in radians for the ACS detection.
        """
        self.angle_view: float = angle_view
        self.half_angle_view: float = angle_view / 2

        super().__init__(
            acs_detection_profile=AcsDetectionProfile.ANGULAR_RESTRICT_PROJECTION,
            acs_distance=acs_distance,
        )
