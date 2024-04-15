import numpy as np
from path_finding.node import Node
from path_finding.motions import Motions
import math

class Grid:
    def __init__(self, boolean_grid: np.ndarray, motions: Motions, start: tuple[int, int], goal: tuple[int, int]):
        """
        Initialize the grid by given a grid of boolean values.
        False -> forbidden
        True -> authorized
        """
        # Transform the grid to 2 list -> g and rhs, same size as the grid
        # -inf for all authorized cells
        # +inf for all non-authorized cells
        self.g = np.where(boolean_grid, float("+inf"), float("-inf"))
        # self.g = np.where(boolean_grid, float("+inf"), float("+inf"))
        self.rhs = self.g.copy()

        # Set the rhs goal to 0
        self.start = start
        self.goal = goal
        self.rhs[goal] = 0.0

        self.motions = motions  # All possible motions of the robot with their cost

    def valid_coords(self, x: int, y: int) -> bool:
        """
        Check if the given coordinates are valid. (inside the grid)
        I use g here, but it could be rhs as well.
        """
        return 0 <= x < self.g.shape[0] and 0 <= y < self.g.shape[1]

    def get_neighbors(self, coords: tuple[int, int]) -> list[Node]:
        """
        Get the neighbors of a given cell.
        """
        node = Node(coords=coords)
        neighbors = []
        for motion in self.motions:
            if self.valid_coords(node.x + motion.x, node.y + motion.y):
                neighbors.append(node + motion)
        return neighbors

    def cost(self, u: tuple[int, int], v: tuple[int, int]) -> float:
        """
        calculate the cost between 2 cases u and v
        :param u: from vertex
        :param v: to vertex
        :return: euclidean distance to traverse. inf if obstacle in path
        """
        # Infinite cost if u or v is an obstacle
        if self.g[u] == float('+inf') or self.g[v] == float('+inf'):
            return float('+inf')
        else:
            return self.heuristic(u, v)


    def is_over_consistent(self, coords: tuple[int, int]) -> bool:
        """
        Check if the given coordinates are over-consistent (g > rhs).
        (TODO: not sur --> return false if it is an obstacle (forbidden cell). They are modelized as +inf in g and rhs.)
        --> return true if g and rhs are -inf (default authorized cell values)
        """
        # If is a default authorized cell which is over-consistent
        if self.g[coords] == float("-inf") and self.rhs[coords] != float("-inf"):
            return True
        return self.g[coords] > self.rhs[coords]

    def is_under_consistent(self, coords: tuple[int, int]) -> bool:
        """
        Check if the given coordinates are under-consistent (g < rhs).
        TODO: Not sur of this part ! Better to just not pop element ? Is it usefull to recompute the key ?
        """
        return self.g[coords] < self.rhs[coords]

    @staticmethod
    def heuristic(a: tuple[int, int], b: tuple[int, int]) -> float:
        """
        Helper function to compute distance between two points.
        :param a: (x,y)
        :param b: (x,y)
        :return: manhattan distance
        """
        return math.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2)

    def update_rhs(self, coords: tuple[int, int]):
        # Update its RHS value to the minimum of the cost to reach its neighbors + their g value
        predecessors_cost = []
        for neighbor in self.get_neighbors(coords):
            # If default authorized cell
            if self.g[neighbor.coords] == float("-inf"):
                predecessors_cost.append(self.cost(coords, neighbor.coords) + float("+inf"))
            else:
                predecessors_cost.append(self.cost(coords, neighbor.coords) + self.g[neighbor.coords])

        self.rhs[coords] = min(predecessors_cost)
