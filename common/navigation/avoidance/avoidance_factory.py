# ====== Code Summary ======
# This module defines a factory class `AvoidanceFactory` that creates instances of different
# obstacle avoidance modules based on the specified strategy in the provided parameters.
# It currently supports instantiation of `StopAndWaitAvoidance`.

# ====== Standard Library Imports ======
from typing import cast

# ====== Internal Project Imports ======
from navigation.avoidance.structs import AvoidanceStrategy
from navigation.avoidance.base_avoidance import (
    BaseAvoidance,
    BaseAvoidanceParams,
)
from navigation.avoidance.stop_and_wait_avoidance import (
    StopAndWaitAvoidance,
    StopAndWaitAvoidanceParams,
)


class AvoidanceFactory:
    """
    Factory class to instantiate the appropriate obstacle avoidance component based on strategy.
    """

    @staticmethod
    def instantiate(params: BaseAvoidanceParams) -> BaseAvoidance:
        """
        Create an avoidance module based on the given parameters.

        Args:
            params (BaseAvoidanceParams): Parameters including the desired avoidance strategy.

        Returns:
            BaseAvoidance: A specific implementation of an obstacle avoidance module.

        Raises:
            ValueError: If the avoidance strategy is not supported.
        """
        strategy = params.avoidance_strategy

        if strategy == AvoidanceStrategy.STOP_AND_WAIT:
            return StopAndWaitAvoidance(cast(StopAndWaitAvoidanceParams, params))

        raise ValueError(f"Unsupported avoidance strategy: {strategy}")
