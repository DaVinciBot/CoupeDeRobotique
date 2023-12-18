from environment.geometric_shapes.point import Point

class OrientedPoint(Point):
    def __init__(self, x: float, y: float, theta : float = 0):
        super().__init__(x, y)
        self.theta = theta

    def __add__(self, p : object) -> object:
        return OrientedPoint(self.x+p.x, self.y+p.y, self.theta+p.theta)
    
    def __sub__(self, p : object) -> object:
        return OrientedPoint(self.x-p.x, self.y-p.y, self.theta-p.theta)
    
    def __str__(self) -> str:
        return f"Point(x={self.x}, y={self.y}, theta={self.theta})"
 