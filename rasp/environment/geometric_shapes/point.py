import math
class Point:
    
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y
    
    def __add__(self, p : object) -> object:
        return Point(self.x+p.x, self.y+p.y)
    
    def __sub__(self, p : object) -> object:
        return Point(self.x-p.x, self.y-p.y)

    def __str__(self) -> str:
        return f"Point(x={self.x}, y={self.y})"
    
    def __eq__(self, p : object) -> bool:
        if isinstance(p,Point): return self.x == p.x and self.y == p.y
        else: return super().__eq__(p)
        
    @staticmethod
    def get_distance(p1, p2, nb_digits : int =2):
        """return the distance betwen the two gien points

        Args:
            p1 (Point)
            p2 (Point)
            nb_digits (int, optional): the requiered number of digits after the decimal point. Defaults to 2.

        Returns:
            float : distance between points
        """
        return round(math.sqrt((p1.x-p2.x)*(p1.x-p2.x)+(p1.y-p2.y)*(p1.y-p2.y)),nb_digits)
    
    def get_distance(self, p2, nb_digits : int =2):
        """return the distance betwen the given point an itself

        Args:
            p2 (Point): the point to compare to
            nb_digits (int, optional): the requiered number of digits after the decimal point . Defaults to 2.

        Returns:
            float: distance between points
        """
        return round(math.sqrt((self.x-p2.x)*(self.x-p2.x)+(self.y-p2.y)*(self.y-p2.y)),nb_digits)