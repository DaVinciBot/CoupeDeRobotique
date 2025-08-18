"""Core interfaces for path planners."""

import functools
from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import override

from loggerplusplus import Logger

from geometry import OrientedPoint
from navigation.path_planner.base_path_planner.base_path_planner_params import (
    BasePathPlannerParams,
    BasePathPlannerPlanPathParams,
)


class BasePathPlanner[
    PARAMSTYPE: BasePathPlannerParams,
    PLANPATHPARAMSTYPE: BasePathPlannerPlanPathParams,
](ABC):
    """Base class for all path planners."""

    def __init__(self, params: PARAMSTYPE, logger: Logger | None = None) -> None:
        """Initialize the BasePathPlanner.

        Args:
            params (PARAMSTYPE): The parameters for the path planner.
            logger (Logger | None, optional):
                Logger instance for debugging. Defaults to None.

        """
        self.logger: Logger = logger or Logger(
            identifier=self.__class__.__name__,
            follow_logger_manager_rules=True,
        )
        self.params: PARAMSTYPE = params
        self.last_plan_path_params: PLANPATHPARAMSTYPE | None = None

    @staticmethod
    def store_plan_path_params(
        method: Callable[..., list[OrientedPoint]],
    ) -> Callable[..., list[OrientedPoint]]:
        """Decorator storing the last parameters used to plan a path.

        Args:
            method (Callable[..., list[OrientedPoint]]): The method to wrap.

        Returns:
            Callable[..., list[OrientedPoint]]: Wrapped method storing parameters.

        """

        @functools.wraps(method)
        def wrapper(
            self: BasePathPlanner[PARAMSTYPE, PLANPATHPARAMSTYPE],
            plan_path_params: PLANPATHPARAMSTYPE,
        ) -> list[OrientedPoint]:
            self.last_plan_path_params = plan_path_params

            # Execute the method
            return method(self, plan_path_params)

        return wrapper

    @abstractmethod
    def plan_path(self, params: PLANPATHPARAMSTYPE) -> list[OrientedPoint]:
        """Abstract method to compute a path from start to goal.

        This method must be implemented by subclasses to define the specific
        path planning algorithm.

        Args:
            params (PLANPATHPARAMSTYPE):
                Parameters for path planning, including start and goal points.

        Returns:
            list[OrientedPoint]: A list of waypoints representing the planned path.

        """

    @override
    def __str__(self) -> str:
        """Returns a human-readable string representation of the path planner.

        Returns:
            str: String representation with class name and parameters.

        """
        return f"{self.__class__.__name__}({self.params})"

    @override
    def __repr__(self) -> str:
        """Returns an official string representation of the path planner.

        Returns:
            str: The same as ``__str__`` for consistency in debugging and logging.

        """
        return self.__str__()
