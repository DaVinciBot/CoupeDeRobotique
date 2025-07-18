# ====== Code Summary ======
# This module defines the NoAvoidance class, an implementation of the BaseAvoidance strategy
# used when no obstacle avoidance is required. It inherits from BaseAvoidance and simply
# returns the current trajectory command without performing any additional checks or logic.


from __future__ import annotations

from typing import TYPE_CHECKING

from navigation.avoidance.base_avoidance import BaseAvoidance
from navigation.avoidance.no_avoidance.no_avoidance_params import NoAvoidanceParams

if TYPE_CHECKING:
    from loggerplusplus import Logger

    from arena import AllyZone, EnemyZone
    from navigation.avoidance.acs_detection_profiles import (
        BaseAcsDetectionProfileParams,
    )
    from navigation.navigator.task.navigator_task import NavigatorTask
    from navigation.trajectory_planner import TrajectoryPlanCommand


class NoAvoidance(BaseAvoidance[NoAvoidanceParams]):
    """Implementation of a no-op avoidance strategy.

    The navigation system proceeds with its task without applying any obstacle
    avoidance logic and simply returns the current trajectory command unchanged.
    """

    def __init__(
        self,
        params: NoAvoidanceParams,
        acs_detection_profile_params: BaseAcsDetectionProfileParams,
        logger: Logger | None = None,
    ) -> None:
        """Initialize the no-avoidance strategy.

        Args:
            params (NoAvoidanceParams): Configuration parameters.
            acs_detection_profile_params (BaseAcsDetectionProfileParams):
                Parameters for the ACS detection profile.
            logger (Logger | None, optional): Logger instance for debugging. Defaults to None.
        """
        super().__init__(params, acs_detection_profile_params, logger)

    @BaseAvoidance._ensure_original_task_storage
    def handle(
        self,
        current_navigator_task: NavigatorTask,
        ally_zone: AllyZone,
        enemy_zone: EnemyZone,
    ) -> TrajectoryPlanCommand:
        """Handle method for no avoidance logic.

        Since this strategy does not perform any avoidance, it simply returns the current
        trajectory command as-is.

        Args:
            current_navigator_task (NavigatorTask): The current navigation task.
            ally_zone (AllyZone): Ally zone data.
            enemy_zone (EnemyZone): Enemy zone data.

        Returns:
            TrajectoryPlanCommand: The current trajectory command without changes.
        """
        return current_navigator_task.current_trajectory_command
