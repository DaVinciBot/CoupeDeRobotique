from bot.Shapes import Point, Rectangle, Circle, OrientedPoint
from typing import Union

class Arena:
    """Represent an arena"""

    def __init__(
        self,
        area: Rectangle = Rectangle(Point(200, 0), Point(0, 300)),
        forbidden_area: Rectangle = Rectangle(Point(0, 0), Point(0, 0)),
        home: Rectangle = Rectangle(Point(0, 0), Point(0, 0)),
    ):
        if (
            not isinstance(area, Rectangle)
            or not isinstance(forbidden_area, Rectangle)
            or not isinstance(home, Rectangle)
        ):
            raise TypeError("Arguments must be Rectangle")
        self.area = area
        self.forbidden_area = forbidden_area
        self.home = home

    def is_in(self, point: Point) -> bool:
        """Check if a point is in the arena

        Args:
            point (Point): The point to check

        Returns:
            bool: True if the point is in the arena, False otherwise
        """
        return self.area.is_in(point)

    def is_in_forbidden_area(self, point: Point) -> bool:
        return self.forbidden_area.is_in(point)

    def enable_go_to(
        self,
        starting_point: Point,
        destination_point: Point,
        robot_width: int = 0,
        robot_length: int = 0,
    ) -> bool:
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

        # verify that the point is in the arena and do not collide with boarders
        distance = robot_length / 2
        valid_area = Rectangle(
            Point(self.area.corner.x-distance, distance),
            Point(distance,self.area.opposite_corner.y - distance)
            )
        if not valid_area.is_in(destination_point):
            return False

        # check if go_to describe an horizontal or vertical line
        if destination_point.x == starting_point.x:  # line = |
            # Check for collisions with the forbidden area
            if (
                destination_point.x <= self.forbidden_area.corner.x
                and destination_point.x >= self.forbidden_area.opposite_corner.x
            ):
                return False
            elif (
                destination_point.x - robot_width <= self.forbidden_area.corner.x
                and destination_point.x - robot_width
                >= self.forbidden_area.opposite_corner.x
            ):
                return False
            elif (
                destination_point.x + robot_width <= self.forbidden_area.corner.x
                and destination_point.x + robot_width
                >= self.forbidden_area.opposite_corner.x
            ):
                return False
            else:
                return True
        if destination_point.y == starting_point.y:  # line = --
            # Check for collisions with the forbidden area
            if (
                destination_point.y >= self.forbidden_area.corner.y
                and destination_point.y <= self.forbidden_area.opposite_corner.y
            ):
                return False
            elif (
                destination_point.y - robot_width >= self.forbidden_area.corner.y
                and destination_point.y - robot_width
                <= self.forbidden_area.opposite_corner.y
            ):
                return False
            elif (
                destination_point.y + robot_width >= self.forbidden_area.corner.y
                and destination_point.y + robot_width
                <= self.forbidden_area.opposite_corner.y
            ):
                return False
            else:
                return True
        # get the equation of the center straight line
        a = (destination_point.y - starting_point.y) / (
            destination_point.x - starting_point.x
        )
        b = destination_point.y - a * destination_point.x
        b2 = b - robot_width / 2
        b3 = b + robot_width / 2
        # given the folowing restricted area :
        # BC
        # AD
        # Calculate collision points between the center line and the forbidden area's sides
        c1 = Point(
            self.forbidden_area.corner.x,
            a * self.forbidden_area.corner.x + b,
        )  # collision point between center line and AB
        c2 = Point(
            (self.forbidden_area.opposite_corner.y - b) / a,
            self.forbidden_area.opposite_corner.y,
        )  # collision point between center line and BC
        c3 = Point(
            self.forbidden_area.opposite_corner.x,
            a * self.forbidden_area.opposite_corner.x + b,
        )  # collision point between center line and CD
        c4 = Point(
            (self.forbidden_area.corner.y - b) / a,
            self.forbidden_area.corner.y,
        )  # collision point between center line and CD
        # Check for collisions
        if (
            self.forbidden_area.is_in(c1)
            or self.forbidden_area.is_in(c2)
            or self.forbidden_area.is_in(c3)
            or self.forbidden_area.is_in(c4)
        ):
            return False
            
        # Calculate collision points between the right side line and the forbidden area's sides
        c1 = Point(
            self.forbidden_area.corner.x,
            a * self.forbidden_area.corner.x + b2,
        )  # collision point between right side line and AB
        c2 = Point(
            (self.forbidden_area.opposite_corner.y - b2) / a,
            self.forbidden_area.opposite_corner.y,
        )  # collision point between right side line and BC
        c3 = Point(
            self.forbidden_area.opposite_corner.x,
            a * self.forbidden_area.opposite_corner.x + b2,
        )  # collision point between right side line and CD
        c4 = Point(
            (self.forbidden_area.corner.y - b2) / a,
            self.forbidden_area.corner.y,
        )  # collision point between right side line and CD
        # Check for collisions
        if (
            self.forbidden_area.is_in(c1)
            or self.forbidden_area.is_in(c2)
            or self.forbidden_area.is_in(c3)
            or self.forbidden_area.is_in(c4)
        ):
            return False
        # Calculate collision points between the left side line and the forbidden area's sides
        c1 = Point(
            self.forbidden_area.corner.x,
            a * self.forbidden_area.corner.x + b3,
        )  # collision point between left side line and AB
        c2 = Point(
            (self.forbidden_area.opposite_corner.y - b3) / a,
            self.forbidden_area.opposite_corner.y,
        )  # collision point between left side line and BC
        c3 = Point(
            self.forbidden_area.opposite_corner.x,
            a * self.forbidden_area.opposite_corner.x + b3,
        )  # collision point between left side line and CD
        c4 = Point(
            (self.forbidden_area.corner.y - b3) / a,
            self.forbidden_area.corner.y,
        )  # collision point between left side line and CD
        # Check for collisions
        if (
            self.forbidden_area.is_in(c1)
            or self.forbidden_area.is_in(c2)
            or self.forbidden_area.is_in(c3)
            or self.forbidden_area.is_in(c4)
        ):
            return False
        return True
            
    def __str__(self) -> str:
        return "Arena"
    
    def display(self)->str:
        return f"""{self.__str__}: \n
        \tArea : {self.area}
        \tForbidden area : {self.forbidden_area}
        \tHome : {self.home}
        """


