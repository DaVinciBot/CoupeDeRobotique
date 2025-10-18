"""Path planner applying relative displacement and rotation."""

from __future__ import annotations

import math

from geometry import OrientedPoint
from navigation.path_planner.base_path_planner.base_path_planner import BasePathPlanner
from navigation.path_planner.delta_path_planner.delta_path_planner_params import (
    DeltaPathPlannerParams,
    DeltaPathPlannerPlanPathParams,
)

EPSILON = 1e-14


class DeltaPathPlanner(
    BasePathPlanner[DeltaPathPlannerParams, DeltaPathPlannerPlanPathParams],
):
    """Apply a relative displacement and rotation to the start position.

    Generates a two-point path based on linear distance and rotational delta.
    """

    @staticmethod
    def _compute_displacement(
        start: OrientedPoint,
        distance: float,
    ) -> tuple[float, float]:
        """Compute the displacement vector from the start point.

        Args:
            start (OrientedPoint): Starting pose.
            distance (float): Distance to move forward.

        Returns:
            tuple[float, float]:
                Displacement vector (dx, dy) based on the start orientation.

        Raises:
            ValueError: If `start.theta` is None.
        """
        if start.theta is None:
            msg = "Start orientation (theta) must be defined."
            raise ValueError(msg)
        return (
            distance * math.cos(start.theta),  # dx
            distance * math.sin(start.theta),  # dy
        )

    @staticmethod
    def _compute_rotation(start: OrientedPoint, rotation: float) -> float:
        """Compute the final orientation after applying rotation.

        Args:
            start (OrientedPoint): Starting pose.
            rotation (float): Rotation to apply.

        Returns:
            float: Final orientation angle.

        Raises:
            ValueError: If `start.theta` is None.
        """
        if start.theta is None:
            msg = "Start orientation (theta) must be defined."
            raise ValueError(msg)
        return (start.theta + rotation) % (2 * math.pi)

    @BasePathPlanner.store_plan_path_params
    def plan_path(self, params: DeltaPathPlannerPlanPathParams) -> list[OrientedPoint]:
        """Generate a path using relative displacement and rotation.

        Args:
            params (DeltaPathPlannerPlanPathParams):
                Parameters including start point, distance, and rotation.

        Returns:
            list[OrientedPoint]: List containing the start and resulting goal pose.

        Raises:
            ValueError: If start position theta is None.
        """
        if params.start.theta is None:
            msg = (
                f"Start position theta must be defined for DeltaPathPlanner, "
                f"got None at position ({params.start.x}, {params.start.y})"
            )
            raise ValueError(msg)

        x, y, theta = params.start.x, params.start.y, params.start.theta

        # 1. Apply displacement
        if abs(self.params.distance) > EPSILON:
            dx, dy = self._compute_displacement(params.start, self.params.distance)
            x += dx
            y += dy

        # 2. Apply rotation
        if abs(self.params.rotation) > EPSILON:
            theta = self._compute_rotation(params.start, self.params.rotation)

        return [params.start, OrientedPoint(x, y, theta)]
