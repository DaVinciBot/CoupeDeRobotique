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


# ====== Delta Path Planner Class ======
class DeltaPathPlanner(BasePathPlanner):

    def __init__(self, params: DeltaPathPlannerParams, logger: Logger | None = None) -> None:
        super().__init__(params, logger)

    @staticmethod
    def _compute_displacement(start: OrientedPoint, distance: float) -> tuple[float, float]:
        return (
            distance * math.cos(start.theta),  # dx
            distance * math.sin(start.theta)  # dy
        )

    @staticmethod
    def _compute_rotation(start: OrientedPoint, rotation: float) -> float:
        return (start.theta + rotation) % (2 * math.pi)

    def plan_path(self, start: OrientedPoint, distance: float = 0.0, rotation: float = 0.0) -> list[OrientedPoint]:
        # Compute the displacement, then rotation
        x, y, theta = start.x, start.y, start.theta

        # 1. Compute the displacement
        if distance != 0.0:
            dx, dy = self._compute_displacement(start, distance)
            x += dx
            y += dy

        # 2. Compute the rotation
        if rotation != 0.0:
            theta = self._compute_rotation(start, rotation)

        return [
            start,
            OrientedPoint(x, y, theta)
        ]
