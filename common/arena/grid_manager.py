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
from shapely.geometry import box
from pathfinding.core.grid import Grid, GridNode

from logger import Logger, LogLevels
import functools

import matplotlib.pyplot as plt


class GridManager:
    """
    static grid -> attention aux zones de stuff qui change de status après avoir été utilisées
    dynamic zones (enemy)
    use memoization to avoid recalculating the same grid
    # 1 -> walkable, 0 -> obstacle
    """

    def __init__(
        self, logger: Logger, chunk_size: int, width: int, height: int
    ) -> None:
        self.logger: Logger = logger

        # Check if chunk_size is a multiple of width and height
        if width % chunk_size != 0 or height % chunk_size != 0:
            self.logger.log(
                f"[GRID] width and height must be a multiple of chunk_size. "
                f"The chunk size will be round to the nearest multiple",
                LogLevels.ERROR,
            )
            # round chunk_size to the nearest multiple of with and height
            chunk_size = min(width, height, key=lambda x: abs(x - chunk_size))

        self.chunk_size: int = chunk_size
        self.half_chunk_size: float = chunk_size / 2

        self.absolute_width: int = width
        self.absolute_height: int = height

        self.grid_width: int = (
            width // chunk_size
        )  # Ensure that width and height are multiples of chunk_size
        self.grid_height: int = height // chunk_size

        # Forbidden zones
        self.static_forbidden_zones: list[Polygon] = []
        self.dynamic_forbidden_zones: list[Polygon] = []

        # Grid
        self.static_grid: Grid = self.__generate_base_grid()
        self.static_and_dynamic_grid: Grid = self.__generate_base_grid()

    def __update_grid(
        self, *, update_static_zones=False, update_dynamic_zones=False
    ) -> None:
        if update_static_zones:
            for zone in self.static_forbidden_zones:
                self.static_grid = self.__mark_zone_as_forbidden(
                    grid=self.static_grid, polygon_to_mark=zone
                )
                # Also update the static_and_dynamic_grid
                self.static_and_dynamic_grid = self.__mark_zone_as_forbidden(
                    grid=self.static_grid, polygon_to_mark=zone
                )

        if update_dynamic_zones:
            # Don't keep the last dynamic zones in memory
            for zone in self.dynamic_forbidden_zones:
                self.static_and_dynamic_grid = self.__mark_zone_as_forbidden(
                    grid=self.static_grid, polygon_to_mark=zone
                )

    def __generate_base_grid(self) -> Grid:
        return Grid(
            matrix=[
                [1 for _ in range(self.grid_width)] for _ in range(self.grid_height)
            ]
        )

    def __get_grid_node_center(self, node: GridNode) -> tuple[float, float]:
        return (
            node.x * self.chunk_size + self.half_chunk_size,
            node.y * self.chunk_size + self.half_chunk_size,
        )

    @functools.lru_cache  # Memoization dont recalculate the same grid
    def __mark_zone_as_forbidden(self, grid: Grid, polygon_to_mark: Polygon) -> Grid:
        # Determine the grid cells that intersect the polygon
        minx, miny, maxx, maxy = polygon_to_mark.bounds
        min_row = int(miny // self.chunk_size)
        max_row = int(maxy // self.chunk_size)
        min_col = int(minx // self.chunk_size)
        max_col = int(maxx // self.chunk_size)

        # Iterate over the cells that intersect the polygon
        for row in range(max(min_row, 0), min(max_row + 1, self.grid_height)):
            for col in range(max(min_col, 0), min(max_col + 1, self.grid_width)):
                # Create a cell polygon
                cell = box(
                    col * self.chunk_size,
                    row * self.chunk_size,
                    (col + 1) * self.chunk_size,
                    (row + 1) * self.chunk_size,
                )
                # If the cell intersects the polygon, mark it as forbidden
                if polygon_to_mark.intersects(cell):
                    grid.nodes[row][col].walkable = False
        return grid

    def __absolute_coords_to_grid_coords(
        self, point: OrientedPoint | Point
    ) -> GridNode:
        return GridNode(point.x / self.chunk_size, point.y / self.chunk_size)

    def __grid_coords_to_absolute_coords(self, node: GridNode) -> Point:
        x, y = self.__get_grid_node_center(node)
        return Point(x * self.chunk_size, y * self.chunk_size)

    def add_forbidden_static_zone(
        self, forbidden_zones: Polygon | list[Polygon]
    ) -> None:
        """
        Given in real absolute coordinates
        """
        if not isinstance(forbidden_zones, list):
            forbidden_zones = [forbidden_zones]

        self.static_forbidden_zones.extend(forbidden_zones)
        self.__update_grid(update_static_zones=True, update_dynamic_zones=False)

    def remove_forbidden_static_zone(
        self, forbidden_zones_to_remove: Polygon | list[Polygon]
    ) -> None:
        """
        Given in real absolute coordinates
        """
        if not isinstance(forbidden_zones_to_remove, list):
            forbidden_zones_to_remove = [forbidden_zones_to_remove]

        # Exclude the forbidden zones to remove
        self.static_forbidden_zones = [
            zone
            for zone in self.static_forbidden_zones
            if zone not in forbidden_zones_to_remove
        ]
        self.__update_grid(update_static_zones=True, update_dynamic_zones=False)

    def update_dynamic_forbidden_zones(self, forbidden_zones: list[Polygon]) -> None:
        """
        Given in real absolute coordinates
        """
        if not isinstance(forbidden_zones, list):
            forbidden_zones = [forbidden_zones]

        self.dynamic_forbidden_zones.extend(forbidden_zones)
        self.__update_grid(update_static_zones=False, update_dynamic_zones=True)

    def get_static_grid(self) -> Grid:
        return self.static_grid

    def static_and_dynamic_grid(self) -> Grid:
        return self.static_and_dynamic_grid

    def visualize(self, only_static_grid: bool = False) -> None:
        """
        Visualise the grid
        """
        grid_to_visualize = (
            self.static_grid if only_static_grid else self.static_and_dynamic_grid
        )

        # Assuming grid dimensions can be inferred from its node structure
        rows, cols = (
            grid_to_visualize.height,
            grid_to_visualize.width,
        )  # Adjust based on your Grid implementation

        # Initialize the plot
        fig, ax = plt.subplots(figsize=(10, 10))

        # Draw each cell of the grid
        for y in range(self.grid_height):
            for x in range(self.grid_width):
                if not grid_to_visualize.node(x, y).walkable:
                    # Draw obstacles in black
                    ax.add_patch(plt.Rectangle((x, rows - y - 1), 1, 1, color="black"))

        # Set grid lines
        ax.set_xticks(range(cols))
        ax.set_yticks(range(rows))
        ax.grid(True)

        # Set axis limits and labels
        ax.set_xlim(0, cols)
        ax.set_ylim(0, rows)
        ax.set_aspect("equal")
        ax.set_title("Arena Grid Visualization")
        ax.legend(loc="upper right")

        # Show the plot
        plt.show()
