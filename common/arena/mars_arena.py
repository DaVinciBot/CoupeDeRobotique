class MarsArena(Arena):
    """Represent the arena of the CDR 2023-2024"""

    def __init__(self, start_zone: int):
        """
        Generate the arena of the CDR 2023-2024

        :param start_zone: The start zone of the robot, must be between 1 and 6
        :type start_zone: int
        :raises ValueError: If start_zone is not between 1 and 6
        """
        if not (start_zone >= 1 and start_zone <= 6):
            raise ValueError("start_zone must be between 1 and 6")
        origin = Point(0, 0)
        opposite_corner = Point(200, 300)
        zones = [
            Rectangle(Point(0, 0), Point(45, 45)),  # 1 - Blue (Possible forbidden area)
            Rectangle(Point(77.5, 0), Point(122.5, 45)),  # 2 - Yellow
            Rectangle(Point(155, 0), Point(200, 45)),  # 3 - Blue
            Rectangle(
                Point(0, 255), Point(45, 300)
            ),  # 4 - Yellow (Possible forbidden area)
            Rectangle(Point(77.5, 255), Point(122, 300)),  # 5 - Blue
            Rectangle(Point(155, 255), Point(200, 300)),  # 6 - Yellow
        ]
        self.color = "yellow" if start_zone % 2 == 0 else "blue"
        super().__init__(
            area=Rectangle(origin, opposite_corner),
            forbidden_area=zones[(start_zone % 2) * 3],
            home=zones[start_zone - 1],
        )

    def __str__(self) -> str:
        return "MarsArena"

    def display(self) -> str:
        return f"""MarsArena: \n
        \tArea : {self.area}
        \tForbidden area : {self.forbidden_area}
        \tHome : {self.home}
        """
