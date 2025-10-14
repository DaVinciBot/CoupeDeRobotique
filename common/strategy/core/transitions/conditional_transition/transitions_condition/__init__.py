"""Predicates used by conditional transitions."""

from strategy.core.transitions.conditional_transition.transitions_condition import (
    base_transition_condition as _btc,
)
from strategy.core.transitions.conditional_transition.transitions_condition import (
    from_function_transition_condition as _fftc,
)
from strategy.core.transitions.conditional_transition.transitions_condition import (
    zone_accessibility_transition_condition as _zatc,
)

BaseTransitionCondition = _btc.BaseTransitionCondition
FromFunctionTransitionCondition = _fftc.FromFunctionTransitionCondition
ZoneAccessibilityTransitionCondition = _zatc.ZoneAccessibilityTransitionCondition

__all__ = [
    "BaseTransitionCondition",
    "FromFunctionTransitionCondition",
    "ZoneAccessibilityTransitionCondition",
]
