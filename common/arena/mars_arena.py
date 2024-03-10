from arena.arena import Arena
from geometry import (
    Point,
    Polygon,
    create_straight_rectangle,
    MultiPolygon,
    OrientedPoint,
)
from utils.tools import closest_zone


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

        class plants_zone:
            def __init__(self, zone, nb_plant: int = 0) -> None:
                self.zone = zone
                self.nb_plant = nb_plant

        self.drop_zones = [
            plants_zone(
                create_straight_rectangle(Point(45, 0), Point(0, 45))
            ),  # 1 - Blue (Possible forbidden area)
            plants_zone(
                create_straight_rectangle(Point(122.5, 0), Point(77.5, 45))
            ),  # 2 - Yellow
            plants_zone(
                create_straight_rectangle(Point(200, 0), Point(155, 45))
            ),  # 3 - Blue
            plants_zone(
                create_straight_rectangle(Point(45, 255), Point(0, 300))
            ),  # 4 - Yellow (Possible forbidden area)
            plants_zone(
                create_straight_rectangle(Point(122.5, 255), Point(77.5, 300))
            ),  # 5 - Blue
            plants_zone(
                create_straight_rectangle(Point(200, 255), Point(155, 300))
            ),  # 6 - Yellow
        ]

        self.pickup_zones = [
            plants_zone(Point(70, 100).buffer(250), 6),
            plants_zone(Point(130, 100).buffer(250), 6),
            plants_zone(Point(150, 150).buffer(250), 6),
            plants_zone(Point(130, 200).buffer(250), 6),
            plants_zone(Point(70, 200).buffer(250), 6),
            plants_zone(Point(50, 150).buffer(250), 6),
        ]

        self.gardeners = [
            (
                create_straight_rectangle(Point(77.5, -15), Point(45, -3)),
                False,
            ),  # 0 - Blue
            (
                create_straight_rectangle(Point(155, -15), Point(122.5, -3)),
                False,
            ),  # 1 - Yellow
            (
                create_straight_rectangle(Point(77.5, 303), Point(45, 315)),
                False,
            ),  # 2 - Blue
            (
                create_straight_rectangle(Point(155, 303), Point(122.5, 315)),
                False,
            ),  # 3 - Yellow
        ]

        def closest_gardener(
            self,
            actual_position: OrientedPoint,
            our=True,
            exclude_not_basic=True,
            basic=False,
        ):
            return closest_zone(
                zone_bool=self.gardeners,
                actual_position=actual_position,
                our=our,
                exclude_not_basic=exclude_not_basic,
                color=self.color,
                basic=basic,
            )

        def closest_drop_zone(
            self,
            actual_position: OrientedPoint,
            our=True,
            exclude_not_basic=True,
            basic=False,
        ):
            return closest_zone(
                zone_bool=self.drop_zones,
                actual_position=actual_position,
                our=our,
                exclude_not_basic=exclude_not_basic,
                color=self.color,
                basic=basic,
            )

        def closest_plant_zones(
            self,
            actual_position: OrientedPoint,
            our=True,
            exclude_not_basic=True,
            basic=True,
        ):
            return closest_zone(
                zone_bool=self.plant_zones,
                actual_position=actual_position,
                our=our,
                exclude_not_basic=exclude_not_basic,
                color=self.color,
                basic=basic,
            )

        super().__init__(
            game_borders=create_straight_rectangle(origin, opposite_corner),
            zones={
                "forbidden": MultiPolygon([self.drop_zones[(start_zone % 2) * 3]]),
                "home": self.drop_zones[start_zone - 1],
            },
        )

    def __str__(self) -> str:
        return "MarsArena"

    def display(self) -> str:
        return f"""MarsArena: \n
        \tArea : {self.game_borders}
        \tForbidden area : {self.drop_zones["forbidden"]}
        \tHome : {self.zones["home"]}
        """
