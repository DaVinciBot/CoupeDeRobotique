# ====== Code Summary ======
# The BaseArena class models a physical arena with zones, border buffers, and obstacles.
# It initializes a list of zones with added buffers and includes a GridManager for managing grid-based zones.
# Methods include creating border zones, adding buffers to zones, and visualizing the arena with optional buffer zones.

# ====== Imports ======
# Third-party library imports
import matplotlib.pyplot as plt

# Internal project imports
from geometry import (
    BufferCapStyle,
    BufferJoinStyle,
    Polygon,
    box,
    Point,
    OrientedPoint,
)
from logger import Logger, LogLevels, time_tracker
from arena.base_arena.grid_manager import GridManager
from arena.base_arena.arena_zone import (
    # Enums
    ZoneType,
    ZoneAccessibility,

    # Zones
    BaseArenaZone,
    BorderZone,
    YellowReservedZone,
    BlueReservedZone,
)


# ====== BaseArena Class ======
class BaseArena:
    """
    Represents the arena and its zones, including buffer zones and borders.

    Attributes:
        logger (Logger): Logger instance for logging information.
        width (int): Width of the arena in centimeters.
        height (int): Height of the arena in centimeters.
        border_buffer (float): Buffer distance for the arena border.
        obstacle_buffer (float): Buffer distance for obstacles.
        zones (list[BaseArenaZone]): List of all zones in the arena.
        grid_manager (GridManager): Grid manager instance for managing zones.
    """

    def __init__(
            self,
            logger: Logger,
            width: int,
            height: int,
            border_buffer: float,
            obstacle_buffer: float,
            zones: list[BaseArenaZone],
            chunk_size: int = 10,
            grid_manager_logger: Logger = Logger(
                identifier="GridManager",
                decorator_level=LogLevels.INFO,
                print_log_level=LogLevels.DEBUG,
                file_log_level=LogLevels.DEBUG,
            ),
    ) -> None:
        self.logger: Logger = logger

        self.width: int = width
        self.height: int = height

        self.border_buffer: float = border_buffer
        self.obstacle_buffer: float = obstacle_buffer

        # Initialize zones with added buffer
        self.zones: list[BaseArenaZone] = []
        for zone in zones:
            zone.polygon = self.__add_buffer_to_zone(zone.polygon, self.obstacle_buffer)
            self.zones.append(zone)

        # Add border zone
        self.zones.append(self.__create_arena_border_zone())

        # Initialize grid manager
        self.grid_manager: GridManager = GridManager(
            grid_manager_logger, chunk_size, width, height
        )

        # Add forbidden and border zones to the grid manager
        for zone in self.zones:
            if not zone.is_accessible():
                self.grid_manager.add_forbidden_static_zone(zone.polygon)

        self.team_color = None

    # ====== Private Methods ======
    @staticmethod
    def __add_buffer_to_zone(polygon: Polygon, buffer: float) -> Polygon:
        """
        Adds a buffer around a zone to account for obstacle or border spacing.
        The buffer uses a square cap style to match the grid structure.
        """
        return polygon.buffer(buffer, cap_style=BufferCapStyle.flat, join_style=BufferJoinStyle.mitre)

    def __create_arena_border_zone(self) -> BorderZone:
        """
        Create a border zone around the arena with a specified buffer width.
        Prevents the robot from approaching too close to the arena edges.
        """
        arena_polygon = box(0, 0, self.width, self.height)
        inner_polygon = self.__add_buffer_to_zone(arena_polygon, -self.border_buffer)
        border_zone_polygon = arena_polygon.difference(inner_polygon)

        return BorderZone(polygon=border_zone_polygon)

    @staticmethod
    def __plot_polygon(ax, polygon: Polygon, color: str, label: str = None, alpha: float = 1.0,
                       hatch: str = None, hatch_color: str = None) -> None:
        """
        Helper method to plot a polygon or multipolygon on a matplotlib axis.

        - Fills polygons without holes, optionally with hatching.
        - Draws only outlines (dashed) for polygons with holes.
        - Ensures that the same legend label is not added more than once.

        Parameters:
        - ax: matplotlib axis
        - polygon: Polygon to plot (from shapely.geometry)
        - color: Color of the polygon (fill or outline)
        - label: Legend label (optional)
        - alpha: Transparency of the fill or line (default=1.0)
        - hatch: Hatching pattern (optional), e.g., '/' or '\\'. Set None for no hatching.
        - hatch_color: Color of the hatching lines (optional, default same as outline color)
        """
        # Avoid duplicate labels
        existing_labels = ax.get_legend_handles_labels()[1]
        if label is not None and label in existing_labels:
            label = None

        if len(polygon.interiors) == 0:
            # Polygon without holes
            x, y = polygon.exterior.xy
            ax.fill(x, y, alpha=alpha, fc=color, label=label, hatch=hatch, ec=hatch_color or color)
        else:
            # Polygon with holes: outline and interior lines
            x, y = polygon.exterior.xy
            ax.plot(x, y, color=color, linestyle="--", label=label, alpha=alpha)
            for interior in polygon.interiors:
                x, y = interior.xy
                ax.plot(x, y, color=color, linestyle="--", alpha=alpha)

    def __plot_zone(self, ax, zone: BaseArenaZone, show_buffer: bool):
        """Plots zones and their buffers on the arena."""
        if show_buffer:
            # Plot buffer zone in transparent color
            self.__plot_polygon(
                ax,
                zone.polygon,
                color=zone.zone_color,
                alpha=0.5
            )

        # Plot the original zone in full color and hatch if necessary
        if not zone.is_instance(BorderZone):
            hatch_params = {}
            if zone.is_accessible(team_color=self.team_color):
                pass  # No hatch
            elif zone.is_accessible_for_emergency(team_color=self.team_color):
                hatch_params = {"hatch": "\\", "hatch_color": "red"}  # Hatch with red lines for restricted zones
            elif not zone.is_accessible(team_color=self.team_color):
                hatch_params = {"hatch": "/", "hatch_color": "black"}  # Hatch with black lines for forbidden zones

            self.__plot_polygon(
                ax,
                self.__add_buffer_to_zone(zone.polygon, -self.obstacle_buffer),  # Remove buffer for original zone
                color=zone.zone_color,
                label=zone.zone_type.name,
                alpha=0.8,
                **hatch_params
            )

    # ====== Public Methods ======
    def set_team_color(self, team_color: str) -> None:
        """Set the team color for determining zone accessibility."""
        self.team_color = team_color

        # Remove all current team color zones from the grid manager
        # TODO: retirer ça et juste laisser les update de zones mettre à jour leur état, la grille qui possède des pointeurs vers ces zones devrait être capable de mettre à jour son état elle meme
        for zone in self.zones:
            if (zone.is_instance(BlueReservedZone) and team_color.lower() in ["blue", "b"]) or (
                    zone.is_instance(YellowReservedZone) and team_color.lower() in ["yellow", "y"]):
                self.grid_manager.remove_forbidden_static_zone(
                    zone.polygon
                )

        self.update([], [])
        print()

    @time_tracker(lambda self: self.logger)
    def update(self, ally_positions: list[OrientedPoint | Point], enemy_positions: list[OrientedPoint | Point]) -> None:
        """Update the zones based on the positions of allies and enemies."""
        for i in range(len(ally_positions)):
            ally_positions[i] = Point(ally_positions[i].x, ally_positions[i].y)
        for i in range(len(enemy_positions)):
            enemy_positions[i] = Point(enemy_positions[i].x, enemy_positions[i].y)

        # TODO: mise à jour des zones en fonction des positions des alliés et ennemis, ça devrait se répercuter sur grid_manager
        for zone in self.zones:
            zone.update(self.team_color, ally_positions, enemy_positions)

    @time_tracker(lambda self: self.logger)
    def visualize(self, show_buffer: bool = True) -> None:
        """
        Visualize the arena, including its zones, buffers, and accessibility grid.

        Args:
            show_buffer (bool): If True, buffer zones are displayed.
        """
        fig, ax = plt.subplots(figsize=(12, 6))

        # Draw the arena boundary
        arena_polygon = box(0, 0, self.width, self.height)
        self.__plot_polygon(ax, arena_polygon, color="#f0f0f0", label="Arena")

        # Plot zones and their buffers
        for zone in self.zones:
            self.__plot_zone(ax, zone, show_buffer)

        ax.set_xlim(self.width, 0)  # Reverse x-axis
        ax.set_ylim(0, self.height)  # Keep y-axis normal
        ax.spines['top'].set_visible(False)  # Hide top frame line
        ax.spines['right'].set_visible(False)  # Hide right frame line
        ax.spines['left'].set_position(('axes', 1))  # Move y-axis to the right
        ax.yaxis.tick_right()  # Move y-axis labels to the right
        ax.yaxis.set_label_position("right")

        ax.set_aspect("equal", adjustable="box")
        ax.set_title("Arena Visualization")

        # Place legend on the left
        plt.legend(loc='center right', bbox_to_anchor=(-0.1, 0.5))

        plt.tight_layout()
        plt.show()
