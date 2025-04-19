import functools
import copy

import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
from shapely.geometry import box
from shapely.strtree import STRtree
from pathfinding.core.grid import Grid, GridNode

from geometry import Point, Polygon, OrientedPoint
from old_logger import Logger, LogLevels, time_tracker


class GridManager:
    """
    Manages a grid for pathfinding and collision detection.
    Optimized for efficient zone management and pathfinding.

    Notes:
    - Uses static and dynamic grids to conform to external library requirements.
    - Integrates spatial indexing for performance improvements.
    """

    def __init__(self, logger: Logger, chunk_size: int, width: int, height: int) -> None:
        self.logger = logger
        self.chunk_size = chunk_size
        self.half_chunk_size = chunk_size / 2
        self.absolute_width = width
        self.absolute_height = height
        self.grid_width = width // chunk_size
        self.grid_height = height // chunk_size

        if width % chunk_size != 0 or height % chunk_size != 0:
            self.logger.log(
                f"[GRID] width and height must be multiples of chunk_size. Adjusting chunk size.",
                LogLevels.WARNING,
            )
            chunk_size = min(width, height, key=lambda x: abs(x - chunk_size))

        self.static_grid = self.__generate_base_grid()
        self.dynamic_grid = self.__generate_base_grid()
        self.static_forbidden_zones = []
        self.dynamic_forbidden_zones = []
        self.spatial_index = STRtree([])

    # ====== Private Methods ======

    def __generate_base_grid(self) -> Grid:
        """Generates a base grid with all cells walkable."""
        return Grid(
            matrix=[
                [1 for _ in range(self.grid_width)] for _ in range(self.grid_height)
            ]
        )

    def __update_spatial_index(self):
        """Updates the spatial index for static forbidden zones."""
        self.spatial_index = STRtree(self.static_forbidden_zones)

    def __mark_zone(self, grid: Grid, zones: list[Polygon], walkable: bool) -> Grid:
        """
        Marks cells in the grid as walkable or non-walkable based on zones.
        Args:
            grid (Grid): The grid to update.
            zones (list[Polygon]): The zones to mark.
            walkable (bool): Whether to mark the cells as walkable or not.

        Returns:
            Grid: Updated grid.
        """
        for polygon in zones:
            minx, miny, maxx, maxy = polygon.bounds

            min_col = max(0, int((self.grid_width * self.chunk_size - maxx) // self.chunk_size))
            max_col = min(self.grid_width, int((self.grid_width * self.chunk_size - minx) // self.chunk_size) + 1)
            min_row = max(0, int(miny // self.chunk_size))
            max_row = min(self.grid_height, int(maxy // self.chunk_size) + 1)

            for row in range(min_row, max_row):
                for col in range(min_col, max_col):
                    actual_col = self.grid_width - 1 - col
                    cell = box(
                        actual_col * self.chunk_size,
                        row * self.chunk_size,
                        (actual_col + 1) * self.chunk_size,
                        (row + 1) * self.chunk_size,
                    )

                    if polygon.intersects(cell):
                        if walkable and any(zone.intersects(cell) for zone in self.spatial_index.query(cell)):
                            continue
                        grid.nodes[row][actual_col].walkable = walkable

        return grid

    # ====== Public Methods ======

    @time_tracker(lambda self: self.logger)
    def add_forbidden_static_zone(self, forbidden_zones: Polygon | list[Polygon]) -> None:
        """Adds static forbidden zones."""
        if not isinstance(forbidden_zones, list):
            forbidden_zones = [forbidden_zones]

        self.static_forbidden_zones.extend(forbidden_zones)
        self.__update_spatial_index()
        self.static_grid = self.__mark_zone(self.static_grid, forbidden_zones, walkable=False)

    @time_tracker(lambda self: self.logger)
    def remove_forbidden_static_zone(self, forbidden_zones: Polygon | list[Polygon]) -> None:
        """Removes static forbidden zones."""
        if not isinstance(forbidden_zones, list):
            forbidden_zones = [forbidden_zones]

        self.static_forbidden_zones = [
            zone for zone in self.static_forbidden_zones if zone not in forbidden_zones
        ]
        self.__update_spatial_index()
        self.static_grid = self.__generate_base_grid()
        self.static_grid = self.__mark_zone(self.static_grid, self.static_forbidden_zones, walkable=False)

    @time_tracker(lambda self: self.logger)
    def update_dynamic_forbidden_zones(self, dynamic_zones: list[Polygon]) -> None:
        """Updates dynamic forbidden zones."""
        self.dynamic_forbidden_zones = dynamic_zones
        self.dynamic_grid = self.__mark_zone(copy.deepcopy(self.static_grid), dynamic_zones, walkable=False)

    def get_grid_node_center(self, node: GridNode) -> tuple[float, float]:
        """Returns the center coordinates of a grid node."""
        return (
            node.x * self.chunk_size + self.half_chunk_size,
            node.y * self.chunk_size + self.half_chunk_size,
        )

    def absolute_coords_to_grid_coords(self, point: OrientedPoint | Point) -> GridNode:
        """Converts absolute coordinates to grid coordinates."""
        return GridNode(int(point.x / self.chunk_size), int(point.y / self.chunk_size))

    def grid_coords_to_absolute_coords(self, node: GridNode) -> Point:
        """Converts grid coordinates to absolute coordinates."""
        x, y = self.get_grid_node_center(node)
        return Point(x, y)

    def get_static_grid(self) -> Grid:
        """Returns the static grid."""
        return self.static_grid

    def get_dynamic_grid(self) -> Grid:
        """Returns the combined static and dynamic grid."""
        return self.dynamic_grid

    def visualize(self, only_static_grid: bool = False, path=None) -> None:
        """Visualizes the grid using matplotlib."""
        grid_to_visualize = self.static_grid if only_static_grid else self.dynamic_grid

        fig, ax = plt.subplots(figsize=(12, 6))

        for y in range(self.grid_height):
            for x in range(self.grid_width):
                if not grid_to_visualize.node(x, y).walkable:
                    ax.add_patch(plt.Rectangle((x, y), 1, 1, color="black"))

        if path:
            for i in range(len(path) - 1):
                ax.plot(
                    [path[i].x, path[i + 1].x],
                    [path[i].y, path[i + 1].y],
                    color="green",
                    linewidth=2,
                )

        ax.set_xticks(range(self.grid_width))
        ax.set_yticks(range(self.grid_height))

        ax.set_xlim(0, self.grid_width)
        ax.set_ylim(0, self.grid_height)

        ax.grid(True)
        plt.show()
