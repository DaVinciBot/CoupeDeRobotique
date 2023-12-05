from geometric_shapes.point import Point
from geometric_shapes.rectangle import Rectangle

class Arena:
    """Represent an arena
    """
    def __init__(self, origin : Point = Point(0,0), opposite_corner : Point = Point(200,300), forbidden_area : Rectangle = Rectangle(Point(0,0),Point(0,0)), home : Rectangle = Rectangle(Point(0,0),Point(0,0))):
        self.origin = origin
        self.opposite_corner = opposite_corner
        self.forbidden_area = forbidden_area
        self.home = home

    def __str__(self) -> str:
        return(
            "MarsArena :\n"
            f"\thome.center : {self.home.center.__str__()}\n"
            f"\torigin : {self.origin.__str__()}\n"
            f"\topposite corner : {self.opposite_corner.__str__()}\n"
            f"\trival_protected_depot_zone : {self.rival_protected_depot_zone.__str__()}\n"
            "\tplants_zone :\n"
            "\town_protected_gardeners : \n"
            "\town_gardeners\n : "
            "\town_protected_depot_zone : \n"
            "\town_depot_zone : "
        )

    def is_in(self, point : Point) -> bool:
        try : return point.x<=self.opposite_corner.x and point.y<=self.opposite_corner.y and point.x>=self.origin.x and point.y>= self.origin.y
        except : raise Exception("arena isn't correctly initialized")
        
    def is_in_forbidden_area(self, point : Point) -> bool:
        try : return self.forbidden_area.is_in(point)
        except :
            raise Exception("arena isn't correctly initialized")
        
    def enable_go_to(self, starting_point : Point, destination_point : Point, robot_width : int = 0, robot_length : int = 0) -> bool:
        """this function checks if a given straight line move can be made into the arena. It avoid collisions with the boarders and the forbidden area.
            takes into account the width and the length of the robot 

        Args:
            starting_point (Point): _description_
            destination_point (Point): _description_
            robot_width (int, optional): _description_. Defaults to 22.
            robot_length (int, optional): _description_. Defaults to 31.

        Raises:
            Exception: _description_

        Returns:
            bool: _description_
        """
        try :
            if(self.forbidden_area!= None):
                # verify that the point is in the arena and do not collide with boarders
                distence = robot_length/2
                restricted_area = Rectangle(Point(distence,distence),Point(self.opposite_corner.x-distence, self.opposite_corner.y-distence))
                if(restricted_area.is_in(destination_point)): # maybe not always valid
                    # check if go_to describe an horizontal or vertical line
                    if(destination_point.x == starting_point.x): # line = |
                        # Check for collisions with the forbidden area
                        if(destination_point.x>=self.forbidden_area.corner.x and destination_point.x<=self.forbidden_area.opposite_corner.x):
                            return False
                        elif(destination_point.x-robot_width>=self.forbidden_area.corner.x and destination_point.x-robot_width<=self.forbidden_area.opposite_corner.x):
                            return False
                        elif(destination_point.x+robot_width>=self.forbidden_area.corner.x and destination_point.x+robot_width<=self.forbidden_area.opposite_corner.x):
                            return False
                        else:
                            return True
                    if(destination_point.y == starting_point.y): # line = --
                        # Check for collisions with the forbidden area
                        if(destination_point.y>=self.forbidden_area.corner.y and destination_point.y<=self.forbidden_area.opposite_corner.y):
                            return False
                        elif(destination_point.y-robot_width>=self.forbidden_area.corner.y and destination_point.y-robot_width<=self.forbidden_area.opposite_corner.y):
                            return False
                        elif(destination_point.y+robot_width>=self.forbidden_area.corner.y and destination_point.y+robot_width<=self.forbidden_area.opposite_corner.y):
                            return False
                        else : 
                            return True
                    # get the equation of the center straight line
                    a = (destination_point.y-starting_point.y)/(destination_point.x-starting_point.x)
                    b = destination_point.y-a*destination_point.x
                    b2 = b-robot_width/2
                    b3 = b+robot_width/2
                    # given the folowing restricted area :
                    # BC
                    # AD
                    # Calculate collision points between the center line and the forbidden area's sides
                    c1 = Point(self.forbidden_area.corner.x,a*self.forbidden_area.corner.x+b) #collision point between center line and AB
                    c2 = Point((self.forbidden_area.opposite_corner.y-b)/a,self.forbidden_area.opposite_corner.y) #collision point between center line and BC
                    c3 = Point(self.forbidden_area.opposite_corner.x,a*self.forbidden_area.opposite_corner.x+b) #collision point between center line and CD
                    c4 = Point((self.forbidden_area.corner.y-b)/a,self.forbidden_area.corner.y) #collision point between center line and CD
                    # Check for collisions
                    if(self.forbidden_area.is_in(c1) or self.forbidden_area.is_in(c2) or self.forbidden_area.is_in(c3) or self.forbidden_area.is_in(c4)):
                        return False
                    # Calculate collision points between the right side line and the forbidden area's sides
                    c1 = Point(self.forbidden_area.corner.x,a*self.forbidden_area.corner.x+b2) #collision point between right side line and AB
                    c2 = Point((self.forbidden_area.opposite_corner.y-b2)/a,self.forbidden_area.opposite_corner.y) #collision point between right side line and BC
                    c3 = Point(self.forbidden_area.opposite_corner.x,a*self.forbidden_area.opposite_corner.x+b2) #collision point between right side line and CD
                    c4 = Point((self.forbidden_area.corner.y-b2)/a,self.forbidden_area.corner.y) #collision point between right side line and CD
                    # Check for collisions
                    if(self.forbidden_area.is_in(c1) or self.forbidden_area.is_in(c2) or self.forbidden_area.is_in(c3) or self.forbidden_area.is_in(c4)):
                        return False
                    # Calculate collision points between the left side line and the forbidden area's sides
                    c1 = Point(self.forbidden_area.corner.x,a*self.forbidden_area.corner.x+b3) #collision point between left side line and AB
                    c2 = Point((self.forbidden_area.opposite_corner.y-b3)/a,self.forbidden_area.opposite_corner.y) #collision point between left side line and BC
                    c3 = Point(self.forbidden_area.opposite_corner.x,a*self.forbidden_area.opposite_corner.x+b3) #collision point between left side line and CD
                    c4 = Point((self.forbidden_area.corner.y-b3)/a,self.forbidden_area.corner.y) #collision point between left side line and CD
                    # Check for collisions
                    if(self.forbidden_area.is_in(c1) or self.forbidden_area.is_in(c2) or self.forbidden_area.is_in(c3) or self.forbidden_area.is_in(c4)):
                        return False
                    return True
                else:
                    return False
        except : raise Exception("arena isn't correctly initialized")
            