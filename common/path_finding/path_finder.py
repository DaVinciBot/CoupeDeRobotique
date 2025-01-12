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
        """
        Initialize the PathFinder instance.

        Args:
            logger (Logger): Logger instance for logging information.
            start (OrientedPoint): Starting position in absolute coordinates.
            goal (OrientedPoint): Goal position in absolute coordinates.
            grid_manager (GridManager): Manager for grid operations and transformations.
            path_resolution (float): Resolution for path smoothing.
        """
        self.logger: Logger = logger
        self.grid_manager: GridManager = grid_manager

        self.absolute_current_position: OrientedPoint = start
        self.absolute_goal: OrientedPoint = goal

        self.current_position: GridNode = (
            self.grid_manager.absolute_coords_to_grid_coords(start)
        )
        self.goal: GridNode = self.grid_manager.absolute_coords_to_grid_coords(goal)

        self.path_resolution: float = path_resolution
        self.finder = AStarFinder(diagonal_movement=DiagonalMovement.always)

        self.path_found: list[GridNode] = []
        self.oriented_path_found: list[OrientedPoint] = []

    # ====== Private Methods ======

    @staticmethod
    def __compute_orientation(
        current_point: GridNode | Point, next_point: GridNode | Point
    ) -> float:
        """
        Compute the orientation (angle in radians) from the current point to the next.

        Args:
            current_point (GridNode | Point): Current point coordinates.
            next_point (GridNode | Point): Next point coordinates.

        Returns:
            float: Orientation angle in radians.
        """
        return math.atan2(
            next_point.y - current_point.y, next_point.x - current_point.x
        )

    def __find_path(self, use_static_and_dynamic_grid: bool) -> list[GridNode]:
        """
        Run the A* algorithm to find a path between current_position and goal.

        Returns:
            list[GridNode]: List of nodes representing the found path.
        """
        grid = (
            self.grid_manager.static_and_dynamic_grid
            if use_static_and_dynamic_grid
            else self.grid_manager.static_grid
        )

        self.path_found, exploration_value = self.finder.find_path(
            start=grid.node(self.current_position.x, self.current_position.y),
            end=grid.node(self.goal.x, self.goal.y),
            graph=grid,
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
        """
        Convert a grid path to an absolute path.

        Args:
            grid_path (list[GridNode]): Path as a list of grid nodes.

        Returns:
            list[Point]: Path as a list of absolute points.
        """
        if not grid_path:
            self.logger.log(
                "[grid path to absolute path] Path to convert is empty!",
                LogLevels.DEBUG,
            )
            return []

        return [
            Point(*self.grid_manager.get_grid_node_center(node)) for node in grid_path
        ]

    def __path_to_absolute_oriented_path(
        self, path: list[GridNode] | list[Point], is_grid_path: bool
    ) -> list[OrientedPoint]:
        """
        Convert a path (grid or absolute) to an oriented path for the robot.

        Args:
            path (list[GridNode] | list[Point]): Input path.
            is_grid_path (bool): Indicates if the path is in grid coordinates.

        Returns:
            list[OrientedPoint]: Path with orientation included.
        """
        if not path:
            self.logger.log(
                "[path to absolute oriented path] Path to convert is empty!",
                LogLevels.DEBUG,
            )
            return []

        oriented_path: list[OrientedPoint] = []

        for i in range(len(path) - 1):
            current_point = (
                GridNode(*self.grid_manager.get_grid_node_center(path[i]))
                if is_grid_path
                else path[i]
            )
            next_point = (
                GridNode(*self.grid_manager.get_grid_node_center(path[i + 1]))
                if is_grid_path
                else path[i + 1]
            )

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

    @time_tracker(lambda self: self.logger)
    def __smooth_path(self, path: list[Point]) -> list[Point]:
        """
        Smooth the path to ensure consistent spacing and reduce sharp turns.

        Args:
            path (list[Point]): Path as a list of absolute points.

        Returns:
            list[Point]: Smoothed path.
        """
        if not path:
            self.logger.log("[smooth path] Path to convert is empty!", LogLevels.DEBUG)
            return []

        path_array = np.array([[point.x, point.y] for point in path])

        smoothed_path = np.empty_like(path_array)
        smoothed_path[0] = path_array[0]
        smoothed_path[1:-1] = (path_array[:-2] + path_array[1:-1] + path_array[2:]) / 3
        smoothed_path[-1] = path_array[-1]

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
            new_points = [
                start + j * self.path_resolution * direction
                for j in range(1, num_new_points + 1)
            ]
            interpolated_path.extend(new_points)
            interpolated_path.append(end)

        return [Point(x, y) for x, y in interpolated_path]

    def __remove_points_before_position(
        self, path: list[OrientedPoint], from_start_to_end: bool
    ) -> list[OrientedPoint]:
        """
        Remove points from the path before the current position.

        Args:
            path (list[OrientedPoint]): Path to modify.
            from_start_to_end (bool): Direction of the path.
        Returns:
            list[OrientedPoint]: Path with points removed.
        """
        diff = -1

        if from_start_to_end:
            i = 0
            while diff < 0 and i < len(path) - 1:
                diff = path[i + 1].distance(self.absolute_current_position) - path[
                    i
                ].distance(self.absolute_current_position)
                i += 1

            return path[i:]
        else:
            i = len(path) - 1
            while diff < 0 and i > 0:
                diff = path[i - 1].distance(self.absolute_current_position) - path[
                    i
                ].distance(self.absolute_current_position)
                i -= 1

            return path[:i]

    def __add_absolute_start_and_goal_to_path(
        self, path: list[OrientedPoint]
    ) -> list[OrientedPoint]:
        """
        Add the real robot position as start point and goal as end point (not approximated chunk points).

        Args:
            path (list[OrientedPoint]): Path to modify.
        Returns:
            list[OrientedPoint]: Path with start and goal points added.
        """
        return [self.absolute_current_position, *path, self.absolute_goal]

    def __add_path_extremities(self, path: list[OrientedPoint]) -> list[OrientedPoint]:
        """
        Add the real robot position as start point and goal as end point (not approximated chunk points).

        Args:
            path (list[OrientedPoint]): Path to modify.
        Returns:
            list[OrientedPoint]: Path with start and goal points added.
        """
        path = self.__remove_points_before_position(path=path, from_start_to_end=True)
        # path = self.__remove_points_before_position(path=path, from_start_to_end=False)
        return self.__add_absolute_start_and_goal_to_path(path=path)

    # ====== Public Methods ======

    def update_goal(self, new_goal: OrientedPoint) -> None:
        """
        Update the goal position.

        Args:
            new_goal (OrientedPoint): New goal position in absolute coordinates.
        """
        self.absolute_goal: OrientedPoint = new_goal
        self.goal: GridNode = self.grid_manager.absolute_coords_to_grid_coords(new_goal)

    def update_current_position(self, new_position: OrientedPoint) -> None:
        """
        Update the current position.

        Args:
            new_position (OrientedPoint): New current position in absolute coordinates.
        """
        self.absolute_current_position: OrientedPoint = new_position
        self.current_position: GridNode = (
            self.grid_manager.absolute_coords_to_grid_coords(new_position)
        )

    @time_tracker(lambda self: self.logger)
    def find_oriented_path(
        self, use_static_and_dynamic_grid: bool = False, smooth_path: bool = False
    ) -> list[OrientedPoint]:
        """
        Find a path and convert it into an oriented path.

        Args:
            use_static_and_dynamic_grid (bool): Whether to use the static and dynamic grid for pathfinding
                - Static grid: Contains only static obstacles.
                - Dynamic grid: Contains both static and dynamic obstacles (Enemy for exemple).
            smooth_path (bool): Whether to smooth the path before orientation.

        Returns:
            list[OrientedPoint]: Oriented path with angles included.
        """
        # self.__find_path(use_static_and_dynamic_grid=use_static_and_dynamic_grid)
        #
        # if not smooth_path:
        #     return self.__path_to_absolute_oriented_path(self.path_found, is_grid_path=True)
        #
        # self.oriented_path_found = self.__path_to_absolute_oriented_path(
        #     self.__smooth_path(self.__grid_path_to_absolute_path(self.path_found)),
        #     is_grid_path=False,
        # )
        #
        # return self.oriented_path_found
        self.__find_path(use_static_and_dynamic_grid=use_static_and_dynamic_grid)

        # Add real robot position as start point and goal as end point (not approximated chunk points)
        if not smooth_path:
            self.oriented_path_found = self.__path_to_absolute_oriented_path(
                self.path_found, is_grid_path=True
            )
            self.oriented_path_found = self.__add_path_extremities(
                self.oriented_path_found
            )
            return self.oriented_path_found

        self.oriented_path_found = self.__path_to_absolute_oriented_path(
            self.__smooth_path(self.__grid_path_to_absolute_path(self.path_found)),
            is_grid_path=False,
        )
        self.oriented_path_found = self.__add_path_extremities(self.oriented_path_found)
        return self.oriented_path_found
