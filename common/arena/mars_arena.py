from arena.arena import Arena
from geometry import Point, Polygon, create_straight_rectangle


class MarsArena(Arena):
    """Represent the arena of the CDR 2023-2024"""

    def __init__(self, start_zone: int):
        """
        Generate the arena of the CDR 2023-2024

        :param start_zone: The start zone of the robot, must be between 1 and 6
        :type start_zone: int
        :raises ValueError: If start_zone is not between 1 and 6
        """
        if not (1 <= start_zone <= 6):
            raise ValueError("start_zone must be between 1 and 6")

        origin = Point(0, 0)
        opposite_corner = Point(200, 300)

        self.color = "yellow" if start_zone % 2 == 0 else "blue"

        all_zones = [
            create_straight_rectangle(
                Point(0, 0), Point(45, 45)
            ),  # 1 - Blue (Possible forbidden area)
            create_straight_rectangle(
                Point(77.5, 0), Point(122.5, 45)
            ),  # 2 - Yellow
            create_straight_rectangle(Point(155, 0), Point(200, 45)),  # 3 - Blue
            create_straight_rectangle(
                Point(0, 255), Point(45, 300)
            ),  # 4 - Yellow (Possible forbidden area)
            create_straight_rectangle(
                Point(77.5, 255), Point(122, 300)
            ),  # 5 - Blue
            create_straight_rectangle(
                Point(155, 255), Point(200, 300)
            ),  # 6 - Yellow
        ]

        super().__init__(
            game_borders=create_straight_rectangle(origin, opposite_corner),
            zones={
                "forbidden": all_zones[(start_zone % 2) * 3],
                "home": all_zones[start_zone - 1],
            },
        )

    def __str__(self) -> str:
        return "MarsArena"

    def display(self) -> str:
        return f"""MarsArena: \n
        \tArea : {self.game_borders}
        \tForbidden area : {self.zones["forbidden"]}
        \tHome : {self.zones["home"]}
        """
