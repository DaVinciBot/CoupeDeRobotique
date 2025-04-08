# ====== Code Summary ======

# ====== Internal Project Imports ======
from navigation.path_planner.structs import PathPlanningStrategy, Direction
from navigation.path_planner.base_path_planner.base_path_planner_params import BasePathPlannerParams, \
    BasePathPlannerPlanPathParams
from path_finding import PathFinder
from pathfinding.core.grid import Grid

from geometry import OrientedPoint


class AStarPathPlannerParams(BasePathPlannerParams):
    """
    Parameter class for the A* path planner.

    Attributes:
        direction (Direction): Indicates whether the path should be planned FORWARD or BACKWARD.
        current_grid_state (Grid): Current state of the grid for pathfinding.
    """

    def __init__(self, direction: Direction = Direction.FORWARD, path_finder: PathFinder = None,
                 current_grid_state: Grid = None):
        """
        Initialize parameters for the A* path planner.

        Args:
            direction (Direction): Direction of motion (default is FORWARD).
            path_finder (PathFinder): Instance of the path finder (default is None).
            current_grid_state (Grid): Current state of the grid (default is None).
        """
        self.direction: Direction = direction
        self.current_grid_state: Grid = current_grid_state
        super().__init__(PathPlanningStrategy.A_STAR)


class AStarPathPlannerPlanPathParams(BasePathPlannerPlanPathParams):
    """
    Parameters for planning a path using the A* algorithm.

    Attributes:
        start (OrientedPoint): Starting point of the path.
        goal (OrientedPoint): Goal point of the path.
    """

    def __init__(self, start: OrientedPoint, goal: OrientedPoint):
        self.goal: OrientedPoint = goal
        super().__init__(start)
