"""ACS detection profile implementations for obstacle avoidance.

The subpackage groups concrete detection profiles and factories used to
determine when an anti-collision system should trigger.
"""

from .acs_detection_profile_factory import (
    AcsDetectionProfileFactory,
)
from .angular_restrict_projection_acs_detection_profile import (
    AngularRestrictProjectionAcsDetectionProfile,
    AngularRestrictProjectionAcsDetectionProfileParams,
)
from .base_acs_detection_profiles import (
    BaseAcsDetectionProfile,
    BaseAcsDetectionProfileParams,
)
from .no_acs_detection_profile import (
    NoAcsDetectionProfile,
    NoAcsDetectionProfileParams,
)
from .no_projection_acs_detection_profile import (
    NoProjectionAcsDetectionProfile,
    NoProjectionAcsDetectionProfileParams,
)
from .rectangular_projection_acs_detection_profile import (
    RectangularProjectionAcsDetectionProfile,
    RectangularProjectionAcsDetectionProfileParams,
)
from .struct import AcsDetectionProfile

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
