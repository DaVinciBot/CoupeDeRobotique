from arena.arena import Arena
from geometry import (
    Point,
    Polygon,
    create_straight_rectangle,
    MultiPolygon,
    OrientedPoint,
)
from shapely import distance
from sys import maxsize


class plants_zone:
    def __init__(self, zone, nb_plant: int = 0) -> None:
        self.zone = zone
        self.nb_plant = nb_plant

    def __str__(self) -> str:
        return f"zone : {self.zone.__str__()}, nb_plant {self.nb_plant}"

    def __repr__(self) -> str:
        return self.__str__()


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

        self.drop_zones: list[plants_zone] = [
            plants_zone(
                create_straight_rectangle(Point(45, 0), Point(0, 45))
            ),  # 1 - Blue (Possible forbidden area)
            create_straight_rectangle(Point(77.5, 0), Point(122.5, 45)),  # 2 - Yellow
            create_straight_rectangle(Point(155, 0), Point(200, 45)),  # 3 - Blue
            create_straight_rectangle(
                Point(0, 255), Point(45, 300)
            ),  # 4 - Yellow (Possible forbidden area)
            plants_zone(
                create_straight_rectangle(Point(122.5, 255), Point(77.5, 300))
            ),  # 5 - Blue
            plants_zone(
                create_straight_rectangle(Point(200, 255), Point(155, 300))
            ),  # 6 - Yellow
        ]

        self.pickup_zones: list[plants_zone] = [
            plants_zone(Point(70, 100).buffer(25), 6),
            plants_zone(Point(130, 100).buffer(25), 6),
            plants_zone(Point(150, 150).buffer(25), 6),
            plants_zone(Point(130, 200).buffer(25), 6),
            plants_zone(Point(70, 200).buffer(25), 6),
            plants_zone(Point(50, 150).buffer(25), 6),
        ]

        self.gardeners: list[plants_zone] = [
            (
                plants_zone(create_straight_rectangle(Point(77.5, -15), Point(45, -3)))
            ),  # 0 - Blue
            (
                plants_zone(
                    create_straight_rectangle(Point(155, -15), Point(122.5, -3)),
                )
            ),  # 1 - Yellow
            (
                plants_zone(create_straight_rectangle(Point(77.5, 303), Point(45, 315)))
            ),  # 2 - Blue
            (
                plants_zone(
                    create_straight_rectangle(Point(155, 303), Point(122.5, 315))
                )
            ),  # 3 - Yellow
        ]

        super().__init__(
            game_borders=create_straight_rectangle(origin, opposite_corner),
            zones={
                "forbidden": MultiPolygon([self.drop_zones[(start_zone % 2) * 3].zone]),
                "home": self.drop_zones[start_zone - 1].zone,
            },
        )

    def sort_zone(
        self,
        zones: list[plants_zone],
        actual_position: OrientedPoint,
        our=True,
        mini=-1,
        maxi=maxsize,
        color="blue",
        reverse=False,
    ):
        if our:
            if color == "blue":
                s = 0
            else:
                s = 1
            zones: list[plants_zone] = [
                zones[i]
                for i in range(s, len(zones), 2)
                if zones[i].nb_plant > mini and zones[i].nb_plant < maxi
            ]
        zones = sorted(
            zones, key=lambda x: distance(x.zone, actual_position)
        )  # sort according to the required bound and by distance
        if reverse:
            zones = sorted(zones, key=lambda x: (x.nb_plant), reverse=True)
        return zones

    def sort_gardener(
        self, actual_position: OrientedPoint, our=True, maxi=6, reverse=True
    ):
        return self.sort_zone(
            actual_position=actual_position,
            our=our,
            zones=self.gardeners,
            maxi=maxi,
            color=self.color,
            reverse=reverse,
        )

    def sort_drop_zone(
        self, actual_position: OrientedPoint, our=True, maxi=6, reverse=True
    ):
        return self.sort_zone(
            actual_position=actual_position,
            our=our,
            zones=self.drop_zones,
            maxi=maxi,
            color=self.color,
            reverse=reverse,
        )

    def sort_pickup_zone(
        self,
        actual_position: OrientedPoint,
        our=False,  # there isn't a notion of propriety for pickup zones
        mini=2,
        reverse=False,
    ):
        return self.sort_zone(
            actual_position=actual_position,
            our=our,
            zones=self.pickup_zones,
            mini=mini,
            color=self.color,
            reverse=reverse,
        )

    def __str__(self) -> str:
        return "MarsArena"

    def display(self) -> str:
        return f"""MarsArena: \n
        \tArea : {self.game_borders}
        \tForbidden area : {self.zones["forbidden"]}
        \tHome : {self.zones["home"]}
        """
