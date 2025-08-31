"""No-op ACS detection profile.

Exports a profile that never triggers avoidance along with its parameters.
"""

from navigation.avoidance.acs_detection_profiles.no_acs_detection_profile.no_acs_detection_profile import (
    NoAcsDetectionProfile,
)
from navigation.avoidance.acs_detection_profiles.no_acs_detection_profile.no_acs_detection_profile_params import (
    NoAcsDetectionProfileParams,
)

__all__ = [
    "NoAcsDetectionProfile",
    "NoAcsDetectionProfileParams",
]
