from path_finding.motions import Motions
from path_finding.node import Node, InconsistentNode
from path_finding.grid import Grid
from path_finding.key import Key
from path_finding.priority_queue import Priority, PriorityNode, PriorityQueue
import math
import numpy as np


class PathFinder:
    def __init__(self, motions: Motions, initial_grid: np.ndarray, start: tuple[int, int], goal: tuple[int, int]):
        # Create a grid
        self.grid = Grid(initial_grid, motions, start, goal)

        self.km = 0.0

        self.opens: list[Node] = []
        # Start by adding the goal to the opens list, it is inconsistent because g = inf and rhs = 0
        self.opens.insert(0, Node(coords=goal, cost=0.0, key=self.calculate_key(goal)))

    def update_grid(self, coords: tuple[int, int]):
        # If the node is not the goal, update its rhs value
        if coords != self.grid.goal:
            # Update its RHS value to the minimum of the cost to reach its neighbors + their g value
            self.grid.update_rhs(coords)

        # If the node is in the opens list, remove it
        for node in self.opens:
            if node.coords == coords:
                self.opens.remove(node)
                break

        # If the node is inconsistent, add it to the opens list
        if self.grid.g[coords] != self.grid.rhs[coords]:
            self.opens.append(Node(coords=coords, cost=0.0, key=self.calculate_key(coords)))

    def find_shortest_path(self):
        while len(self.opens) and self.opens[0].coords != self.grid.start:
            self.opens.sort(key=lambda x: x.coords)  # Sort the opens list by coordinates
            top_open = self.opens[0]
            self.opens.pop(0)  # Remove the top element that we are going to work on

            if top_open.key < self.calculate_key(top_open.coords):
                self.opens.append(
                    Node(coords=top_open.coords, cost=0.0, key=self.calculate_key(top_open.coords))
                )

            # It is over-consistent ? (g > rhs) --> g = rhs
            elif self.grid.is_over_consistent(top_open.coords):
                self.grid.g[top_open.coords] = self.grid.rhs[top_open.coords]

                # Update the neighbors
                for neighbor in self.grid.get_neighbors(top_open.coords):
                    self.update_grid(neighbor.coords)

            else:
                self.grid.g[top_open.coords] = float("-inf")
                # Update the neighbors of the open (the current top open node including)
                for neighbor in self.grid.get_neighbors(top_open.coords) + [top_open]:
                    self.update_grid(neighbor.coords)

        self.km += 1

    def compute_current_path(self):
        path = []
        current_point = Node(coords=self.grid.start)
        while current_point.coords != self.grid.goal:
            path.append(current_point)

            current_point = min(
                self.grid.get_neighbors(current_point.coords),
                key=lambda z: self.grid.cost(current_point.coords, z.coords) + self.grid.g[z.coords]
            )
        path.append(Node(coords=self.grid.goal))

        return path

    def update_obstacle(self, obstacles_to_add: list[tuple[int, int]] = [], obstacles_to_remove: list[tuple[int, int]] = []):
        for obstacle in obstacles_to_add:
            self.grid.g[obstacle] = float("+inf")
            self.grid.rhs[obstacle] = float("+inf")
            self.update_grid(obstacle)

        for obstacle in obstacles_to_remove:
            self.grid.g[obstacle] = float("-inf")
            self.grid.rhs[obstacle] = float("-inf")
            self.update_grid(obstacle)

    def get_optimized_path(self):
        """
        Optimize the path by removing unnecessary nodes.
        """
        path = self.compute_current_path()
        path = [p.coords for p in path]
        if len(path) < 3:
            return path

        filtered_path = [path[0]]

        for i in range(1, len(path) - 1):
            prev, current, next = path[i - 1], path[i], path[i + 1]

            dx1 = current[0] - prev[0]
            dy1 = current[1] - prev[1]
            dx2 = next[0] - current[0]
            dy2 = next[1] - current[1]

            cross_product = dx1 * dy2 - dy1 * dx2

            if cross_product != 0:
                filtered_path.append(current)

        filtered_path.append(path[-1])
        return filtered_path

    @staticmethod
    def heuristic(a: tuple[int, int], b: tuple[int, int]) -> float:
        """
        Helper function to compute distance between two points.
        :param a: (x,y)
        :param b: (x,y)
        :return: manhattan distance
        """
        return math.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2)

    def calculate_key(self, coords: tuple[int, int]) -> Key:
        """
        Calculate the key for a given coordinates.
        Primary key: min(g, rhs) + heuristic + km
        Secondary key: min(g, rhs)
        """
        k1 = min(self.grid.g[coords], self.grid.rhs[coords]) + self.heuristic(self.grid.start, coords) + self.km
        k2 = min(self.grid.g[coords], self.grid.rhs[coords])
        return Key(k1, k2)
