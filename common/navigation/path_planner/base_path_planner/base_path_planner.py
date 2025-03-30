# ====== Code Summary ======
# This code defines an abstract base class `BasePathPlanner` for use in navigation systems.
# It establishes a common interface for all path planners, requiring implementation of the
# `plan_path` method. It also provides a basic string representation of any planner that inherits it.

# ====== Imports ======
# Standard library imports
from abc import ABC, abstractmethod
from typing import Generic, TypeVar

# Third-party imports
from loggerplusplus import Logger

# Local imports
from geometry import OrientedPoint

# Internal project imports
from navigation.path_planner.base_path_planner.base_path_planner_params import BasePathPlannerParams

# ====== Type Hint ======
ParamsType = TypeVar("ParamsType", bound=BasePathPlannerParams)


# ====== Base Path Planner Class ======
class BasePathPlanner(ABC, Generic[ParamsType]):
    def __init__(self, params: ParamsType, logger: Logger | None = None) -> None:
        if logger is None:
            logger = Logger(identifier=self.__class__.__name__, follow_logger_manager_rules=True)

        self.logger: Logger = logger
        self.params: ParamsType = params

    @abstractmethod
    def plan_path(self, start: OrientedPoint, **kwargs) -> list[OrientedPoint]:
        """
        Abstract method to compute a path from start to goal.

        This method must be implemented by subclasses to define the specific
        path planning algorithm.

        Args:
            start (OrientedPoint): The starting position and orientation.
            **kwargs: Additional arguments that specific planners may require.

        Returns:
            list[OrientedPoint]: A list of waypoints representing the planned path.
        """
        ...

    def __str__(self) -> str:
        """
        Returns a human-readable string representation of the path planner.

        Returns:
            str: String representation with class name and parameters.
        """
        return f"{self.__class__.__name__}({self.params})"

    def __repr__(self) -> str:
        """
        Returns an official string representation of the path planner.

        Returns:
            str: The same as __str__ for consistency in debugging and logging.
        """
        return self.__str__()
