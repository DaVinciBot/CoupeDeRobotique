# ====== Code Summary ======
# This code defines an abstract base class `BasePathPlanner` for use in navigation systems.
# It establishes a common interface for all path planners, requiring implementation of the
# `plan_path` method. It also provides a basic string representation of any planner that inherits it.

import functools
from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from loggerplusplus import Logger

from geometry import OrientedPoint
from navigation.path_planner.base_path_planner.base_path_planner_params import (
    BasePathPlannerParams,
    BasePathPlannerPlanPathParams,
)

ParamsType = TypeVar("ParamsType", bound=BasePathPlannerParams)
PlanPathParamsType = TypeVar("PlanPathParamsType", bound=BasePathPlannerPlanPathParams)


class BasePathPlanner(ABC, Generic[ParamsType, PlanPathParamsType]):
    """Base class for all path planners."""

    def __init__(self, params: ParamsType, logger: Logger | None = None) -> None:
        """Initialize the BasePathPlanner.

        Args:
            params (ParamsType): The parameters for the path planner.
            logger (Logger | None, optional): Logger instance for debugging. Defaults to None.
        """
        self.logger: Logger = logger or Logger(
            identifier=self.__class__.__name__,
            follow_logger_manager_rules=True,
        )
        self.params: ParamsType = params
        self.last_plan_path_params: PlanPathParamsType | None = None

    @staticmethod
    def _store_plan_path_params(method: callable) -> callable:
        @functools.wraps(method)
        def wrapper(
            self: BasePathPlanner,
            plan_path_params: PlanPathParamsType,
            *args,
            **kwargs,
        ):
            self.last_plan_path_params = plan_path_params

            # Execute the method
            return method(self, plan_path_params, *args, **kwargs)

        return wrapper

    @abstractmethod
    def plan_path(self, params: PlanPathParamsType) -> list[OrientedPoint]:
        """Abstract method to compute a path from start to goal.

        This method must be implemented by subclasses to define the specific
        path planning algorithm.

        Args:
            params (PlanPathParamsType): Parameters for path planning, including start and goal points.

        Returns:
            list[OrientedPoint]: A list of waypoints representing the planned path.
        """
        ...

    def __str__(self) -> str:
        """Returns a human-readable string representation of the path planner.

        Returns:
            str: String representation with class name and parameters.
        """
        return f"{self.__class__.__name__}({self.params})"

    def __repr__(self) -> str:
        """Returns an official string representation of the path planner.

        Returns:
            str: The same as __str__ for consistency in debugging and logging.
        """
        return self.__str__()
