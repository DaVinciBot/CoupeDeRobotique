"""Obstacle avoidance strategies and factory utilities.

This package exposes high-level interfaces to build avoidance behaviors.
"""

from navigation.avoidance.acs_detection_profiles import (
    BaseAcsDetectionProfile,
    BaseAcsDetectionProfileParams,
)
from navigation.avoidance.base_avoidance.base_avoidance import BaseAvoidance
from navigation.avoidance.base_avoidance.base_avoidance_params import (
    BaseAvoidanceParams,
)
from navigation.avoidance.base_avoidance.states import AvoidanceState
from navigation.avoidance.no_avoidance.no_avoidance import NoAvoidance
from navigation.avoidance.no_avoidance.no_avoidance_params import NoAvoidanceParams
from navigation.avoidance.stop_and_wait_avoidance.stop_and_wait_avoidance import (
    StopAndWaitAvoidance,
)
from navigation.avoidance.stop_and_wait_avoidance.stop_and_wait_avoidance_params import (
    StopAndWaitAvoidanceParams,
)
from navigation.avoidance.structs import AvoidanceStrategy

__all__ = [
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