class MarsArena(Arena):
    """Represent the arena of the CDR 2023-2024"""

    def __init__(self, start_zone: int):
        """
        Generate the arena of the CDR 2023-2024

        :param start_zone: The start zone of the robot, must be between 1 and 6
        :type start_zone: int
        :raises ValueError: If start_zone is not between 1 and 6
        """
        if not (start_zone >= 0 and start_zone <= 5):
            raise ValueError("start_zone must be between 0 and 5")
        origin = Point(200, 0)
        opposite_corner = Point(0, 300)
        
        # (zone,is_full)
        self.gardeners = [
            (Rectangle(Point(77.5,-15), Point(45,-3)),False),  # 0 - Blue
            (Rectangle(Point(155,-15), Point(122.5,-3)),False),  # 1 - Yellow
            (Rectangle(Point(77.5,303), Point(45,315)),False),  # 2 - Blue
            (Rectangle(Point(155,303), Point(122.5,315)),False),  # 3 - Yellow
        ]

        # (zone,still_plants)
        self.plant_areas = [
            (Circle(Point(70,100),250),True),
            (Circle(Point(130,100),250),True),
            (Circle(Point(150,150),250),True),
            (Circle(Point(130,200),250),True),
            (Circle(Point(70,200),250),True),
            (Circle(Point(50,150),250),True)
        ]
        
        # (zone,is_full)
        self.drop_zones = [
            (Rectangle(Point(45, 0), Point(0, 45)),False),  # 0 - Blue (Possible forbidden area)
            (Rectangle(Point(122.5, 0), Point(77.5, 45)),False),  # 1 - Yellow
            (Rectangle(Point(200, 0), Point(155, 45)),False),  # 2 - Blue
            (Rectangle(Point(45, 255), Point(0, 300)),False),  # 3 - Yellow (Possible forbidden area)
            (Rectangle(Point(122, 255), Point(77.5, 300)),False),  # 4 - Blue
            (Rectangle(Point(200, 255), Point(155, 300)),False)  # 5 - Yellow
        ]
        self.color = "blue" if start_zone % 2 == 0 else "yellow"
        super().__init__(
            area=Rectangle(origin, opposite_corner),
            forbidden_area=self.drop_zones[(start_zone % 2) * 3][0],
            home=self.drop_zones[start_zone - 1][0],
        )

    def __str__(self) -> str:
        return "MarsArena"
    
    def is_our_zone(self, zone, zones )->bool:
        """this function tells wether the given zone is in zones and that it is ours 

        Args:
            zone (_type_): the zone to serch for
            zones (list[(type(zone),bool)]): the list of zones to serch in. 

        Returns:
            bool: is zone in zones
        """
        for i in range(0,len(zones)):
            if zones[i][0]==zone:
                if self.color == "blue": return i%2 == 0
                else: return i%2 != 0
                

    def display(self)->str:
        return f"""{self.__str__}: \n
        \tArea : {self.area}
        \tForbidden area : {self.forbidden_area}
        \tHome : {self.home}
        """