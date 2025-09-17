"""ACS detection profile implementations for obstacle avoidance.

The subpackage groups concrete detection profiles and factories used to
determine when an anti-collision system should trigger.
"""

from navigation.avoidance.acs_detection_profiles import (
    angular_restrict_projection_acs_detection_profile,
    base_acs_detection_profiles,
    no_acs_detection_profile,
    no_projection_acs_detection_profile,
    rectangular_projection_acs_detection_profile,
)
from navigation.avoidance.acs_detection_profiles.acs_detection_profile_factory import (
    AcsDetectionProfileFactory,
)
from navigation.avoidance.acs_detection_profiles.struct import (
    AcsDetectionProfile,
)

__all__ = [
    "AcsDetectionProfile",
    "AcsDetectionProfileFactory",
    "angular_restrict_projection_acs_detection_profile",
    "base_acs_detection_profiles",
    "no_acs_detection_profile",
    "no_projection_acs_detection_profile",
    "rectangular_projection_acs_detection_profile",
]
