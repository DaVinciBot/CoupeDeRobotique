"""Direct two-point path planner."""

from __future__ import annotations

from typing import TYPE_CHECKING

from navigation.path_planner.base_path_planner.base_path_planner import BasePathPlanner
from navigation.path_planner.basic_path_planner.basic_path_planner_params import (
    BasicPathPlannerParams,
    BasicPathPlannerPlanPathParams,
)
from navigation.path_planner.structs import Direction

if TYPE_CHECKING:
    from geometry import OrientedPoint


class BasicPathPlanner(
    BasePathPlanner[BasicPathPlannerParams, BasicPathPlannerPlanPathParams],
):
    """A basic path planner that generates a direct path between start and goal points.

    If the direction is set to BACKWARD, the orientations are flipped by π radians.
    """

    @BasePathPlanner.store_plan_path_params
    def plan_path(self, params: BasicPathPlannerPlanPathParams) -> list[OrientedPoint]:
        """Plan a basic two-point path from start to goal.

        Args:
            params (BasicPathPlannerPlanPathParams):
                Parameters including start and goal points.

        Returns:
            list[OrientedPoint]: List containing start and goal, possibly reversed
                for backward direction.
        """
        return [
            (
                params.start
                if self.params.direction == Direction.FORWARD
                else self._compute_backward_position(params.start)
            ),
            (
                params.goal
                if self.params.direction == Direction.FORWARD
                else self._compute_backward_position(params.goal)
            ),
        ]
