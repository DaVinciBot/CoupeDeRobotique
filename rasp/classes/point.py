class point:
    
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

    def __add__(self,other):
        self.x+=other.x
        self.y+=other.y

    def __str__(self):
        return f"Point(x={self.x}, y={self.y})"