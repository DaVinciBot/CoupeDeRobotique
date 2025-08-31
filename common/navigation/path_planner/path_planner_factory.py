"""Factory to instantiate the appropriate path planner."""

from __future__ import annotations

from typing import TYPE_CHECKING, cast

from navigation.path_planner.astar_path_planner import (
    AStarPathPlanner,
    AStarPathPlannerParams,
)
from navigation.path_planner.basic_path_planner import (
    BasicPathPlanner,
    BasicPathPlannerParams,
)
from navigation.path_planner.delta_path_planner import (
    DeltaPathPlanner,
    DeltaPathPlannerParams,
)
from navigation.path_planner.structs import PathPlanningStrategy

if TYPE_CHECKING:
    from navigation.path_planner.base_path_planner import (
        BasePathPlanner,
        BasePathPlannerParams,
    )


class PathPlannerFactory:
    """Instantiate the correct path planner based on the given parameters."""

    @staticmethod
    def instantiate(
        params: BasePathPlannerParams,
    ) -> BasePathPlanner:
        """Create a path planner based on the given parameters.

        This method inspects the ``path_finding_strategy`` attribute of the provided
        parameter object and returns an instance of the appropriate path planner class.
        It safely casts the parameter to the expected subclass before passing it
        to the respective path planner constructor.

        Args:
            params (BasePathPlannerParams): Configuration for the path planner,
                including the desired path planning strategy.

        Returns:
            BasePathPlanner: A specific implementation of the path planner,
                instantiated with the given parameters.

        Raises:
            ValueError: If the strategy specified in ``params`` is not supported.

        """
        strategy = params.path_finding_strategy

        if strategy == PathPlanningStrategy.DELTA:
            # Cast params to DeltaPathPlannerParams before instantiation
            return DeltaPathPlanner(cast("DeltaPathPlannerParams", params))

        if strategy == PathPlanningStrategy.BASIC:
            # Cast params to BasicPathPlannerParams before instantiation
            return BasicPathPlanner(cast("BasicPathPlannerParams", params))

        if strategy == PathPlanningStrategy.A_STAR:
            # Cast params to AStarPathPlannerParams before instantiation
            return AStarPathPlanner(cast("AStarPathPlannerParams", params))

        # Raise an error if the strategy is not recognized
        msg = f"Unsupported path planning strategy: {strategy}"
        raise ValueError(msg)
