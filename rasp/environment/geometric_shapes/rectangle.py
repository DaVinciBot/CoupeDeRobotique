import math
import sys
from . import point as p
class Rectangle:
    
    def __init__(self, corner : p.Point, opposite_corner : p.Point):
        """Creates a new instance of rectangle. Corner must be the point at the bottom left corner from the origin and opposite_corner the top right corner. Therfore corner.x must be higer than opposite_corner.x, same for y

        Args:
            corner (p.Point): bottom left corner from the origin
            opposite_corner (p.Point): top right corner
        """
        if self.verified_params(corner , opposite_corner):
            self.corner = corner
            self.opposite_corner = opposite_corner
            self.center = p.Point((corner.x+opposite_corner.x)/2.0, (corner.y+opposite_corner.y)/2.0)
        else:
            self.corner = None
    
    def verified_params(self, corner : p.Point, opposite_corner : p.Point) -> bool:
        are_respected_coordinates = True
        if corner.x > opposite_corner.x or corner.y > opposite_corner.y:
            print(f"corner.x must be lower or equal than oppositer corner.x, same for y")
            are_respected_coordinates = False
        return  are_respected_coordinates
    
    def __str__(self):
        if self.corner == None:
            return "Rectangle None"
        else: return f"Rectangle :(corner = {self.corner.__str__()},opposite_corner = {self.opposite_corner.__str__()},center : {self.center.__str__()}"

    def get_distance_between_centers(self, r, nb_digits: int = 2) -> float:
        """return the distance between its center and the center of another rectangle

        Args:
            r (Rectangle): the rectangle to compare too
            nb_digits (int, optional): the requiered number of digits after the decimal point. Defaults to 2.

        Returns:
            float: distance between centers, -1 if one is None
        """
        if(self==None): return -1
        else:
            return round(p.Point.get_distance(self.center, r.center), nb_digits)
        
    def is_in(self, point : p.Point) -> bool:
        return point.x<=self.opposite_corner.x and point.y<=self.opposite_corner.y and point.x>=self.corner.x and point.y>= self.corner.y

