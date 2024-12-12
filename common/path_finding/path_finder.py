# ====== Imports ======
# Standard library imports
import math

# Third-party library imports
from pathfinding.core.diagonal_movement import DiagonalMovement
from pathfinding.finder.a_star import AStarFinder
from pathfinding.core.grid import Grid, GridNode
import matplotlib.pyplot as plt

# Internal project imports
from logger import Logger, LogLevels, time_tracker
from geometry import OrientedPoint, Point


# ====== PathFinder Class ======
class PathFinder:
    """
    Pathfinding utility using the A* algorithm.

    Attributes:
        logger (Logger): Logger instance for logging information.
        current_position (GridNode): Current position in grid coordinates.
        goal (GridNode): Goal position in grid coordinates.
        grid (Grid): The grid to navigate.
        chunk_size (int): Size of each grid chunk in absolute coordinates.
        path_found (list[GridNode]): Grid path found by the algorithm.
        oriented_path_found (list[OrientedPoint]): Path with orientation for the robot.
    """

    def __init__(
            self,
            logger: Logger,
            start: OrientedPoint,
            goal: OrientedPoint,
            grid: Grid,
            chunk_size: int,
    ) -> None:
        self.logger: Logger = logger
        self.chunk_size: int = chunk_size

        self.current_position: GridNode = self.__absolute_coords_to_grid_coords(start)
        self.goal: GridNode = self.__absolute_coords_to_grid_coords(goal)

        self.grid: Grid = grid

        # Instantiate the A* path finder
        self.finder = AStarFinder(diagonal_movement=DiagonalMovement.always)

        # Placeholder attributes for paths
        self.path_found: list[GridNode] = []
        self.oriented_path_found: list[OrientedPoint] = []

    # ====== Private Methods ======

    @staticmethod
    def __compute_orientation(current_point: GridNode, next_point: GridNode) -> float:
        """Compute the orientation (angle in radians) from the current point to the next."""
        return math.atan2(
            next_point.y - current_point.y, next_point.x - current_point.x
        )

    def __get_grid_node_center(self, node: GridNode) -> tuple[int, int]:
        """Get the center coordinates of a grid node."""
        return (
            node.x * self.chunk_size + self.chunk_size // 2,
            node.y * self.chunk_size + self.chunk_size // 2,
        )

    def __find_path(self) -> list[GridNode]:
        """Run the A* algorithm to find a path between current_position and goal."""
        self.path_found, _ = self.finder.find_path(
            self.grid.node(self.current_position.x, self.current_position.y),
            self.grid.node(self.goal.x, self.goal.y),
            self.grid,
        )

        if not self.path_found:
            self.logger.log(
                f"No path found! [start=({self.current_position.x}, {self.current_position.y}), "
                f"goal=({self.goal.x}, {self.goal.y})]",
                LogLevels.WARNING,
            )
            return []

        return self.path_found

    def __path_to_oriented_path(self, path: list[GridNode]) -> list[OrientedPoint]:
        """Convert a grid path to an oriented path for the robot."""
        if not path:
            self.logger.log("Path to convert is empty!", LogLevels.DEBUG)
            return []

        oriented_path: list[OrientedPoint] = []

        for i in range(len(path) - 1):
            current_node = GridNode(*self.__get_grid_node_center(path[i]))
            next_node = GridNode(*self.__get_grid_node_center(path[i + 1]))
            current_orientation = self.__compute_orientation(current_node, next_node)

            oriented_path.append(
                OrientedPoint(current_node.x, current_node.y, current_orientation)
            )

        oriented_path.append(
            OrientedPoint(
                *self.__get_grid_node_center(path[-1]), oriented_path[-1].theta
            )
        )

        return oriented_path

    def __absolute_coords_to_grid_coords(
            self, point: OrientedPoint | Point
    ) -> GridNode:
        """Convert absolute coordinates to grid coordinates."""
        return GridNode(
            int(point.x // self.chunk_size), int(point.y // self.chunk_size)
        )

    def __grid_coords_to_absolute_coords(self, node: GridNode) -> Point:
        """Convert grid coordinates back to absolute coordinates."""
        x, y = self.__get_grid_node_center(node)
        return Point(x * self.chunk_size, y * self.chunk_size)

    # ====== Public Methods ======

    def update_grid(self, new_grid: Grid) -> None:
        """Update the grid for pathfinding."""
        self.grid = new_grid

    def update_goal(self, new_goal: OrientedPoint) -> None:
        """Update the goal position."""
        self.goal = self.__absolute_coords_to_grid_coords(new_goal)

    def update_current_position(self, new_position: OrientedPoint) -> None:
        """Update the current position."""
        self.current_position = self.__absolute_coords_to_grid_coords(new_position)

    @time_tracker(lambda self: self.logger)
    def find_oriented_path(self) -> list[OrientedPoint]:
        """Find a path and convert it into an oriented path."""
        self.oriented_path_found = self.__path_to_oriented_path(self.__find_path())
        return self.oriented_path_found

    def visualize(self) -> None:
        """Visualize the grid and the path found."""
        rows, cols = self.grid.height, self.grid.width
        fig, ax = plt.subplots(figsize=(10, 10))

        for y in range(rows):
            for x in range(cols):
                node = self.grid.node(x, y)
                if not node.walkable:
                    ax.add_patch(plt.Rectangle((x, rows - y - 1), 1, 1, color="black"))

        start_x, start_y = self.current_position.x, rows - self.current_position.y - 1
        goal_x, goal_y = self.goal.x, rows - self.goal.y - 1

        ax.add_patch(
            plt.Rectangle((start_x, start_y), 1, 1, color="green", label="Start")
        )
        ax.add_patch(plt.Rectangle((goal_x, goal_y), 1, 1, color="red", label="Goal"))

        if self.path_found:
            for i in range(len(self.path_found) - 1):
                current = self.path_found[i]
                next_node = self.path_found[i + 1]
                ax.plot(
                    [current.x + 0.5, next_node.x + 0.5],
                    [rows - current.y - 1 + 0.5, rows - next_node.y - 1 + 0.5],
                    color="blue",
                    linewidth=2,
                )

        ax.set_xticks(range(cols))
        ax.set_yticks(range(rows))
        ax.grid(True)
        ax.set_xlim(0, cols)
        ax.set_ylim(0, rows)
        ax.set_aspect("equal")
        ax.set_title("Pathfinding Visualization")
        ax.legend(loc="upper right")
        plt.show()

    def visualize_with_scores(self) -> None:
        """Visualize the grid, path, and node scores."""
        rows, cols = self.grid.height, self.grid.width
        fig, ax = plt.subplots(figsize=(15, 15))

        max_score, min_score = float("-inf"), float("inf")
        for y in range(rows):
            for x in range(cols):
                node = self.grid.node(x, y)
                if node.walkable:
                    max_score = max(max_score, node.f)
                    min_score = min(min_score, node.f)

        score_range = max_score - min_score if max_score > min_score else 1

        for y in range(rows):
            for x in range(cols):
                node = self.grid.node(x, y)
                if not node.walkable:
                    ax.add_patch(plt.Rectangle((x, rows - y - 1), 1, 1, color="black"))
                else:
                    normalized_score = (node.f - min_score) / score_range
                    color_intensity = 1.0 - normalized_score
                    ax.add_patch(
                        plt.Rectangle(
                            (x, rows - y - 1),
                            1,
                            1,
                            color=(color_intensity, color_intensity, color_intensity),
                        )
                    )
                    ax.text(
                        x + 0.5,
                        rows - y - 1 + 0.5,
                        f"{node.f:.1f}",
                        color="orange",
                        ha="center",
                        va="center",
                        fontsize=10,
                    )

        start_x, start_y = self.current_position.x, rows - self.current_position.y - 1
        goal_x, goal_y = self.goal.x, rows - self.goal.y - 1

        ax.add_patch(
            plt.Rectangle((start_x, start_y), 1, 1, color="green", label="Start")
        )
        ax.add_patch(plt.Rectangle((goal_x, goal_y), 1, 1, color="red", label="Goal"))

        if self.path_found:
            for i in range(len(self.path_found) - 1):
                current = self.path_found[i]
                next_node = self.path_found[i + 1]
                ax.plot(
                    [current.x + 0.5, next_node.x + 0.5],
                    [rows - current.y - 1 + 0.5, rows - next_node.y - 1 + 0.5],
                    color="blue",
                    linewidth=2,
                )

        ax.set_xticks(range(cols))
        ax.set_yticks(range(rows))
        ax.grid(True)
        ax.set_xlim(0, cols)
        ax.set_ylim(0, rows)
        ax.set_aspect("equal")
        ax.set_title("Pathfinding Visualization with Scores")
        ax.legend(loc="upper right")
        plt.show()

# ====== Code Summary ======
# This implementation defines the PathFinder class, which leverages the A* algorithm for grid-based pathfinding.
# It includes methods to find a path, convert it to an oriented path, update positions/goals, and visualize the grid.
# Visualization methods include basic and score-based grid representations.
