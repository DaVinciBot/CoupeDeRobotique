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

from pathfinding.core.grid import Grid, GridNode


class Plants_zone:
    def __init__(self, zone, nb_plant: int = 0) -> None:
        self.zone: Polygon = zone
        self.nb_plant: int = nb_plant
        self.visited = False

    def __str__(self) -> str:
        return f"zone : {self.zone.__str__()}, nb_plant {self.nb_plant}"

    def __repr__(self) -> str:
        return self.__str__()

    def take_plants(self, nb):
        self.nb_plant -= nb

    def drop_plants(self, nb):
        self.nb_plant += nb

    def visit(self):
        self.visited = True


class MarsArena(Arena):
    """Represent the arena of the +CDR 2023-2024"""

    def __init__(
        self, start_zone_id: int, logger: Logger, *, border_buffer, robot_buffer
    ):
        """
        Generate the arena of the CDR 2023-2024

        :param start_zone: The start zone of the robot, must be between 1 and 6
        :type start_zone: int
        :raises ValueError: If start_zone is not between 0 and 5
        """
        if not (0 <= start_zone_id <= 5):
            raise ValueError("start_zone must be between 0 and 5")

        origin = Point(0, 0)
        opposite_corner = Point(200, 300)

        self.start_zone_id = start_zone_id

        solar_panels_distances: list[float] = [27.5, 50, 72.5, 127.5, 150]
        self.solar_panels_y: list[float] = (
            solar_panels_distances
            if self.start_zone_id % 2 == 0
            else [300 - val for val in solar_panels_distances]
        )

        self.drop_zones: list[Plants_zone] = [
            Plants_zone(
                create_straight_rectangle(Point(45, 0), Point(0, 45))
            ),  # 0 - Blue (Possible forbidden area)
            Plants_zone(
                create_straight_rectangle(Point(77.5, 0), Point(122.5, 45))
            ),  # 1 - Yellow
            Plants_zone(
                create_straight_rectangle(Point(155, 0), Point(200, 45))
            ),  # 2 - Blue
            Plants_zone(
                create_straight_rectangle(Point(0, 255), Point(45, 300))
            ),  # 3 - Yellow (Possible forbidden area)
            Plants_zone(
                create_straight_rectangle(Point(122.5, 255), Point(77.5, 300))
            ),  # 4 - Blue
            Plants_zone(
                create_straight_rectangle(Point(200, 255), Point(155, 300))
            ),  # 5 - Yellow
        ]

        self.pickup_zones: list[Plants_zone] = [
            Plants_zone(Point(70, 100).buffer(12.5), 6),
            Plants_zone(Point(130, 100).buffer(12.5), 6),
            Plants_zone(Point(150, 150).buffer(12.5), 6),
            Plants_zone(Point(130, 200).buffer(12.5), 6),
            Plants_zone(Point(70, 200).buffer(12.5), 6),
            Plants_zone(Point(50, 150).buffer(12.5), 6),
        ]

        self.gardeners: list[Plants_zone] = [
            (
                Plants_zone(
                    create_straight_rectangle(Point(45, -15), Point(77.5, -3)),
                )
            ),  # 0 - Blue
            (
                Plants_zone(
                    create_straight_rectangle(Point(122.5, -15), Point(155, -3))
                )
            ),  # 1 - Yellow
            (
                Plants_zone(create_straight_rectangle(Point(203, 60), Point(215, 92.5)))
            ),  # 2 - Yellow
            (
                Plants_zone(create_straight_rectangle(Point(45, 315), Point(77.5, 303)))
            ),  # 3 - Yellow
            (
                Plants_zone(
                    create_straight_rectangle(Point(122.5, 315), Point(155, 303))
                )
            ),  # 4 - Blue
            (
                Plants_zone(
                    create_straight_rectangle(Point(203, 240), Point(215, 207.5))
                )
            ),  # 5 - Blue
        ]
        if self.start_zone_id % 2 == 0:
            forbidden = self.drop_zones[3].zone
        else:
            forbidden = self.drop_zones[0].zone
        super().__init__(
            game_borders=create_straight_rectangle(origin, opposite_corner),
            logger=logger,
            zones={
                "forbidden": forbidden,
                "home": self.drop_zones[start_zone_id].zone,
            },
            border_buffer=border_buffer,
            robot_buffer=robot_buffer,
        )

    @property
    def team(self):
        return "y" if self.start_zone_id % 2 == 0 else "b"

    def sort_plant_zones(
        self,
        zones_to_sort: list[Plants_zone],
        actual_position: OrientedPoint,
        mini_plants=-1,
        maxi_plants=maxsize,
        reverse=False,
    ):
        zones: list[Plants_zone] = []

        zones = [
            zone
            for zone in zones_to_sort
            if zone.nb_plant > mini_plants and zone.nb_plant < maxi_plants
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
            maxi_plants=maxi,
            reverse=reverse,
        )

    def sort_drop_zone(
        self,
        actual_position: OrientedPoint,
        friendly_only=True,
        maxi_plants=6,
        reverse=False,
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
            maxi_plants=maxi_plants,
            reverse=reverse,
        )

    def sort_pickup_zone(
        self,
        actual_position: OrientedPoint,
        mini_plants=2,
        reverse=False,
    ):
        return self.sort_plant_zones(
            actual_position=actual_position,
            zones_to_sort=self.pickup_zones,
            mini_plants=mini_plants,
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

    def to_grid(self, chunk_size_cm: int) -> Grid:
        width_cm = 300
        height_cm = 200

        width = width_cm // chunk_size_cm
        height = height_cm // chunk_size_cm

        # ALl the grid is filled with 1 -> authorized area
        grid = [[1 for _ in range(width)] for _ in range(height)]

        # Forbidden area
        forbidden_area = [plant_zone.zone for plant_zone in self.drop_zones] + [
            plant_zone.zone for plant_zone in self.pickup_zones
        ]

        # Iterate over each cell in the grid
        for row in range(height):
            for col in range(width):
                # Compute the center point of the current cell
                cell_center = Point(
                    (col * chunk_size_cm + chunk_size_cm // 2),
                    (row * chunk_size_cm + chunk_size_cm // 2),
                )

                # Check if the cell center is within the forbidden area
                if any(area.contains(cell_center) for area in forbidden_area):
                    grid[row][col] = 0

        return Grid(matrix=grid)
