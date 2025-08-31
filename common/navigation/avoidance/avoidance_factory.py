"""Factory for creating obstacle avoidance components based on strategy.

The factory inspects the provided parameters and returns the appropriate
``BaseAvoidance`` implementation. Supported strategies include "no avoidance",
"stop and wait", and "backward" avoidance.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, cast

from navigation.avoidance.back_avoidance.back_avoidance import BackAvoidance
from navigation.avoidance.no_avoidance.no_avoidance import NoAvoidance
from navigation.avoidance.stop_and_wait_avoidance.stop_and_wait_avoidance import (
    StopAndWaitAvoidance,
)
from navigation.avoidance.structs import AvoidanceStrategy

if TYPE_CHECKING:
    from navigation.avoidance.acs_detection_profiles import (
        BaseAcsDetectionProfileParams,
    )
    from navigation.avoidance.back_avoidance.back_avoidance_params import (
        BackAvoidanceParams,
    )
    from navigation.avoidance.base_avoidance.base_avoidance import (
        BaseAvoidance,
    )
    from navigation.avoidance.base_avoidance.base_avoidance_params import (
        BaseAvoidanceParams,
    )
    from navigation.avoidance.no_avoidance.no_avoidance_params import NoAvoidanceParams
    from navigation.avoidance.stop_and_wait_avoidance import StopAndWaitAvoidanceParams


class AvoidanceFactory:
    """Instantiate the appropriate obstacle avoidance component."""

    @staticmethod
    def instantiate(
        params: BaseAvoidanceParams,
        acs_detection_profile_params: BaseAcsDetectionProfileParams,
    ) -> BaseAvoidance:
        """Create an avoidance module based on the given parameters.

        Args:
            params (BaseAvoidanceParams): Parameters including the desired
                avoidance strategy.
            acs_detection_profile_params (BaseAcsDetectionProfileParams):
                Parameters for ACS detection profile.

        Returns:
            BaseAvoidance: A specific implementation of an obstacle avoidance module.

        Raises:
            ValueError: If the avoidance strategy is not supported.

        """
        strategy = params.avoidance_strategy

        if strategy == AvoidanceStrategy.NO_AVOIDANCE:
            return NoAvoidance(
                cast("NoAvoidanceParams", params),
                acs_detection_profile_params,
            )

        if strategy == AvoidanceStrategy.STOP_AND_WAIT:
            return StopAndWaitAvoidance(
                cast("StopAndWaitAvoidanceParams", params),
                acs_detection_profile_params,
            )

        if strategy == AvoidanceStrategy.BACK:
            return BackAvoidance(
                cast("BackAvoidanceParams", params),
                acs_detection_profile_params,
            )

        msg = f"Unsupported avoidance strategy: {strategy}"
        raise ValueError(msg)
