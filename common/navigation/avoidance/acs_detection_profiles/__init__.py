"""ACS detection profile implementations for obstacle avoidance.

The subpackage groups concrete detection profiles and factories used to
determine when an anti-collision system should trigger.
"""

from navigation.avoidance.acs_detection_profiles.acs_detection_profile_factory import (
    AcsDetectionProfileFactory,
)
from navigation.avoidance.acs_detection_profiles.angular_restrict_projection_acs_detection_profile import (
    AngularRestrictProjectionAcsDetectionProfile,
    AngularRestrictProjectionAcsDetectionProfileParams,
)
from navigation.avoidance.acs_detection_profiles.base_acs_detection_profiles import (
    BaseAcsDetectionProfile,
    BaseAcsDetectionProfileParams,
)
from navigation.avoidance.acs_detection_profiles.no_acs_detection_profile import (
    NoAcsDetectionProfile,
    NoAcsDetectionProfileParams,
)
from navigation.avoidance.acs_detection_profiles.no_projection_acs_detection_profile import (
    NoProjectionAcsDetectionProfile,
    NoProjectionAcsDetectionProfileParams,
)
from navigation.avoidance.acs_detection_profiles.rectangular_projection_acs_detection_profile import (
    RectangularProjectionAcsDetectionProfile,
    RectangularProjectionAcsDetectionProfileParams,
)
from navigation.avoidance.acs_detection_profiles.struct import (
    AcsDetectionProfile,
)

__all__ = [
    "AcsDetectionProfile",
    "AcsDetectionProfileFactory",
    "AngularRestrictProjectionAcsDetectionProfile",
    "AngularRestrictProjectionAcsDetectionProfileParams",
    "BaseAcsDetectionProfile",
    "BaseAcsDetectionProfileParams",
    "NoAcsDetectionProfile",
    "NoAcsDetectionProfileParams",
    "NoProjectionAcsDetectionProfile",
    "NoProjectionAcsDetectionProfileParams",
    "RectangularProjectionAcsDetectionProfile",
    "RectangularProjectionAcsDetectionProfileParams",
]
