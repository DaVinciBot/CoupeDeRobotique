# ====== Code Summary ======
# This implementation defines the GridManager class, which manages a grid for pathfinding and collision detection.
# Imports are organized into standard library, third-party, and internal project sections for clarity.
# Private methods handle grid generation, coordinate conversions, and marking forbidden zones, ensuring encapsulation.
# Public methods allow adding/removing static zones, updating dynamic zones, converting coordinates, and retrieving or visualizing grids.
# The visualization method uses matplotlib for clear grid rendering, showing obstacles and walkable areas effectively.

# ====== Imports ======
# Standard library imports
import functools

# Third-party library imports
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
from shapely.geometry import box
from pathfinding.core.grid import Grid, GridNode

# Internal project imports
from geometry import (
    Point,
    MultiPoint,
    Polygon,
    MultiPolygon,
    LineString,
    BufferCapStyle,
    BufferJoinStyle,
    Geometry,
    create_straight_rectangle,
    prepare,
    distance,
    OrientedPoint,
    nearest_points,
)
from logger import Logger, LogLevels, time_tracker


# ====== GridManager Class ======
class GridManager:
    """
    Manages a grid for pathfinding and collision detection.
    Includes static and dynamic forbidden zones and grid visualization.

    Notes:
    - The grid uses a coordinate system where the origin is at the bottom-right corner.
    - X-axis increases towards the left, while Y-axis increases upwards.
    - This reference frame affects calculations and visualization; adjustments ensure alignment.
    """

    def __init__(
        self, logger: Logger, chunk_size: int, width: int, height: int
    ) -> None:
        """
        Initializes the grid manager.

        Args:
            logger (Logger): Logger instance for logging errors and information.
            chunk_size (int): Size of each grid chunk.
            width (int): Total width of the grid in absolute units.
            height (int): Total height of the grid in absolute units.
        """
        self.logger: Logger = logger

        # Validate chunk size
        if width % chunk_size != 0 or height % chunk_size != 0:
            self.logger.log(
                f"[GRID] width and height must be multiples of chunk_size. "
                f"Chunk size will be adjusted to the nearest multiple.",
                LogLevels.ERROR,
            )
            chunk_size = min(width, height, key=lambda x: abs(x - chunk_size))

        self.chunk_size: int = chunk_size
        self.half_chunk_size: float = chunk_size / 2
        self.absolute_width: int = width
        self.absolute_height: int = height
        self.grid_width: int = width // chunk_size
        self.grid_height: int = height // chunk_size

        self.static_forbidden_zones: list[Polygon] = []
        self.dynamic_forbidden_zones: list[Polygon] = []

        self.static_grid: Grid = self.__generate_base_grid()
        self.static_and_dynamic_grid: Grid = self.__generate_base_grid()

    # ====== Private Methods ======

    def __generate_base_grid(self) -> Grid:
        """Generates a base grid with all cells walkable."""
        return Grid(
            matrix=[
                [1 for _ in range(self.grid_width)] for _ in range(self.grid_height)
            ]
        )

    def __mark_zone_as_forbidden(self, grid: Grid, polygon_to_mark: Polygon) -> Grid:
        """
        Marks cells in the grid as forbidden based on intersection with a polygon.

        Args:
            grid (Grid): The grid to modify.
            polygon_to_mark (Polygon): The polygon defining forbidden zones.
        """
        minx, miny, maxx, maxy = polygon_to_mark.bounds

        min_col, max_col = int(
            (self.grid_width * self.chunk_size - maxx) // self.chunk_size
        ), int((self.grid_width * self.chunk_size - minx) // self.chunk_size)
        min_row, max_row = int(miny // self.chunk_size), int(maxy // self.chunk_size)

        for row in range(max(min_row, 0), min(max_row + 1, self.grid_height)):
            for col in range(max(min_col, 0), min(max_col + 1, self.grid_width)):
                actual_col = self.grid_width - 1 - col
                cell = box(
                    (self.grid_width - 1 - col) * self.chunk_size,
                    row * self.chunk_size,
                    (self.grid_width - col) * self.chunk_size,
                    (row + 1) * self.chunk_size,
                )
                if polygon_to_mark.intersects(cell):
                    grid.nodes[row][actual_col].walkable = False

        return grid

    def __update_grid(
        self, *, update_static_zones=False, update_dynamic_zones=False, clear_grid=False
    ) -> None:
        """
        Updates the grids for static and dynamic zones.

        Args:
            update_static_zones (bool): Whether to update static zones.
            update_dynamic_zones (bool): Whether to update dynamic zones.
        """
        if clear_grid:
            self.static_grid = self.__generate_base_grid()
            self.static_and_dynamic_grid = self.__generate_base_grid()

        if update_static_zones:
            for zone in self.static_forbidden_zones:
                self.static_grid = self.__mark_zone_as_forbidden(
                    grid=self.static_grid, polygon_to_mark=zone
                )
                self.static_and_dynamic_grid = self.__mark_zone_as_forbidden(
                    grid=self.static_grid, polygon_to_mark=zone
                )

        if update_dynamic_zones:
            for zone in self.dynamic_forbidden_zones:
                self.static_and_dynamic_grid = self.__mark_zone_as_forbidden(
                    grid=self.static_grid, polygon_to_mark=zone
                )

    # ====== Public Methods ======
    @time_tracker(lambda self: self.logger)
    def add_forbidden_static_zone(
        self, forbidden_zones: Polygon | list[Polygon]
    ) -> None:
        """
        Adds static forbidden zones to the grid.

        Args:
            forbidden_zones (Polygon | list[Polygon]): Zones to mark as static forbidden areas.
        """
        if not isinstance(forbidden_zones, list):
            forbidden_zones = [forbidden_zones]

        self.static_forbidden_zones.extend(forbidden_zones)
        self.__update_grid(update_static_zones=True)

    @time_tracker(lambda self: self.logger)
    def remove_forbidden_static_zone(
        self, forbidden_zones_to_remove: Polygon | list[Polygon]
    ) -> None:
        """
        Removes static forbidden zones from the grid.

        Args:
            forbidden_zones_to_remove (Polygon | list[Polygon]): Zones to remove from static forbidden areas.
        """
        if not isinstance(forbidden_zones_to_remove, list):
            forbidden_zones_to_remove = [forbidden_zones_to_remove]

        original_static_forbidden_zones = self.static_forbidden_zones[:]
        self.static_forbidden_zones = [
            zone
            for zone in self.static_forbidden_zones
            if zone not in forbidden_zones_to_remove
        ]

        removed_zones = set(original_static_forbidden_zones) - set(
            self.static_forbidden_zones
        )
        if not removed_zones:
            self.logger.log(
                "Call remove zone but no zone removed. Check if you use buffer.",
                LogLevels.WARNING,
            )

        self.__update_grid(update_static_zones=True, clear_grid=True)

    @time_tracker(lambda self: self.logger)
    def update_dynamic_forbidden_zones(self, forbidden_zones: list[Polygon]) -> None:
        """
        Updates dynamic forbidden zones in the grid.

        Args:
            forbidden_zones (list[Polygon]): Dynamic zones to add or update.
        """
        if not isinstance(forbidden_zones, list):
            forbidden_zones = [forbidden_zones]

        self.dynamic_forbidden_zones = forbidden_zones
        self.__update_grid(update_dynamic_zones=True)

    def get_grid_node_center(self, node: GridNode) -> tuple[float, float]:
        """Calculates the absolute center coordinates of a grid node."""
        return (
            node.x * self.chunk_size + self.half_chunk_size,
            node.y * self.chunk_size + self.half_chunk_size,
        )

    def absolute_coords_to_grid_coords(self, point: OrientedPoint | Point) -> GridNode:
        """Converts absolute coordinates to grid coordinates."""
        return GridNode(point.x / self.chunk_size, point.y / self.chunk_size)

    def grid_coords_to_absolute_coords(self, node: GridNode) -> Point:
        """Converts grid coordinates to absolute coordinates."""
        x, y = self.get_grid_node_center(node)
        return Point(x, y)

    def get_static_grid(self) -> Grid:
        """Returns the static grid."""
        return self.static_grid

    def get_static_and_dynamic_grid(self) -> Grid:
        """Returns the combined static and dynamic grid."""
        return self.static_and_dynamic_grid

    def visualize(self, only_static_grid: bool = False, path=None) -> None:
        """
        Visualizes the grid using matplotlib.

        Args:
            only_static_grid (bool): Whether to show only the static grid.
            path (list): List of coordinates representing a path (optional).
        """
        grid_to_visualize = (
            self.static_grid if only_static_grid else self.static_and_dynamic_grid
        )

        fig, ax = plt.subplots(figsize=(12, 6))

        for y in range(self.grid_height):
            for x in range(self.grid_width):
                if not grid_to_visualize.node(x, y).walkable:
                    ax.add_patch(plt.Rectangle((x, y), 1, 1, color="black"))

        if path and len(path) > 1:
            for i in range(len(path) - 1):
                current = self.absolute_coords_to_grid_coords(path[i])
                next_node = self.absolute_coords_to_grid_coords(path[i + 1])
                # Draw a line connecting the current node to the next node
                ax.plot(
                    [
                        current.x + self.half_chunk_size,
                        next_node.x + self.half_chunk_size,
                    ],
                    [
                        current.y + self.half_chunk_size,
                        next_node.y + self.half_chunk_size,
                    ],
                    color="blue",
                    linewidth=2,
                )

        ax.set_xticks(range(self.grid_width))
        ax.set_yticks(range(self.grid_height))

        ax.set_xlim(self.grid_width, 0)
        ax.set_ylim(0, self.grid_height)

        ax.xaxis.set_major_locator(MaxNLocator(integer=True, nbins=25))
        ax.yaxis.set_major_locator(MaxNLocator(integer=True, nbins=25))
        plt.xticks(rotation=45)

        ax.set_aspect("equal", adjustable="box")
        ax.set_title("Arena Grid Visualization")

        ax.grid(True)
        plt.tight_layout()
        plt.show()
