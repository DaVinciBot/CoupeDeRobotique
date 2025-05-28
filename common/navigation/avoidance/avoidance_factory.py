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
from navigation.avoidance.no_avoidance import (
    NoAvoidance,
    NoAvoidanceParams,
)
from navigation.avoidance.stop_and_wait_avoidance import (
    StopAndWaitAvoidance,
    StopAndWaitAvoidanceParams,
)

from navigation.avoidance.back_avoidance import (
    BackAvoidance,
    BackAvoidanceParams,
)

from navigation.avoidance.acs_detection_profiles import BaseAcsDetectionProfileParams


class AvoidanceFactory:
    """
    Factory class to instantiate the appropriate obstacle avoidance component based on strategy.
    """

    @staticmethod
    def instantiate(
        params: BaseAvoidanceParams,
        acs_detection_profile_params: BaseAcsDetectionProfileParams,
    ) -> BaseAvoidance:
        """
        Create an avoidance module based on the given parameters.

        Args:
            params (BaseAvoidanceParams): Parameters including the desired avoidance strategy.
            acs_detection_profile_params (BaseAcsDetectionProfileParams): Parameters for ACS detection profile.

        Returns:
            BaseAvoidance: A specific implementation of an obstacle avoidance module.

        Raises:
            ValueError: If the avoidance strategy is not supported.
        """
        strategy = params.avoidance_strategy

        if strategy == AvoidanceStrategy.NO_AVOIDANCE:
            return NoAvoidance(
                cast(NoAvoidanceParams, params), acs_detection_profile_params
            )

        if strategy == AvoidanceStrategy.STOP_AND_WAIT:
            return StopAndWaitAvoidance(
                cast(StopAndWaitAvoidanceParams, params), acs_detection_profile_params
            )

        if strategy == AvoidanceStrategy.BACK:
            return BackAvoidance(
                cast(BackAvoidanceParams, params),
                acs_detection_profile_params,
            )

        raise ValueError(f"Unsupported avoidance strategy: {strategy}")
