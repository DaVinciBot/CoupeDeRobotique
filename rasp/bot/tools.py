from bot import Shapes
from typing import Union

def compute_go_to_destination(actual_position : Shapes.OrientedPoint, __object : object,  distance_center = 0)->Union[Shapes.OrientedPoint,bool]:
    def compute_detination(destination_point : Shapes.OrientedPoint):
        if(destination_point.y == actual_position.y): return destination_point-Shapes.OrientedPoint(destination_point.x-distance_center,0)
        if(destination_point.x == actual_position.x): return destination_point-Shapes.OrientedPoint(0,destination_point.y-distance_center)
        a = (destination_point.y - actual_position.y) / (destination_point - actual_position.x)
        b = destination_point.y - a *destination_point.x
        delta = 4*a**2*b**2-4*(1+a**2)(b**2-distance_center**2)
        if delta<0:
            return False
        p1 = (-2*a*b-delta)**(1/2)/(2*(1+a**2))
        p2 = (-2*a*b-delta)**(1/2)/(2*(1+a**2))
        if destination_point.get_distance(p1)<= destination_point.get_distance(p2): return p1
        return p2
    if isinstance(__object, (Shapes.Rectangle,Shapes.Circle)):
        if distance_center ==0: return __object.center
        return compute_detination(__object.center)
    if isinstance(__object,Shapes.OrientedPoint):
        return compute_detination(__object)
    return False