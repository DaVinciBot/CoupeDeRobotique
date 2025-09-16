"""Parameters for the angular restrict projection ACS detection profile.

Defines the viewing angle and distance used to trigger the avoidance system.
"""

from __future__ import annotations

from navigation.avoidance.acs_detection_profiles.base_acs_detection_profiles import (
    BaseAcsDetectionProfileParams,
)
from navigation.avoidance.acs_detection_profiles.struct import AcsDetectionProfile


class AngularRestrictProjectionAcsDetectionProfileParams(BaseAcsDetectionProfileParams):
    """Parameters for the angular restrict projection ACS detection profile."""

    def __init__(self, acs_distance: float, angle_view: float) -> None:
        """Initializes the AngularRestrictProjectionAcsDetectionProfileParams.

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
