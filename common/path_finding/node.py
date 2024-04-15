from path_finding.key import Key


class Node:
    def __init__(self, x: int = 0, y: int = 0, cost: float = 0.0, key: Key = None, coords: tuple[int, int] = None):
        if coords:
            x, y = coords
        self.x = x
        self.y = y
        self.cost = cost
        self.key = key

    """
    def __eq__(self, other):
        return self.x == other.x and self.y == other.y and self.cost == other.cost

    """

    def __add__(self, other):
        return Node(self.x + other.x, self.y + other.y, self.cost + other.cost)

    @property
    def coords(self) -> tuple[int, int]:
        return self.x, self.y


class InconsistentNode:
    def __init__(self, x: int, y: int, key: Key):
        self.x = x
        self.y = y
        self.key = key

    @property
    def coords(self) -> tuple[int, int]:
        return self.x, self.y
