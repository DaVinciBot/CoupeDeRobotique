from logger import Logger, LogLevels, time_tracker
from geometry import OrientedPoint, Point

from pathfinding.core.diagonal_movement import DiagonalMovement
from pathfinding.finder.a_star import AStarFinder
from pathfinding.core.grid import Grid, GridNode

import matplotlib.pyplot as plt
import math
import time
import numpy as np


class PathFinder:

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

        # Use later
        self.path_found: list[GridNode] = []
        self.oriented_path_found: list[OrientedPoint] = []

    """ Private methods """

    @staticmethod
    def __compute_orientation(current_point: GridNode, next_point: GridNode) -> float:
        return math.atan2(
            next_point.y - current_point.y, next_point.x - current_point.x
        )

    def __get_grid_node_center(self, node: GridNode) -> tuple[int, int]:
        return (
            node.x * self.chunk_size + self.chunk_size // 2,
            node.y * self.chunk_size + self.chunk_size // 2,
        )

    def __find_path(self) -> list[GridNode]:
        self.path_found, _ = self.finder.find_path(
            self.grid.node(
                self.current_position.x, self.current_position.y
            ),  # Start node
            self.grid.node(self.goal.x, self.goal.y),  # Goal node
            self.grid,
        )

        if not self.path_found:
            self.logger.log(
                f"No path found ! [start=({self.current_position.x}, {self.current_position.y}), goal=({self.goal.x}, {self.goal.y})]",
                LogLevels.WARNING,
            )
            return []

        return self.path_found

    def __path_to_oriented_path(self, path: list[GridNode]) -> list[OrientedPoint]:
        if not path:
            self.logger.log("Path to convert is empty !", LogLevels.DEBUG)
            return []

        oriented_path: list[OrientedPoint] = []

        for i in range(len(path) - 1):
            # Assume that the robot will use the center of each grid node as a reference point
            current_node = GridNode(*self.__get_grid_node_center(path[i]))
            next_node = GridNode(*self.__get_grid_node_center(path[i + 1]))

            # Compute the orientation of the robot at each point
            current_orientation = self.__compute_orientation(current_node, next_node)

            oriented_path.append(
                OrientedPoint(current_node.x, current_node.y, current_orientation)
            )

        # Add the last point (use same orientation as the previous one)
        oriented_path.append(
            OrientedPoint(
                *self.__get_grid_node_center(path[-1]), oriented_path[-1].theta
            )
        )

        return oriented_path

    def __absolute_coords_to_grid_coords(
        self, point: OrientedPoint | Point
    ) -> GridNode:
        return GridNode(
            int(point.x // self.chunk_size), int(point.y // self.chunk_size)
        )

    def __grid_coords_to_absolute_coords(self, node: GridNode) -> Point:
        x, y = self.__get_grid_node_center(node)
        return Point(x * self.chunk_size, y * self.chunk_size)

    """ Public methods """

    def update_grid(self, new_grid: Grid) -> None:
        self.grid = new_grid

    def update_goal(self, new_goal: OrientedPoint) -> None:
        self.goal = self.__absolute_coords_to_grid_coords(new_goal)

    def update_current_position(self, new_position: OrientedPoint) -> None:
        self.current_position = self.__absolute_coords_to_grid_coords(new_position)

    @time_tracker(lambda self: self.logger)
    def find_oriented_path(self) -> list[OrientedPoint]:
        self.oriented_path_found = self.__path_to_oriented_path(self.__find_path())
        return self.oriented_path_found

    def visualize(self) -> None:
        """
        Visualise the grid with start, goal, obstacles, and the path.
        """
        # Assuming grid dimensions can be inferred from its node structure
        rows, cols = (
            self.grid.height,
            self.grid.width,
        )  # Adjust based on your Grid implementation

        # Initialize the plot
        fig, ax = plt.subplots(figsize=(10, 10))

        # Draw each cell of the grid
        for y in range(rows):
            for x in range(cols):
                node = self.grid.node(x, y)
                if not node.walkable:
                    # Draw obstacles in black
                    ax.add_patch(plt.Rectangle((x, rows - y - 1), 1, 1, color="black"))

        # Draw the start and goal points
        start_x, start_y = self.current_position.x, rows - self.current_position.y - 1
        goal_x, goal_y = self.goal.x, rows - self.goal.y - 1

        ax.add_patch(
            plt.Rectangle((start_x, start_y), 1, 1, color="green", label="Start")
        )
        ax.add_patch(plt.Rectangle((goal_x, goal_y), 1, 1, color="red", label="Goal"))

        # Draw the path if it exists
        if self.path_found:
            for i in range(len(self.path_found) - 1):
                current = self.path_found[i]
                next_node = self.path_found[i + 1]

                # Extract coordinates from GridNode
                current_x, current_y = current.x, rows - current.y - 1
                next_x, next_y = next_node.x, rows - next_node.y - 1

                # Plot the path
                ax.plot(
                    [current_x + 0.5, next_x + 0.5],
                    [current_y + 0.5, next_y + 0.5],
                    color="blue",
                    linewidth=2,
                    label="Path" if i == 0 else None,
                )

        # Set grid lines
        ax.set_xticks(range(cols))
        ax.set_yticks(range(rows))
        ax.grid(True)

        # Set axis limits and labels
        ax.set_xlim(0, cols)
        ax.set_ylim(0, rows)
        ax.set_aspect("equal")
        ax.set_title("Pathfinding Visualization")
        ax.legend(loc="upper right")

        # Show the plot
        plt.show()

    def visualize_with_scores(self) -> None:
        """
        Visualise the grid with start, goal, obstacles, the path, and the scores of each cell.
        """
        # Assuming grid dimensions can be inferred from its node structure
        rows, cols = (
            self.grid.height,
            self.grid.width,
        )  # Adjust based on your Grid implementation

        # Initialize the plot
        fig, ax = plt.subplots(figsize=(15, 15))

        # Compute maximum and minimum scores to normalize color intensity
        max_score = float("-inf")
        min_score = float("inf")

        for y in range(rows):
            for x in range(cols):
                node = self.grid.node(x, y)
                if node.walkable:
                    max_score = max(max_score, node.f)
                    min_score = min(min_score, node.f)

        # Ensure there's a range to normalize
        score_range = max_score - min_score if max_score > min_score else 1

        # Draw each cell of the grid
        for y in range(rows):
            for x in range(cols):
                node = self.grid.node(x, y)
                if not node.walkable:
                    # Draw obstacles in black
                    ax.add_patch(plt.Rectangle((x, rows - y - 1), 1, 1, color="black"))
                else:
                    # Normalize the score for color intensity (between 0 and 1)
                    normalized_score = (node.f - min_score) / score_range
                    # Use a grayscale intensity for the score (1.0 = white, 0.0 = black)
                    color_intensity = 1.0 - normalized_score
                    ax.add_patch(
                        plt.Rectangle(
                            (x, rows - y - 1),
                            1,
                            1,
                            color=(color_intensity, color_intensity, color_intensity),
                        )
                    )
                    # Optionally, add text with the exact score
                    ax.text(
                        x + 0.5,
                        rows - y - 1 + 0.5,
                        f"{node.f:.1f}",
                        color="orange",
                        ha="center",
                        va="center",
                        fontsize=10,
                    )

        # Draw the start and goal points
        start_x, start_y = self.current_position.x, rows - self.current_position.y - 1
        goal_x, goal_y = self.goal.x, rows - self.goal.y - 1

        ax.add_patch(
            plt.Rectangle((start_x, start_y), 1, 1, color="green", label="Start")
        )
        ax.add_patch(plt.Rectangle((goal_x, goal_y), 1, 1, color="red", label="Goal"))

        # Draw the path if it exists
        if self.path_found:
            for i in range(len(self.path_found) - 1):
                current = self.path_found[i]
                next_node = self.path_found[i + 1]

                # Extract coordinates from GridNode
                current_x, current_y = current.x, rows - current.y - 1
                next_x, next_y = next_node.x, rows - next_node.y - 1

                # Plot the path
                ax.plot(
                    [current_x + 0.5, next_x + 0.5],
                    [current_y + 0.5, next_y + 0.5],
                    color="blue",
                    linewidth=2,
                    label="Path" if i == 0 else None,
                )

        # Set grid lines
        ax.set_xticks(range(cols))
        ax.set_yticks(range(rows))
        plt.xticks(rotation=90)
        ax.grid(True)

        # Set axis limits and labels
        ax.set_xlim(0, cols)
        ax.set_ylim(0, rows)
        ax.set_aspect("equal")
        ax.set_title("Pathfinding Visualization with Scores")
        ax.legend(loc="upper right")

        # Show the plot
        plt.show()
