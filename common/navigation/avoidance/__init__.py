"""Obstacle avoidance strategies and factory utilities.

This package exposes high-level interfaces to build avoidance behaviors.
"""

from navigation.avoidance import (
    acs_detection_profiles,
    back_avoidance,
    base_avoidance,
    no_avoidance,
    stop_and_wait_avoidance,
)
from navigation.avoidance.avoidance_factory import AvoidanceFactory
from navigation.avoidance.structs import AvoidanceStrategy

__all__ = [
    "AvoidanceFactory",
    "AvoidanceStrategy",
    "acs_detection_profiles",
    "back_avoidance",
    "base_avoidance",
    "no_avoidance",
    "stop_and_wait_avoidance",
]
