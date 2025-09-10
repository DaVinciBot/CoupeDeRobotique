"""Parameters for the delta path planner."""

from __future__ import annotations

from navigation.path_planner.base_path_planner.base_path_planner_params import (
    BasePathPlannerParams,
    BasePathPlannerPlanPathParams,
)
from navigation.path_planner.structs import PathPlanningStrategy


class DeltaPathPlannerParams(BasePathPlannerParams):
    """Parameter class for DeltaPathPlanner.

    Initializes the path finding strategy as DELTA.

    """

    def __init__(self, distance: float = 0.0, rotation: float = 0.0) -> None:
        """Initialize delta-based path planner parameters with DELTA strategy.

        Args:
            distance (float, optional): Distance to travel. Defaults to 0.0.
            rotation (float, optional): Rotation to apply. Defaults to 0.0.

        """
        self.distance: float = distance
        self.rotation: float = rotation
        super().__init__(PathPlanningStrategy.DELTA)


class DeltaPathPlannerPlanPathParams(BasePathPlannerPlanPathParams):
    """Parameters for the delta path planner."""
