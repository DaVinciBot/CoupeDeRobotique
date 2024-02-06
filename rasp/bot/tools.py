from bot.Shapes import Point,OrientedPoint,Rectangle,Circle
from typing import Union

def compute_go_to_destination(actual_position : OrientedPoint, __object : object,  distance = 0, nb_digits : int = 2, closer = True)->Union[OrientedPoint,bool]:
    """ Given the actual position and a destination zone return the Oriented point to reach

    Args:
        actual_position (OrientedPoint): the actual position of the bot
        __object (object): the object to reach (OrientedPoint,Point,Rectangle,Circle)
        distance (int, optional): _description_. Defaults to 0. the returned OrientedPoint will be situated on a straight betwen the actual_position and the deffault oriented_point at distance cm from it
        nb_digits (int, optional): _description_. Defaults to 2. x and y number of decimal digits to return
        closer (bool, optional): _description_. Defaults to True. If True the returned OrientedPoint will be distance closer from actual_position than the default returned point. Ohterwise further

    Returns:
        Union[OrientedPoint,bool]: the OrientedPoint to reach or False if parameters are wrong
    """
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
        __object = __object.center.to_OrientedPOint()
        if distance == 0: return __object
        arrival = compute_detination(__object)
        arrival.__round__(nb_digits)
        return arrival
    if isinstance(__object,OrientedPoint):
        if distance == 0 : return __object
        arrival = compute_detination(__object)
        arrival.__round__(nb_digits)
        return arrival
    if isinstance(__object,Point):
        __object = __object.to_OrientedPOint()
        if distance ==0 : return __object
        arrival = compute_detination(__object)
        arrival.__round__(nb_digits)
        return arrival
    return False


def closest_zone(zone_bool,actual_position : OrientedPoint, our=True, exclude_not_basic=True, color = "blue", basic = False): # zone must math the format [zone,bool]
        if our:
            if color == "blue": s=0
            else : s=1
            zones = [zone_bool[i] for i in range(s,len(zone_bool),2)]
        else:
            zones = zone_bool
        if exclude_not_basic: return sorted(zones, key = lambda x:(x[1]!=basic,x[0].center.get_distance(actual_position))) # False before True
        return sorted(zones, key = lambda x:(x[0].center.get_distance(actual_position)))
