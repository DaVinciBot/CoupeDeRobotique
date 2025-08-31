"""No Projection ACS Detection Profile Parameters Module."""

from __future__ import annotations

from navigation.avoidance.acs_detection_profiles.base_acs_detection_profiles import (
    BaseAcsDetectionProfileParams,
)
from navigation.avoidance.acs_detection_profiles.struct import AcsDetectionProfile


class NoProjectionAcsDetectionProfileParams(BaseAcsDetectionProfileParams):
    """Parameters for the no projection ACS detection profile."""

    def __init__(self, acs_distance: float) -> None:
        """Initializes the NoProjectionAcsDetectionProfileParams.

        Args:
            acs_distance (float): Distance to the obstacle.

        """
        super().__init__(
            acs_detection_profile=AcsDetectionProfile.NO_PROJECTION,
            acs_distance=acs_distance,
        )
