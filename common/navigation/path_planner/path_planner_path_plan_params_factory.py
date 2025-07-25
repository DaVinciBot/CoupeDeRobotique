# ====== Code Summary ======
# This module defines a factory class ``PathPlannerPathPlanParamsFactory`` responsible for generating
# the appropriate path planning parameter objects based on the provided path planning strategy.
# It supports both the Delta and Basic strategies, returning instances of their corresponding
# parameter classes using the current and goal positions.

from geometry import OrientedPoint
from navigation.path_planner import (
    BasePathPlannerPlanPathParams,
    BasicPathPlannerPlanPathParams,
    DeltaPathPlannerPlanPathParams,
    PathPlanningStrategy,
)


class PathPlannerPathPlanParamsFactory:
    """Factory class for creating parameter objects used by different path planning strategies.

    This class abstracts the creation logic for strategy-specific plan path parameter objects,
    ensuring the correct parameters are instantiated based on the given path planning strategy.
    """

    @staticmethod
    def instantiate(
        strategy: PathPlanningStrategy,
        current_position: OrientedPoint,
        goal: OrientedPoint,
    ) -> BasePathPlannerPlanPathParams:
        """Generate the appropriate plan path parameter object based on the path planning strategy.

        Args:
            strategy (PathPlanningStrategy): Enum representing the chosen strategy (DELTA or BASIC).
            current_position (OrientedPoint): The starting position and orientation of the robot.
            goal (OrientedPoint): The desired goal position and orientation.

        Returns:
            BasePathPlannerPlanPathParams: An instance of the appropriate strategy's parameter class.

        Raises:
            ValueError: If an unsupported strategy is provided.
        """
        if strategy == PathPlanningStrategy.DELTA:
            # Create plan path params specific to Delta strategy
            return DeltaPathPlannerPlanPathParams(
                start=current_position,
            )

        if strategy == PathPlanningStrategy.BASIC:
            # Create plan path params specific to Basic strategy
            return BasicPathPlannerPlanPathParams(
                start=current_position,
                goal=goal,
            )

        # Raise an error if the strategy is not recognized
        raise ValueError(f"Unsupported path planning strategy: {strategy}")
