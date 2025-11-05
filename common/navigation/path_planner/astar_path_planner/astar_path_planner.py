"""A* path planner returning oriented paths."""

from __future__ import annotations

import math

from loggerplusplus import Logger, time_tracker
from pathfinding.core.grid import GridNode

from geometry import OrientedPoint
from navigation.path_planner.astar_path_planner.astar_path_planner_params import (
    AStarPathPlannerParams,
    AStarPathPlannerPlanPathParams,
)
from navigation.path_planner.base_path_planner.base_path_planner import BasePathPlanner
from navigation.path_planner.structs import Direction

_TWO_POINTS = 2
_THREE_POINTS = 3
_FOUR_POINTS = 4


class AStarPathPlanner(
    BasePathPlanner[AStarPathPlannerParams, AStarPathPlannerPlanPathParams],
):
    """Generate a path between start and goal points using the A* algorithm."""

    def __init__(
        self,
        params: AStarPathPlannerParams,
        logger: Logger | None = None,
    ) -> None:
        """Initialize the A* path planner.

        Args:
            params (AStarPathPlannerParams): Parameters including motion direction.
            logger (Logger | None, optional):
                Logger instance for debugging. Defaults to None.
        """
        super().__init__(params, logger)

        self.params.current_position = self.__absolute_coords_to_grid_coords(
            self.params.absolute_current_position,
        )
        self.params.goal = self.__absolute_coords_to_grid_coords(
            self.params.absolute_goal,
        )

    # region ====== Private Methods ======
    @staticmethod
    def __compute_orientation(
        current_point: GridNode | OrientedPoint,
        next_point: GridNode | OrientedPoint,
    ) -> float:
        """Compute orientation (angle in radians) from current point to next.

        Args:
            current_point (GridNode | OrientedPoint): Current point coordinates.
            next_point (GridNode | OrientedPoint): Next point coordinates.

        Returns:
            float: Orientation angle in radians.
        """
        return math.atan2(
            next_point.y - current_point.y,
            next_point.x - current_point.x,
        )

    def __find_path(self) -> list[GridNode]:
        """Run the A* algorithm to find a path between current_position and goal.

        Returns:
            list[GridNode]: List of nodes representing the found path.
        """
        grid = self.params.grid

        self.params.path_found, exploration_value = self.params.finder.find_path(
            start=grid.node(
                self.params.current_position.x,
                self.params.current_position.y,
            ),
            end=grid.node(self.params.goal.x, self.params.goal.y),
            graph=grid,
        )

        if not self.params.path_found:
            self._logger.warning(
                f"[NAV:Path] No path found"
                f"Grid: [start=({self.params.current_position.x}, "
                f"{self.params.current_position.y}), goal=({self.params.goal.x}, "
                f"{self.params.goal.y})] "
                f"Absolute: [start=({self.params.absolute_current_position.x}, "
                f"{self.params.absolute_current_position.y}), "
                f"goal=({self.params.absolute_goal.x}, "
                f"{self.params.absolute_goal.y})] | "
                f"exploration_value={exploration_value}",
            )
            return []

        return self.params.path_found

    def __get_grid_node_center(self, node: GridNode) -> tuple[int, int]:
        """Get the center of a grid node.

        Args:
            node (GridNode): The grid node.

        Returns:
            tuple[int, int]: Center of the grid node in absolute coordinates.
        """
        return (
            node.x * self.params.chunk_size + self.params.half_chunk_size,
            node.y * self.params.chunk_size + self.params.half_chunk_size,
        )

    def __path_to_absolute_oriented_path(
        self,
        path: list[GridNode],
        *,
        is_grid_path: bool,
    ) -> list[OrientedPoint]:
        """Convert a path (grid or absolute) to an oriented path for the robot.

        Args:
            path (list[GridNode]): Input path.
            is_grid_path (bool): Indicates if the path is in grid coordinates.

        Returns:
            list[OrientedPoint]: Path with orientation included.
        """
        if not path:
            self._logger.debug(
                "[NAV:Path] Path to convert is empty!",
            )
            return []

        oriented_path: list[OrientedPoint] = []

        for i in range(len(path) - 1):
            current_point = (
                GridNode(*self.__get_grid_node_center(path[i]))
                if is_grid_path
                else path[i]
            )
            next_point = (
                GridNode(*self.__get_grid_node_center(path[i + 1]))
                if is_grid_path
                else path[i + 1]
            )

            current_orientation = self.__compute_orientation(
                current_point,
                next_point,
            )

            oriented_path.append(
                OrientedPoint(current_point.x, current_point.y, current_orientation),
            )

        last_point = (
            GridNode(*self.__get_grid_node_center(path[-1]))
            if is_grid_path
            else path[-1]
        )

        oriented_path.append(
            OrientedPoint(last_point.x, last_point.y, oriented_path[-1].theta),
        )
        return oriented_path

    def __add_path_extremities_point(
        self,
        path: list[OrientedPoint],
    ) -> list[OrientedPoint]:
        """Keep only significant extremity and intermediate points in the path.

        Args:
            path (list[OrientedPoint]): A list of points representing the path.

        Returns:
            list[OrientedPoint]: A reduced list containing key waypoints.
        """
        # If only 2 points in the path, conserve only the start and goal points
        if len(path) <= _TWO_POINTS:
            return [
                self.params.absolute_current_position,
                self.params.absolute_goal,
            ]

        # If 3 points, conserve only the start, goal, and the middle point
        if len(path) == _THREE_POINTS:
            return [
                self.params.absolute_current_position,
                path[1],
                self.params.absolute_goal,
            ]

        # If 4 points, conserve only the start, goal, and the 2 middle points
        if len(path) == _FOUR_POINTS:
            return [
                self.params.absolute_current_position,
                path[1],
                path[2],
                self.params.absolute_goal,
            ]

        # If more than 4 points, keep start/goal and drop first and last two
        return [
            self.params.absolute_current_position,
            *path[2:-2],
            self.params.absolute_goal,
        ]

    def __absolute_coords_to_grid_coords(
        self,
        point: OrientedPoint,
    ) -> GridNode:
        """Convert absolute coordinates to grid coordinates.

        Args:
            point (OrientedPoint): OrientedPoint in absolute coordinates.

        Returns:
            GridNode: Coordinates of the point within the grid.
        """
        return GridNode(
            int(point.x / self.params.chunk_size),
            int(point.y / self.params.chunk_size),
        )

    # endregion

    # region ====== Public Methods ======

    def update_goal(self, new_goal: OrientedPoint) -> None:
        """Update the goal position.

        Args:
            new_goal (OrientedPoint): New goal position in absolute coordinates.
        """
        self.params.absolute_goal = new_goal
        self.params.goal = self.__absolute_coords_to_grid_coords(new_goal)

    def update_current_position(self, new_position: OrientedPoint) -> None:
        """Update the current position.

        Args:
            new_position (OrientedPoint): New current position in absolute coordinates.
        """
        self.params.absolute_current_position = new_position
        self.params.current_position = self.__absolute_coords_to_grid_coords(
            new_position,
        )

    @BasePathPlanner.store_plan_path_params
    @time_tracker(lambda self: self.logger)
    def plan_path(self, _params: AStarPathPlannerPlanPathParams) -> list[OrientedPoint]:
        """Plan a list of oriented points path from start to goal.

        Args:
            _params (AStarPathPlannerPlanPathParams):
                Parameters including start and goal points.

        Returns:
            list[OrientedPoint]:
                List containing oriented path from the start to the goal,
                possibly reversed for backward direction.
        """
        self.__find_path()

        # If no path found, return an empty list
        if not self.params.path_found:
            self._logger.warning("No path found!")
            return []

        # Add real robot position as start point and goal as end point
        # (not approximated chunk points)

        self.params.oriented_path_found = (
            # Add start and goal points to the path
            # and remove some points to improve trajectory
            self.__add_path_extremities_point(
                # grid node path to absolute oriented path (X, Y, THETA)
                self.__path_to_absolute_oriented_path(
                    self.params.path_found,
                    is_grid_path=True,
                ),
            )
        )

        if self.params.direction == Direction.BACKWARD:
            self.params.oriented_path_found = [
                self._compute_backward_position(point)
                for point in self.params.oriented_path_found
            ]
        # We don't need to call __set_path_extremities_correct_theta
        # because we already have the start and goal points with correct theta
        return self.params.oriented_path_found

    # endregion
