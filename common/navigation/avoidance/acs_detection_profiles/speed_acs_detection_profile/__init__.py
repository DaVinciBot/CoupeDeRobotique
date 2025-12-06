"""ACS detection profile using a rectangular projection."""

# ruff: noqa: E501

from navigation.avoidance.acs_detection_profiles.speed_acs_detection_profile import (
    speed_acs_detection_profile as _profile,
)
from navigation.avoidance.acs_detection_profiles.speed_acs_detection_profile import (
    speed_acs_detection_profile_params as _params,
)

SpeedAcsDetectionProfile = (
    _profile.SpeedAcsDetectionProfile
)
SpeedAcsDetectionProfileParams = (
    _params.SpeedAcsDetectionProfileParams
)

__all__ = [
    "SpeedAcsDetectionProfile",
    "SpeedAcsDetectionProfileParams",
]
