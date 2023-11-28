import math
class point:
    
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

    def __add__(self,other):
        return point(self.x+other.x, self.y+other.y)

    def __str__(self):
        return f"Point(x={self.x}, y={self.y})"
    
    @staticmethod
    def get_distance(p1, p2):
        return math.sqrt((p1.x-p2.x)*(p1.x-p2.x)+(p1.y-p2.y)*(p1.y-p2.y))