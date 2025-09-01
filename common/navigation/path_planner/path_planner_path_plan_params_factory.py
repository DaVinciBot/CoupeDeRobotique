"""Factory to create plan parameters for path planners."""

from __future__ import annotations

from typing import TYPE_CHECKING

from navigation.path_planner.astar_path_planner import (
    AStarPathPlannerPlanPathParams,
)
from navigation.path_planner.basic_path_planner import (
    BasicPathPlannerPlanPathParams,
)
from navigation.path_planner.delta_path_planner import (
    DeltaPathPlannerPlanPathParams,
)
from navigation.path_planner.structs import PathPlanningStrategy

if TYPE_CHECKING:
    from geometry import OrientedPoint
    from navigation.path_planner.base_path_planner import (
        BasePathPlannerPlanPathParams,
    )


class PathPlannerPathPlanParamsFactory:
    """Factory class for creating parameter objects for each strategy."""

    @staticmethod
    def instantiate(
        strategy: PathPlanningStrategy,
        current_position: OrientedPoint,
        goal: OrientedPoint,
    ) -> BasePathPlannerPlanPathParams:
        """Generate plan-path parameters based on the strategy.

        Args:
            strategy (PathPlanningStrategy):
                Enum representing the chosen strategy (A_STAR, DELTA or BASIC).
            current_position (OrientedPoint):
                The starting position and orientation of the robot.
            goal (OrientedPoint): The desired goal position and orientation.

        Returns:
            BasePathPlannerPlanPathParams:
                An instance of the appropriate strategy's parameter class.

        Raises:
            ValueError: If an unsupported strategy is provided.

        """
        if strategy == PathPlanningStrategy.DELTA:
            return DeltaPathPlannerPlanPathParams(
                start=current_position,
            )

        if strategy == PathPlanningStrategy.BASIC:
            return BasicPathPlannerPlanPathParams(
                start=current_position,
                goal=goal,
            )

        if strategy == PathPlanningStrategy.A_STAR:
            return AStarPathPlannerPlanPathParams(
                start=current_position,
                goal=goal,
            )

        msg = f"Unsupported path planning strategy: {strategy}"
        raise ValueError(msg)
