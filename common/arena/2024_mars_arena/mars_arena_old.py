"""Legacy Mars 2024 arena and zone utilities."""

from sys import maxsize

from old_logger import Logger
from pathfinding.core.grid import Grid
from shapely import distance

from arena.base_arena.arena import Arena
from geometry import OrientedPoint, Point, Polygon, create_straight_rectangle

MIN_START_ZONE_ID = 0
MAX_START_ZONE_ID = 5
ARENA_WIDTH_CM = 300
ARENA_HEIGHT_CM = 200


class PlantsZone:
    """Track plant counts and visitation state for a zone."""

    def __init__(self, zone: Polygon, nb_plant: int = 0) -> None:
        """Initialize a plant zone.

        Args:
            zone (Polygon): Polygon representing the zone bounds.
            nb_plant (int, optional): Number of plants in the zone. Defaults to 0.

        """
        self.zone: Polygon = zone
        self.nb_plant: int = nb_plant
        self.visited = False

    def __str__(self) -> str:
        """Return a readable representation of the zone.

        Returns:
            str: Description of the zone and plant count.

        """
        return f"zone : {self.zone}, nb_plant {self.nb_plant}"

    def __repr__(self) -> str:
        """Return a string representation for debugging.

        Returns:
            str: Debug-friendly representation of the zone.

        """
        return self.__str__()

    def take_plants(self, nb: int) -> None:
        """Remove plants from the zone.

        Args:
            nb (int): Number of plants to remove.

        """
        self.nb_plant -= nb

    def drop_plants(self, nb: int) -> None:
        """Add plants to the zone.

        Args:
            nb (int): Number of plants to add.

        """
        self.nb_plant += nb

    def visit(self) -> None:
        """Mark the zone as visited."""
        self.visited = True


