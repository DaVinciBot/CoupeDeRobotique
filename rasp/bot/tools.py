from bot.Shapes import Point,OrientedPoint,Rectangle,Circle
from typing import Union

def compute_go_to_destination(actual_position : OrientedPoint, __object : object,  distance = 0, nb_digits : int = 2, closer = True)->Union[OrientedPoint,bool]:
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
        c = 1+a**2
        d = 2*(-destination_point.x+a*(b-destination_point.y))
        e = destination_point.x**2+(b-destination_point.y)**2-distance**2
        delta = d**2-4*c*e
        if delta<0:
            return False
        x1 = (-d-delta**(1/2))/(2*c)
        x2 = (-d+delta**(1/2))/(2*c)
        p1 = OrientedPoint(x1,a*x1+b)
        p2 = OrientedPoint(x2,a*x2+b)
        if closer:
            if actual_position.get_distance(p1) < actual_position.get_distance(p2): return p1
            return p2
        else:
            if actual_position.get_distance(p1) > actual_position.get_distance(p2): return p1
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