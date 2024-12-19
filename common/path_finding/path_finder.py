# ====== Code Summary ======
# This script defines the `PathFinder` class, a utility for pathfinding using the A* algorithm.
# The class is integrated with a grid manager to handle coordinate transformations and supports
# generating paths with orientations. It includes private methods for internal operations like
# orientation calculation, path smoothing, and conversions between grid and absolute coordinates.
# Public methods allow updating positions, goals, and finding oriented paths.

# ====== Imports ======
# Standard library imports
import math

# Third-party library imports
from pathfinding.core.diagonal_movement import DiagonalMovement
from pathfinding.finder.a_star import AStarFinder
from pathfinding.core.grid import GridNode
import numpy as np

# Internal project imports
from logger import Logger, LogLevels, time_tracker
from geometry import OrientedPoint, Point
from arena import GridManager


# ====== PathFinder Class ======
class PathFinder:
    """
    Pathfinding utility using the A* algorithm.

    Attributes:
        logger (Logger): Logger instance for logging information.
        current_position (GridNode): Current position in grid coordinates.
        goal (GridNode): Goal position in grid coordinates.
        grid_manager (GridManager): Manager for grid operations and conversions.
        path_resolution (float): Resolution for path smoothing.
        path_found (list[GridNode]): Grid path found by the algorithm.
        oriented_path_found (list[OrientedPoint]): Path with orientation for the robot.
    """

    def __init__(
            self,
            logger: Logger,
            start: OrientedPoint,
            goal: OrientedPoint,
            grid_manager: GridManager,
            path_resolution: float,
    ) -> None:
        self.logger: Logger = logger
        self.grid_manager: GridManager = grid_manager

        self.current_position: GridNode = self.grid_manager.absolute_coords_to_grid_coords(start)
        self.goal: GridNode = self.grid_manager.absolute_coords_to_grid_coords(goal)

        self.path_resolution: float = path_resolution

        # Instantiate the A* path finder
        self.finder = AStarFinder(diagonal_movement=DiagonalMovement.always)

        # Placeholder attributes for paths
        self.path_found: list[GridNode] = []
        self.oriented_path_found: list[OrientedPoint] = []

    # ====== Private Methods ======

    @staticmethod
    def __compute_orientation(current_point: GridNode | Point, next_point: GridNode | Point) -> float:
        """Compute the orientation (angle in radians) from the current point to the next."""
        return math.atan2(
            next_point.y - current_point.y, next_point.x - current_point.x
        )

    def __find_path(self) -> list[GridNode]:
        """Run the A* algorithm to find a path between current_position and goal."""
        self.path_found, exploration_value = self.finder.find_path(
            self.grid_manager.static_grid.node(
                self.current_position.x, self.current_position.y
            ),
            self.grid_manager.static_grid.node(self.goal.x, self.goal.y),
            self.grid_manager.static_grid,
        )

        if not self.path_found:
            self.logger.log(
                f"No path found! [start=({self.current_position.x}, {self.current_position.y}), "
                f"goal=({self.goal.x}, {self.goal.y})] exploration_value={exploration_value}",
                LogLevels.WARNING,
            )
            return []

        return self.path_found

    def __grid_path_to_absolute_path(self, grid_path: list[GridNode]) -> list[Point]:
        """Convert a grid path to an absolute path."""
        if not grid_path:
            self.logger.log("[grid path to absolute path] Path to convert is empty!", LogLevels.DEBUG)
            return []

        return [
            Point(*self.grid_manager.get_grid_node_center(node)) for node in grid_path
        ]

    def __path_to_absolute_oriented_path(
            self, path: list[GridNode] | list[Point], is_grid_path: bool
    ) -> list[OrientedPoint]:
        """Convert a path (grid or absolute) to an oriented path for the robot."""
        if not path:
            self.logger.log("[path to absolute oriented path] Path to convert is empty!", LogLevels.DEBUG)
            return []

        oriented_path: list[OrientedPoint] = []

        for i in range(len(path) - 1):
            if is_grid_path:
                current_point = GridNode(*self.grid_manager.get_grid_node_center(path[i]))
                next_point = GridNode(*self.grid_manager.get_grid_node_center(path[i + 1]))
            else:
                current_point = path[i]
                next_point = path[i + 1]

            current_orientation = self.__compute_orientation(current_point, next_point)

            oriented_path.append(
                OrientedPoint(current_point.x, current_point.y, current_orientation)
            )

        last_point = (
            GridNode(*self.grid_manager.get_grid_node_center(path[-1]))
            if is_grid_path
            else path[-1]
        )

        oriented_path.append(
            OrientedPoint(last_point.x, last_point.y, oriented_path[-1].theta)
        )

        return oriented_path

    def __smooth_path(self, path: list[Point]) -> list[Point]:
        """Smooth the path to ensure consistent spacing and reduce sharp turns."""
        if not path:
            self.logger.log("[smooth path] Path to convert is empty!", LogLevels.DEBUG)
            return []

        # Convert path to NumPy array for efficient computation
        path_array = np.array([[point.x, point.y] for point in path])
        smoothed_path = [path_array[0]]

        # Smoothing loop
        smoothed_points = (path_array[:-2] + path_array[1:-1] + path_array[2:]) / 3
        smoothed_path.extend(smoothed_points)
        smoothed_path.append(path_array[-1])

        # Interpolate points to maintain uniform spacing
        smoothed_path = np.array(smoothed_path)
        interpolated_path = [smoothed_path[0]]

        for i in range(1, len(smoothed_path)):
            start = interpolated_path[-1]
            end = smoothed_path[i]

            vector = end - start
            distance = np.linalg.norm(vector)

            if distance == 0:
                continue

            direction = vector / distance
            num_new_points = int(distance // self.path_resolution)

            for j in range(1, num_new_points + 1):
                new_point = start + j * self.path_resolution * direction
                interpolated_path.append(new_point)

        # Ensure the last node is included
        if np.linalg.norm(interpolated_path[-1] - smoothed_path[-1]) > 0:
            interpolated_path.append(smoothed_path[-1])

        # Convert back to GridNode objects
        return [Point(x, y) for x, y in interpolated_path]

    # ====== Public Methods ======

    def update_goal(self, new_goal: OrientedPoint) -> None:
        """Update the goal position."""
        self.goal = self.grid_manager.absolute_coords_to_grid_coords(new_goal)

    def update_current_position(self, new_position: OrientedPoint) -> None:
        """Update the current position."""
        self.current_position = self.grid_manager.absolute_coords_to_grid_coords(new_position)

    @time_tracker(lambda self: self.logger)
    def find_oriented_path(self, smooth_path: bool = False) -> list[OrientedPoint]:
        """Find a path and convert it into an oriented path."""
        self.__find_path()

        if not smooth_path:
            return self.__path_to_absolute_oriented_path(self.path_found, is_grid_path=True)

        self.oriented_path_found = self.__path_to_absolute_oriented_path(
            self.__smooth_path(
                self.__grid_path_to_absolute_path(self.path_found)
            ),
            is_grid_path=False
        )

        return self.oriented_path_found
