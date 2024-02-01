import math


class Point:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

    def __add__(self, p: object) -> object:
        return Point(self.x + p.x, self.y + p.y)

    def __sub__(self, p: object) -> object:
        return Point(self.x - p.x, self.y - p.y)

    def __str__(self) -> str:
        return f"Point(x={self.x}, y={self.y})"

    def __eq__(self, p: object) -> bool:
        if isinstance(p, Point):
            return self.x == p.x and self.y == p.y
        else:
            return super().__eq__(p)

    @staticmethod
    def get_distance(p1, p2, nb_digits: int = 2):
        """return the distance betwen the two given points

        Args:
            p1 (Point)
            p2 (Point)
            nb_digits (int, optional): the requiered number of digits after the decimal point. Defaults to 2.

        Returns:
            float : distance between points
        """
        return round(
            math.sqrt((p1.x - p2.x) * (p1.x - p2.x) + (p1.y - p2.y) * (p1.y - p2.y)),
            nb_digits,
        )

    def get_distance(self, p2, nb_digits: int = 2):
        """return the distance betwen the given point an itself

        Args:
            p2 (Point): the point to compare to
            nb_digits (int, optional): the requiered number of digits after the decimal point . Defaults to 2.

        Returns:
            float: distance between points
        """
        return round(
            math.sqrt(
                (self.x - p2.x) * (self.x - p2.x) + (self.y - p2.y) * (self.y - p2.y)
            ),
            nb_digits,
        )


class OrientedPoint(Point):
    """
    Oriented point, inherits from Point, use to represent destination points
    """
    def __init__(self, x: float, y: float, theta: float = 0):
        super().__init__(x, y)
        self.theta = theta

    def __add__(self, p: object) -> object:
        return OrientedPoint(self.x + p.x, self.y + p.y, self.theta + p.theta)

    def __sub__(self, p: object) -> object:
        return OrientedPoint(self.x - p.x, self.y - p.y, self.theta - p.theta)

    def __str__(self) -> str:
        return f"Point(x={self.x}, y={self.y}, theta={self.theta})"


class Circle:
    def __init__(self, center: Point, radius: float):
        if type(center) != Point:
            raise TypeError("center must be a Point")
        self.center = center
        self.radius = radius

    def __str__(self) -> str:
        return f"Circle(\n\tcenter : {self.center}\n\tradius : {self.radius})"


class Rectangle:
    def __init__(self, corner: Point, opposite_corner: Point):
        """Creates a new instance of rectangle. Corner must be the point at the bottom left corner from the origin and opposite_corner the top right corner. Therfore corner.x must be higer than opposite_corner.x, same for y

        Args:
            corner (Point): bottom left corner from the origin
            opposite_corner (Point): top right corner
        """
        if not self.are_valid(corner, opposite_corner):
            raise ValueError("Corner and opposite_corner are not valid")
        self.corner = corner
        self.opposite_corner = opposite_corner
        self.center = Point(
            (corner.x + opposite_corner.x) / 2.0,
            (corner.y + opposite_corner.y) / 2.0,
        )

    def are_valid(self, corner: Point, opposite_corner: Point) -> bool:
        return not (corner.x > opposite_corner.x or corner.y > opposite_corner.y)

    def __str__(self):
        return f"Rectangle(corner = {self.corner.__str__()},opposite_corner = {self.opposite_corner.__str__()},center = {self.center.__str__()})"

    def get_distance_between_centers(self, r, nb_digits: int = 2) -> float:
        """return the distance between its center and the center of another rectangle

        Args:
            r (Rectangle): the rectangle to compare
            nb_digits (int, optional): the requiered number of digits after the decimal point. Defaults to 2.

        Returns:
            float: distance between centers, -1 if one is None
        """
        return round(Point.get_distance(self.center, r.center), nb_digits)

    def is_in(self, point: Point) -> bool:
        return (
            point.x <= self.opposite_corner.x
            and point.y <= self.opposite_corner.y
            and point.x >= self.corner.x
            and point.y >= self.corner.y
        )
