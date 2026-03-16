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
from strategy.core.transitions.conditional_transition.transitions_condition import (
    zone_id_accessibility_transition_condition as _zidac,
)

BaseTransitionCondition = _btc.BaseTransitionCondition
FromFunctionTransitionCondition = _fftc.FromFunctionTransitionCondition
ZoneAccessibilityTransitionCondition = _zatc.ZoneAccessibilityTransitionCondition
ZoneIdAccessibilityTransitionCondition = _zidac.ZoneIdAccessibilityTransitionCondition

__all__ = [
    "BaseTransitionCondition",
    "FromFunctionTransitionCondition",
    "ZoneAccessibilityTransitionCondition",
    "ZoneIdAccessibilityTransitionCondition",
]
