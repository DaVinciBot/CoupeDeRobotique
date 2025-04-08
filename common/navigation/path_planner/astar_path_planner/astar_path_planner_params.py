# ====== Code Summary ======

# ====== Internal Project Imports ======
from navigation.path_planner.structs import PathPlanningStrategy, Direction
from navigation.path_planner.base_path_planner.base_path_planner_params import BasePathPlannerParams, \
    BasePathPlannerPlanPathParams

# Third-party imports
from pathfinding.core.grid import Grid
from pathfinding.core.grid import GridNode
from pathfinding.core.diagonal_movement import DiagonalMovement
from pathfinding.finder.a_star import AStarFinder

from geometry import OrientedPoint


class AStarPathPlannerParams(BasePathPlannerParams):
    """
    Parameter class for the A* path planner.

    Attributes:
        direction (Direction): Indicates whether the path should be planned FORWARD or BACKWARD.
        grid (Grid): Current grid for pathfinding.
        path_resolution (float): Resolution for path smoothing.
        absolute_current_position (OrientedPoint): Absolute position of the robot in the grid.
        absolute_goal (OrientedPoint): Absolute goal position in the grid.
        current_position (GridNode): Current position of the robot in grid coordinates.
        goal (GridNode): Goal position in grid coordinates.
        finder (AStarFinder): Instance of the A* pathfinding algorithm.
        path_found (list[GridNode]): List of grid nodes representing the found path.
        oriented_path_found (list[OrientedPoint]): List of oriented points representing the path with orientation.
    """

    def __init__(self,
                 grid: Grid,
                 path_resolution: float,
                 chunk_size: int,
                 start: OrientedPoint,
                 goal: OrientedPoint,
                 direction: Direction = Direction.FORWARD,
                 ):
        """
        Initialize parameters for the A* path planner.

        Args:
            direction (Direction): Indicates whether the path should be planned FORWARD or BACKWARD.
            grid (Grid): Current the grid for pathfinding.
            path_resolution (float): Resolution for path smoothing.
        """
        # Direction parameter
        self.direction: Direction = direction

        # Grid related parameters
        self.grid: Grid = grid

        self.chunk_size: int = chunk_size
        self.half_chunk_size: float = self.chunk_size / 2

        self.grid_width: int = grid.width
        self.grid_height: int = grid.height

        # Pathfinding related parameters
        self.path_resolution: float = path_resolution

        self.absolute_current_position: OrientedPoint = start
        self.absolute_goal: OrientedPoint = goal

        self.current_position: GridNode = GridNode(0, 0)
        self.goal: GridNode = GridNode(0, 0)

        self.finder = AStarFinder(diagonal_movement=DiagonalMovement.always)

        self.path_found: list[GridNode] = []
        self.oriented_path_found: list[OrientedPoint] = []

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
