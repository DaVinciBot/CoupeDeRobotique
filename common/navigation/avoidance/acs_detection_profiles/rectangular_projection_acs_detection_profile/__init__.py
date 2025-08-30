"""ACS detection profile using a rectangular projection."""

from navigation.avoidance.acs_detection_profiles.rectangular_projection_acs_detection_profile import (
    rectangular_projection_acs_detection_profile as _profile,
)
from navigation.avoidance.acs_detection_profiles.rectangular_projection_acs_detection_profile import (
    rectangular_projection_acs_detection_profile_params as _params,
)

RectangularProjectionAcsDetectionProfile = (
    _profile.RectangularProjectionAcsDetectionProfile
)
RectangularProjectionAcsDetectionProfileParams = (
    _params.RectangularProjectionAcsDetectionProfileParams
)

__all__ = [
    "RectangularProjectionAcsDetectionProfile",
    "RectangularProjectionAcsDetectionProfileParams",
]
