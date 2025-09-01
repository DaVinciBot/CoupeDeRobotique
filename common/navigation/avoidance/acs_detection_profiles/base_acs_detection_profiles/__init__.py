"""Base classes for ACS detection profiles."""

# ruff: noqa: E501

from navigation.avoidance.acs_detection_profiles.base_acs_detection_profiles.base_acs_detection_profiles import (
    BaseAcsDetectionProfile,
)
from navigation.avoidance.acs_detection_profiles.base_acs_detection_profiles.base_acs_detection_profiles_params import (
    BaseAcsDetectionProfileParams,
)

__all__ = [
    "BaseAcsDetectionProfile",
    "BaseAcsDetectionProfileParams",
]
