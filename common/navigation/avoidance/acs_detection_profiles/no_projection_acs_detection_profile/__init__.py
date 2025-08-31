"""ACS detection profile that ignores obstacle projection."""

from navigation.avoidance.acs_detection_profiles.no_projection_acs_detection_profile import (  # noqa: E501
    no_projection_acs_detection_profile as _profile,
)
from navigation.avoidance.acs_detection_profiles.no_projection_acs_detection_profile import (  # noqa: E501
    no_projection_acs_detection_profile_params as _params,
)

NoProjectionAcsDetectionProfile = _profile.NoProjectionAcsDetectionProfile
NoProjectionAcsDetectionProfileParams = _params.NoProjectionAcsDetectionProfileParams

__all__ = [
    "NoProjectionAcsDetectionProfile",
    "NoProjectionAcsDetectionProfileParams",
]
