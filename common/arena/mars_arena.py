from arena.arena import Arena
from geometry import (
    Point,
    Polygon,
    create_straight_rectangle,
    MultiPolygon,
    OrientedPoint,
)
from logger import Logger, LogLevels

from shapely import distance
from sys import maxsize


class Plants_zone:
    def __init__(self, zone, nb_plant: int = 0) -> None:
        self.zone = zone
        self.nb_plant = nb_plant

    def __str__(self) -> str:
        return f"zone : {self.zone.__str__()}, nb_plant {self.nb_plant}"

    def __repr__(self) -> str:
        return self.__str__()

    def take_plant(self, nb):
        self.nb_plant -= nb

    def drop_plant(self, nb):
        self.nb_plant += nb


class MarsArena(Arena):
    """Represent the arena of the CDR 2023-2024"""

    def __init__(self, start_zone_id: int, logger: Logger):
        """
        Generate the arena of the CDR 2023-2024

        :param start_zone: The start zone of the robot, must be between 1 and 6
        :type start_zone: int
        :raises ValueError: If start_zone is not between 1 and 6
        """
        if not (0 <= start_zone_id <= 5):
            raise ValueError("start_zone must be between 0 and 5")

        origin = Point(0, 0)
        opposite_corner = Point(200, 300)

        self.color = "yellow" if start_zone_id % 2 == 0 else "blue"
        self.start_zone_id = start_zone_id

        self.drop_zones: list[Plants_zone] = [
            Plants_zone(
                create_straight_rectangle(Point(45, 0), Point(0, 45))
            ),  # 0 - Yellow (Possible forbidden area)
            Plants_zone(
                create_straight_rectangle(Point(77.5, 0), Point(122.5, 45))
            ),  # 1 - Blue
            Plants_zone(
                create_straight_rectangle(Point(155, 0), Point(200, 45))
            ),  # 2 - Yellow
            Plants_zone(
                create_straight_rectangle(Point(0, 255), Point(45, 300))
            ),  # 3 - Blue (Possible forbidden area)
            Plants_zone(
                create_straight_rectangle(Point(122.5, 255), Point(77.5, 300))
            ),  # 4 - Yellow
            Plants_zone(
                create_straight_rectangle(Point(200, 255), Point(155, 300))
            ),  # 5 - Blue
        ]

        self.pickup_zones: list[Plants_zone] = [
            Plants_zone(Point(70, 100).buffer(25), 6),
            Plants_zone(Point(130, 100).buffer(25), 6),
            Plants_zone(Point(150, 150).buffer(25), 6),
            Plants_zone(Point(130, 200).buffer(25), 6),
            Plants_zone(Point(70, 200).buffer(25), 6),
            Plants_zone(Point(50, 150).buffer(25), 6),
        ]

        self.gardeners: list[Plants_zone] = [
            (
                Plants_zone(
                    create_straight_rectangle(Point(155, -15), Point(122.5, -3)),
                )
            ),  # 0 - Yellow
            (
                Plants_zone(create_straight_rectangle(Point(77.5, -15), Point(45, -3)))
            ),  # 1 - Blue
            (
                Plants_zone(
                    create_straight_rectangle(Point(155, 303), Point(122.5, 315))
                )
            ),  # 2 - Yellow
            (
                Plants_zone(create_straight_rectangle(Point(77.5, 303), Point(45, 315)))
            ),  # 3 - Blue
        ]

        super().__init__(
            game_borders=create_straight_rectangle(origin, opposite_corner),
            logger=logger,
            zones={
                "forbidden": MultiPolygon(
                    [
                        self.drop_zones[i].zone
                        for i in range(6)
                        if i % 2 != start_zone_id % 2
                    ]
                ),
                "home": self.drop_zones[start_zone_id].zone,
            },
        )

    def sort_plant_zones(
        self,
        zones_to_sort: list[Plants_zone],
        actual_position: OrientedPoint,
        mini=-1,
        maxi=maxsize,
        reverse=False,
    ):
        zones: list[Plants_zone] = []

        zones = [
            zone
            for zone in zones_to_sort
            if zone.nb_plant > mini and zone.nb_plant < maxi
        ]

        zones = sorted(
            zones,
            key=lambda x: distance(x.zone, Point(actual_position.x, actual_position.y)),
            reverse=reverse,
        )  # sort according to the required bound and by distance

        return zones

    def sort_gardener(
        self, actual_position: OrientedPoint, friendly_only=True, maxi=6, reverse=False
    ):
        zones_to_sort = (
            [
                self.gardeners[i]
                for i in range(len(self.gardeners))
                if i % 2 == self.start_zone_id % 2
            ]
            if friendly_only
            else self.gardeners
        )
        return self.sort_plant_zones(
            actual_position=actual_position,
            zones_to_sort=zones_to_sort,
            maxi=maxi,
            reverse=reverse,
        )

    def sort_drop_zone(
        self, actual_position: OrientedPoint, friendly_only=True, maxi=6, reverse=False
    ):
        zones_to_sort = (
            [
                self.drop_zones[i]
                for i in range(len(self.drop_zones))
                if i % 2 == self.start_zone_id % 2
            ]
            if friendly_only
            else self.drop_zones
        )
        return self.sort_plant_zones(
            actual_position=actual_position,
            zones_to_sort=zones_to_sort,
            maxi=maxi,
            reverse=reverse,
        )

    def sort_pickup_zone(
        self,
        actual_position: OrientedPoint,
        mini=2,
        reverse=False,
    ):
        return self.sort_plant_zones(
            actual_position=actual_position,
            zones_to_sort=self.pickup_zones,
            mini=mini,
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
