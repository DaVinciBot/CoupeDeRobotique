from geometry import Point, Rectangle


class Arena:
    """Represent an arena"""

    def __init__(
        self,
        area: Rectangle = Rectangle(Point(0, 0), Point(200, 300)),
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
            Point(distance, distance),
            Point(
                self.area.opposite_corner.x - distance,
                self.area.opposite_corner.y - distance,
            ),
        )
        if not valid_area.is_in(destination_point):
            return False

        # check if go_to describe an horizontal or vertical line
        if destination_point.x == starting_point.x:  # line = |
            # Check for collisions with the forbidden area
            if (
                destination_point.x >= self.forbidden_area.corner.x
                and destination_point.x <= self.forbidden_area.opposite_corner.x
            ):
                return False
            elif (
                destination_point.x - robot_width >= self.forbidden_area.corner.x
                and destination_point.x - robot_width
                <= self.forbidden_area.opposite_corner.x
            ):
                return False
            elif (
                destination_point.x + robot_width >= self.forbidden_area.corner.x
                and destination_point.x + robot_width
                <= self.forbidden_area.opposite_corner.x
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
