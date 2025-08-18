"""Structures and enums for avoidance strategies."""

from enum import Enum, auto


class AvoidanceStrategy(Enum):
    """Available obstacle avoidance strategies."""

    NO_AVOIDANCE = auto()
    """No obstacle avoidance behavior is applied."""
    STOP_AND_WAIT = auto()
    """The robot stops and waits for a defined timeout before re-evaluating the situation."""  # noqa: E501
    BACK = auto()
    """The robot reverses its trajectory to avoid the obstacle."""
