from bot.Shapes import Point,OrientedPoint,Rectangle,Circle
from typing import Union

def compute_go_to_destination(actual_position : OrientedPoint, __object : object,  distance = 0, nb_digits : int = 0)->Union[OrientedPoint,bool]:
    def compute_detination(destination_point : OrientedPoint):
        if(destination_point.y == actual_position.y):
            if destination_point.x>actual_position.x: # compute wether the starting point is on the  bottom or on the top of the robot
                return destination_point-OrientedPoint(distance,0)
            return destination_point+OrientedPoint(distance,0)
        if(destination_point.x == actual_position.x): # compute wether the starting point is on the left or on the right of the robot
            if destination_point.y>actual_position.y:
                return destination_point-OrientedPoint(0,distance)
            return destination_point+OrientedPoint(0,distance)
        a = (destination_point.y - actual_position.y) / (destination_point.x - actual_position.x)
        b = destination_point.y - a *destination_point.x
        delta = 4 * (a**2) * (b**2) - 4 * (1 + a**2) * (b**2 - distance**2)
        if delta<0:
            return False
        p1 = (-2*a*b-delta)**(1/2)/(2*(1+a**2))
        p2 = (-2*a*b-delta)**(1/2)/(2*(1+a**2))
        if destination_point.get_distance(p1)<= destination_point.get_distance(p2): return p1
        return p2
    if isinstance(__object, (Rectangle,Circle)):
        if distance == 0: return __object.center
        arrival = compute_detination(__object.center)
        arrival.__round__(nb_digits)
        return arrival
    if isinstance(__object,OrientedPoint):
        if distance == 0 : return __object
        arrival = compute_detination(__object)
        arrival.__round__(nb_digits)
        return arrival
    if isinstance(__object,Point):
        if distance ==0 : return __object.to_OrientedPoint()
        arrival : OrientedPoint = compute_detination(__object)
        arrival.__round__(nb_digits)
        return arrival
    return False