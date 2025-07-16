# ====== Code Summary ======
# This module defines a factory class `PathPlannerFactory` that creates instances of different
# path planner classes based on a specified strategy in the provided parameters.
# It supports instantiation of `DeltaPathPlanner` and `BasicPathPlanner` using
# strongly-typed parameters for safe casting.

from typing import cast

from navigation.path_planner.base_path_planner import (
    BasePathPlanner,
    BasePathPlannerParams,
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

# TODO: implement AStarPathPlanner and add it to the factory
# from navigation.path_planner.astar_path_planner import (
#     AStarPathPlanner, AStarPathPlannerParams, AStarPathPlannerPlanPathParams
# )


class PathPlannerFactory:
    """Factory class to instantiate the appropriate path planner based on the provided parameters."""

    @staticmethod
    def instantiate(params: BasePathPlannerParams) -> BasePathPlanner:
        """Create a path planner based on the given parameters.

        This method inspects the `path_finding_strategy` attribute of the provided
        parameter object and returns an instance of the appropriate path planner class.
        It safely casts the parameter to the expected subclass before passing it
        to the respective path planner constructor.

        Args:
            params (BasePathPlannerParams): An instance containing configuration for the path planner,
                                            including the desired path planning strategy.

        Returns:
            BasePathPlanner: A specific implementation of the path planner, instantiated with the given parameters.

        Raises:
            ValueError: If the strategy specified in `params` is not supported.
        """
        strategy = params.path_finding_strategy

        if strategy == PathPlanningStrategy.DELTA:
            # Cast params to DeltaPathPlannerParams before instantiation
            return DeltaPathPlanner(cast("DeltaPathPlannerParams", params))

        if strategy == PathPlanningStrategy.BASIC:
            # Cast params to BasicPathPlannerParams before instantiation
            return BasicPathPlanner(cast("BasicPathPlannerParams", params))

        # Raise an error if the strategy is not recognized
        raise ValueError(f"Unsupported path planning strategy: {strategy}")
