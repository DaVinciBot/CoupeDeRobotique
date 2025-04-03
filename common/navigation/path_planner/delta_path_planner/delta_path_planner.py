# ====== Code Summary ======
# This module defines the `DeltaPathPlanner`, a path planner that creates a path by applying a linear
# displacement and/or angular rotation relative to the starting point. It is useful for incremental
# motion planning in local navigation scenarios.

# ====== Imports ======
# Standard library imports
import math

# Third-party imports
from loggerplusplus import Logger

# Local imports
from geometry import OrientedPoint

# Internal project imports
from navigation.path_planner.base_path_planner.base_path_planner import BasePathPlanner
from navigation.path_planner.delta_path_planner.delta_path_planner_params import DeltaPathPlannerParams


class DeltaPathPlanner(BasePathPlanner):
    """
    Path planner that applies a relative displacement and rotation to the start position.

    Generates a two-point path based on linear distance and rotational delta.
    """

    def __init__(self, params: DeltaPathPlannerParams, logger: Logger | None = None) -> None:
        """
        Initialize the delta path planner.

        Args:
            params (DeltaPathPlannerParams): Parameters for delta-based path planning.
            logger (Logger | None): Optional logger.
        """
        super().__init__(params, logger)

    @staticmethod
    def _compute_displacement(start: OrientedPoint, distance: float) -> tuple[float, float]:
        """
        Compute the displacement vector from the start point.

        Args:
            start (OrientedPoint): Starting pose.
            distance (float): Distance to move forward.

        Returns:
            tuple[float, float]: (dx, dy) displacement.
        """
        return (
            distance * math.cos(start.theta),  # dx
            distance * math.sin(start.theta)  # dy
        )

    @staticmethod
    def _compute_rotation(start: OrientedPoint, rotation: float) -> float:
        """
        Compute the final orientation after applying rotation.

        Args:
            start (OrientedPoint): Starting pose.
            rotation (float): Rotation to apply.

        Returns:
            float: Final orientation angle.
        """
        return (start.theta + rotation) % (2 * math.pi)

    def plan_path(self, start: OrientedPoint, distance: float = 0.0, rotation: float = 0.0) -> list[OrientedPoint]:
        """
        Generate a path from the start point using relative displacement and rotation.

        Args:
            start (OrientedPoint): Starting pose.
            distance (float): Distance to move forward.
            rotation (float): Rotation to apply at the end.

        Returns:
            list[OrientedPoint]: List containing the start and resulting goal pose.
        """
        x, y, theta = start.x, start.y, start.theta

        # 1. Apply displacement
        if distance != 0.0:
            dx, dy = self._compute_displacement(start, distance)
            x += dx
            y += dy

        # 2. Apply rotation
        if rotation != 0.0:
            theta = self._compute_rotation(start, rotation)

        return [
            start,
            OrientedPoint(x, y, theta)
        ]
