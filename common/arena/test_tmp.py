from shapely import (
    Polygon,
    MultiPolygon,
    LineString,
    geometry,
    BufferCapStyle,
    BufferJoinStyle,
    Geometry,
)

from datetime import datetime
from shapely import geometry, Point, Polygon

import matplotlib.pyplot as plt
import geopandas as gpd


def show(e):
    p = gpd.GeoSeries(e)
    p.plot()
    plt.show()


class Utils:
    @staticmethod
    def get_date() -> datetime:
        return datetime.now()

    @staticmethod
    def get_str_date(format: str = "%H:%M:%S") -> str:
        return datetime.now().strftime(format)

    @staticmethod
    def get_ts() -> float:
        return datetime.timestamp(datetime.now())

    @staticmethod
    def create_straight_rectangle(p1: Point, p2: Point) -> Polygon:
        return geometry.box(min(p1.x, p2.x), min(p1.y, p2.y), max(p1.x, p2.x), max(p1.y, p2.y))


class Arena:
    """Represent an arena"""

    def __init__(
            self,
            game_borders: Polygon = geometry.box(0, 0, 200, 300),
            zones: dict[str, MultiPolygon] or None = None,
    ):

        self.game_borders = game_borders
        if zones is not None:
            self.zones = zones
        else:
            self.zones = {}

    def contains(self, element: Geometry) -> bool:
        """Check if a point is in the arena bounds

        Args:
            element (Geometry): The point to check. Points, Polygons etc. are all Geometries.

        Returns:
            bool: True if the element is entirely in the arena, False otherwise
        """
        return self.game_borders.contains(element)

    def zone_intersects(self, zone_name: str, element: Geometry) -> bool:

        if zone_name not in self.zones:
            raise ValueError("Tried to check intersection with unknown zone in arena")

        return self.zones[zone_name].intersects(element)

    def enable_go_to(self, path: LineString, buffer_distance: float = 0,
                     forbidden_zone_name: str = "forbidden") -> bool:
        """this function checks if a given line (or series of connected lines) move can be made into the arena. It
        avoids collisions with the boarders and the forbidden area. takes into account the width and the length of
        the robot

        Args:
            path (LineString): Path to check
            buffer_distance (float, optional): Max distance around the path to be checked (in all directions). Defaults to 0.
            forbidden_zone_name (str): Name of the zone to check against (in addition to game borders). Defaults to "forbidden".

        Raises:
            Exception: _description_

        Returns:
            bool: Whether this path is theoretically allowed
        """

        # define the area touched by the buffer, for example the sides of a robot moving

        area_to_check = path.buffer(
            buffer_distance,
            cap_style=BufferCapStyle.round,
            join_style=BufferJoinStyle.round,
        ) if buffer_distance > 0 else path

        # verify that the area touched is in the arena and do not collide with boarders

        # if input(f"Show intersection with game zone?") in ("yes", "y"):
        #     show(self.game_borders)
        #     show(area_to_check)
        #     show(self.game_borders.intersection(area_to_check))

        if not self.game_borders.contains(area_to_check):
            return False

        # verify that the area touched isn't in the forbidden area

        return not self.zone_intersects(forbidden_zone_name, area_to_check)


from shapely import Point, Polygon, geometry


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
            Utils.create_straight_rectangle(Point(0, 0), Point(45, 45)),  # 1 - Blue (Possible forbidden area)
            Utils.create_straight_rectangle(Point(77.5, 0), Point(122.5, 45)),  # 2 - Yellow
            Utils.create_straight_rectangle(Point(155, 0), Point(200, 45)),  # 3 - Blue
            Utils.create_straight_rectangle(Point(0, 255), Point(45, 300)),  # 4 - Yellow (Possible forbidden area)
            Utils.create_straight_rectangle(Point(77.5, 255), Point(122, 300)),  # 5 - Blue
            Utils.create_straight_rectangle(Point(155, 255), Point(200, 300)),  # 6 - Yellow
        ]

        super().__init__(
            game_borders=Utils.create_straight_rectangle(origin, opposite_corner),
            zones={
                "forbidden": all_zones[(start_zone % 2) * 3],
                "home": all_zones[start_zone - 1],
            }
        )

    def __str__(self) -> str:
        return "MarsArena"

    def display(self) -> str:
        return f"""MarsArena: \n
        \tArea : {self.game_borders}
        \tForbidden area : {self.zones["forbidden"]}
        \tHome : {self.zones["home"]}
        """


class TestArena:
    def test_enable_go_to(self):
        arena = Arena(zones={"forbidden": Utils.create_straight_rectangle(Point(2, 2), Point(5, 5))})
        a = Point(1, 1)
        b = Point(1, 6)
        c = Point(3, 1)
        d = Point(6, 1)
        e = Point(2, 6)
        f = Point(3, 6)
        # check without width
        assert arena.enable_go_to(LineString([a, b]), buffer_distance=0.01)
        print("Validated")
        assert not arena.enable_go_to(LineString([a, b]), buffer_distance=12.01)
        print("Validated")
        assert arena.enable_go_to(LineString([a, e]), buffer_distance=0.01)
        print("Validated")
        assert arena.enable_go_to(LineString([a, d]), buffer_distance=0.01)
        print("Validated")
        assert not arena.enable_go_to(LineString([c, f]), buffer_distance=0.01)
        print("Validated")
        assert not arena.enable_go_to(LineString([c, b]), buffer_distance=0.01)
        print("Validated")


class TestMarsArena:
    def test_enable_go_to(self):
        arena = MarsArena(1)
        assert arena.enable_go_to(LineString([[10, 10], [100, 100]]))
        print("Validated")
        assert arena.enable_go_to(LineString([[10, 10], [100, 100]]))
        print("Validated")
        assert not arena.enable_go_to(LineString([[10, 10], [100, 400]]))
        print("Validated")
        assert not arena.enable_go_to(LineString([[10, 10], [10, 275]]))
        print("Validated")


test = TestArena()
test.test_enable_go_to()

test2 = TestMarsArena()
test2.test_enable_go_to()
