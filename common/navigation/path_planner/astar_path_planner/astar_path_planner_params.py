"""Parameters for the A* path planner."""

from __future__ import annotations

from typing import TYPE_CHECKING

from pathfinding.core.diagonal_movement import DiagonalMovement
from pathfinding.core.grid import Grid, GridNode
from pathfinding.finder.a_star import AStarFinder

from navigation.path_planner.base_path_planner.base_path_planner_params import (
    BasePathPlannerParams,
    BasePathPlannerPlanPathParams,
)
from navigation.path_planner.structs import Direction, PathPlanningStrategy

if TYPE_CHECKING:
    from geometry import OrientedPoint


class AStarPathPlannerParams(BasePathPlannerParams):
    """Parameter class for the A* path planner."""

    def __init__(
        self,
        grid: Grid,
        path_resolution: float,
        chunk_size: int,
        start: OrientedPoint,
        goal: OrientedPoint,
        direction: Direction = Direction.FORWARD,
    ) -> None:
        """Initialize parameters for the A* path planner.

        Args:
            grid (Grid): Current the grid for pathfinding.
            path_resolution (float): Resolution for path smoothing.
            chunk_size (int): Size of each grid chunk.
            start (OrientedPoint): Starting point of the path.
            goal (OrientedPoint): Goal point of the path.
            direction (Direction, optional): Indicates whether the path should
                be planned FORWARD or BACKWARD. Defaults to Direction.FORWARD.

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
    """Parameters for planning a path using the A* algorithm."""

    def __init__(self, start: OrientedPoint, goal: OrientedPoint) -> None:
        """Initialize plan parameters.

        Args:
            start (OrientedPoint): Starting point of the path.
            goal (OrientedPoint): Goal point of the path.

        """
        self.goal: OrientedPoint = goal
        super().__init__(start)
