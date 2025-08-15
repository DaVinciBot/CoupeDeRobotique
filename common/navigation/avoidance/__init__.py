"""Obstacle avoidance strategies and factory utilities.

This package exposes high-level interfaces to build avoidance behaviors.
"""

from navigation.avoidance.avoidance_factory import AvoidanceFactory  # noqa: I001
from navigation.avoidance.acs_detection_profiles import (
    BaseAcsDetectionProfile,
    BaseAcsDetectionProfileParams,
)
from navigation.avoidance.base_avoidance import (
    AvoidanceState,
    BaseAvoidance,
    BaseAvoidanceParams,
)
from navigation.avoidance.no_avoidance import NoAvoidance, NoAvoidanceParams
from navigation.avoidance.stop_and_wait_avoidance import (
    StopAndWaitAvoidance,
    StopAndWaitAvoidanceParams,
)
from navigation.avoidance.structs import AvoidanceStrategy

__all__ = [
    "AvoidanceFactory",
    "AvoidanceState",
    "AvoidanceStrategy",
    "BaseAcsDetectionProfile",
    "BaseAcsDetectionProfileParams",
    "BaseAvoidance",
    "BaseAvoidanceParams",
    "NoAvoidance",
    "NoAvoidanceParams",
    "StopAndWaitAvoidance",
    "StopAndWaitAvoidanceParams",
]
