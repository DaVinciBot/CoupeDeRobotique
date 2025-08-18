"""Factory for building trajectory planners from parameters."""

from __future__ import annotations

from typing import TYPE_CHECKING, cast

from navigation.trajectory_planner.sequential_trajectory_planner import (
    SequentialTrajectoryPlanner,
    SequentialTrajectoryPlannerParams,
)
from navigation.trajectory_planner.structs import TrajectoryPlannerStrategy

if TYPE_CHECKING:
    from navigation.trajectory_planner.base_trajectory_planner import (
        BaseTrajectoryPlanner,
        BaseTrajectoryPlannerParams,
    )
    from navigation.trajectory_planner.speed_profile.speed_profiler import SpeedProfiler


class TrajectoryPlannerFactory:
    """Instantiate the appropriate trajectory planner based on parameters."""

    @staticmethod
    def instantiate(
        params: BaseTrajectoryPlannerParams,
        speed_profiler: SpeedProfiler,
    ) -> BaseTrajectoryPlanner:
        """Create a trajectory planner based on the given parameters.

        This method inspects the ``trajectory_planning_strategy`` attribute of
        the provided parameter object and returns an instance of the appropriate
        trajectory planner class.
        It safely casts the parameter to the expected subclass before passing it
        to the respective trajectory planner constructor.

        Args:
            params (BaseTrajectoryPlannerParams):
                Configuration including strategy type.
            speed_profiler (SpeedProfiler):
                An object used to compute velocity profiles during trajectory planning.

        Returns:
            BaseTrajectoryPlanner: A specific implementation of the trajectory planner.

        Raises:
            ValueError: If the strategy specified in ``params`` is not supported.

        """
        strategy = params.trajectory_planning_strategy

        if strategy == TrajectoryPlannerStrategy.SEQUENTIAL:
            return SequentialTrajectoryPlanner(
                cast("SequentialTrajectoryPlannerParams", params),
                speed_profiler,
            )

        msg = f"Unsupported trajectory planning strategy: {strategy}"
        raise ValueError(msg)