class MarsArena(Arena):
    """Arena layout and zone helpers for the 2024 Mars challenge."""

    def __init__(
        self,
        start_zone_id: int,
        logger: Logger,
        *,
        border_buffer: float,
        robot_buffer: float,
    ) -> None:
        """Generate the arena of the CDR 2023-2024.

        Args:
            start_zone_id (int): Starting zone ID for the robot.
            logger (Logger): Logger instance for debugging information.
            border_buffer (float): Safety buffer around the arena borders.
            robot_buffer (float): Safety buffer around moving robots.

        Raises:
            ValueError: If ``start_zone_id`` is not between ``MIN_START_ZONE_ID`` and
                ``MAX_START_ZONE_ID``.

        """
        if not (MIN_START_ZONE_ID <= start_zone_id <= MAX_START_ZONE_ID):
            msg = (
                f"start_zone must be between {MIN_START_ZONE_ID} "
                f"and {MAX_START_ZONE_ID}"
            )
            raise ValueError(msg)

        origin = Point(0, 0)
        opposite_corner = Point(200, 300)

        self.start_zone_id = start_zone_id

        solar_panels_distances: list[float] = [27.5, 50, 72.5, 127.5, 150]
        self.solar_panels_y: list[float] = (
            solar_panels_distances
            if self.start_zone_id % 2 == 0
            else [300 - val for val in solar_panels_distances]
        )

        self.drop_zones: list[PlantsZone] = [
            PlantsZone(
                create_straight_rectangle(Point(45, 0), Point(0, 45)),
            ),  # 0 - Blue (Possible forbidden area)
            PlantsZone(
                create_straight_rectangle(Point(77.5, 0), Point(122.5, 45)),
            ),  # 1 - Yellow
            PlantsZone(
                create_straight_rectangle(Point(155, 0), Point(200, 45)),
            ),  # 2 - Blue
            PlantsZone(
                create_straight_rectangle(Point(0, 255), Point(45, 300)),
            ),  # 3 - Yellow (Possible forbidden area)
            PlantsZone(
                create_straight_rectangle(Point(122.5, 255), Point(77.5, 300)),
            ),  # 4 - Blue
            PlantsZone(
                create_straight_rectangle(Point(200, 255), Point(155, 300)),
            ),  # 5 - Yellow
        ]

        self.pickup_zones: list[PlantsZone] = [
            PlantsZone(Point(70, 100).buffer(12.5), 6),
            PlantsZone(Point(130, 100).buffer(12.5), 6),
            PlantsZone(Point(150, 150).buffer(12.5), 6),
            PlantsZone(Point(130, 200).buffer(12.5), 6),
            PlantsZone(Point(70, 200).buffer(12.5), 6),
            PlantsZone(Point(50, 150).buffer(12.5), 6),
        ]

        self.gardeners: list[PlantsZone] = [
            (
                PlantsZone(
                    create_straight_rectangle(Point(45, -15), Point(77.5, -3)),
                )
            ),  # 0 - Blue
            (
                PlantsZone(
                    create_straight_rectangle(Point(122.5, -15), Point(155, -3)),
                )
            ),  # 1 - Yellow
            (PlantsZone(create_straight_rectangle(Point(203, 60), Point(215, 92.5)))),
            (PlantsZone(create_straight_rectangle(Point(45, 315), Point(77.5, 303)))),
            (
                PlantsZone(
                    create_straight_rectangle(Point(122.5, 315), Point(155, 303)),
                )
            ),
            (
                PlantsZone(
                    create_straight_rectangle(Point(203, 240), Point(215, 207.5)),
                )
            ),
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
    def team(self) -> str:
        """Return ``'y'`` for yellow or ``'b'`` for blue based on start zone.

        Returns:
            str: Team color identifier.

        """
        return "y" if self.start_zone_id % 2 == 0 else "b"

    @staticmethod
    def sort_plant_zones(
        *,
        zones_to_sort: list[PlantsZone],
        actual_position: OrientedPoint,
        mini_plants: int = -1,
        maxi_plants: int = maxsize,
        reverse: bool = False,
    ) -> list[PlantsZone]:
        """Sort plant zones by number of plants and distance.

        Args:
            zones_to_sort (list[PlantsZone]): Zones to sort.
            actual_position (OrientedPoint): Reference position for distance.
            mini_plants (int, optional): Minimum number of plants per zone.
                Defaults to -1.
            maxi_plants (int, optional): Maximum number of plants per zone. Defaults to
                ``sys.maxsize``.
            reverse (bool, optional): If ``True``, sort from farthest to nearest.
                Defaults to ``False``.

        Returns:
            list[PlantsZone]: Sorted list of plant zones.

        """
        zones = [
            zone for zone in zones_to_sort if mini_plants < zone.nb_plant < maxi_plants
        ]
        return sorted(
            zones,
            key=lambda x: distance(x.zone, Point(actual_position.x, actual_position.y)),
            reverse=reverse,
        )

    def sort_gardener(
        self,
        actual_position: OrientedPoint,
        *,
        friendly_only: bool = True,
        maxi: int = 6,
        reverse: bool = False,
    ) -> list[PlantsZone]:
        """Sort gardener zones according to filters.

        Args:
            actual_position (OrientedPoint): Reference position for distance.
            friendly_only (bool, optional): If ``True``, consider only friendly zones.
                Defaults to ``True``.
            maxi (int, optional): Maximum number of plants in a zone. Defaults to 6.
            reverse (bool, optional): If ``True``, sort from farthest to nearest.
                Defaults to ``False``.

        Returns:
            list[PlantsZone]: Sorted gardener zones.

        """
        zones_to_sort = (
            [
                self.gardeners[i]
                for i in range(len(self.gardeners))
                if i % 2 == self.start_zone_id % 2
            ]
            if friendly_only
            else self.gardeners
        )
        return MarsArena.sort_plant_zones(
            zones_to_sort=zones_to_sort,
            actual_position=actual_position,
            maxi_plants=maxi,
            reverse=reverse,
        )

    def sort_drop_zone(
        self,
        actual_position: OrientedPoint,
        *,
        friendly_only: bool = True,
        maxi_plants: int = 6,
        reverse: bool = False,
    ) -> list[PlantsZone]:
        """Sort drop zones according to filters.

        Args:
            actual_position (OrientedPoint): Reference position for distance.
            friendly_only (bool, optional): If ``True``, consider only friendly zones.
                Defaults to ``True``.
            maxi_plants (int, optional):
                Maximum number of plants in a zone. Defaults to 6.
            reverse (bool, optional): If ``True``, sort from farthest to nearest.
                Defaults to ``False``.

        Returns:
            list[PlantsZone]: Sorted drop zones.

        """
        zones_to_sort = (
            [
                self.drop_zones[i]
                for i in range(len(self.drop_zones))
                if i % 2 == self.start_zone_id % 2
            ]
            if friendly_only
            else self.drop_zones
        )
        return MarsArena.sort_plant_zones(
            zones_to_sort=zones_to_sort,
            actual_position=actual_position,
            maxi_plants=maxi_plants,
            reverse=reverse,
        )

    def sort_pickup_zone(
        self,
        actual_position: OrientedPoint,
        *,
        mini_plants: int = 2,
        reverse: bool = False,
    ) -> list[PlantsZone]:
        """Sort pickup zones according to filters.

        Args:
            actual_position (OrientedPoint): Reference position for distance.
            mini_plants (int, optional): Minimum number of plants in a zone.
                Defaults to 2.
            reverse (bool, optional): If ``True``, sort from farthest to nearest.
                Defaults to ``False``.

        Returns:
            list[PlantsZone]: Sorted pickup zones.

        """
        return MarsArena.sort_plant_zones(
            zones_to_sort=self.pickup_zones,
            actual_position=actual_position,
            mini_plants=mini_plants,
            reverse=reverse,
        )

    def __str__(self) -> str:
        """Return the class name.

        Returns:
            str: Name of the class.

        """
        return "MarsArena"

    def display(self) -> str:
        """Return a readable description of arena zones.

        Returns:
            str: Summary of the arena layout.

        """
        return (
            f"MarsArena: \n"
            f"\tArea : {self.game_borders}\n"
            f"\tForbidden area : {self.zones['forbidden']}\n"
            f"\tHome : {self.zones['home']}\n"
        )

    def to_grid(self, chunk_size_cm: int) -> Grid:
        """Convert the arena into a grid representation.

        Args:
            chunk_size_cm (int): Size of each grid cell in centimeters.

        Returns:
            Grid: Grid where ``0`` marks forbidden cells.

        """
        width = ARENA_WIDTH_CM // chunk_size_cm
        height = ARENA_HEIGHT_CM // chunk_size_cm

        # All the grid is filled with 1 -> authorized area
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
