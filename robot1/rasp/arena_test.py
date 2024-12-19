from config_loader import CONFIG

from pathfinding.core.grid import Grid, GridNode

from path_finding import PathFinder

from arena import (
    ShowArena,
    BaseArenaZone,
    BaseArena,
    ForbiddenZone,
    ZoneType,
    EnemyZone,
    StuffZone,
    BlueReservedZone,
    YellowReservedZone,
    BorderZone,
    ZoneAccessibility,
)

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
    box,
)
from logger import Logger, LogLevels

finder_logger = Logger(
    identifier="PathFinder",
    decorator_level=LogLevels.INFO,
    print_log_level=LogLevels.DEBUG,
    file_log_level=LogLevels.DEBUG,
)

arena_logger = Logger(
    identifier="ShowArena",
    decorator_level=LogLevels.INFO,
    print_log_level=LogLevels.DEBUG,
    file_log_level=LogLevels.DEBUG,
)

arena = ShowArena(
    logger=arena_logger,
    border_buffer=2,
    obstacle_buffer=5,
    chunk_size=5,
)

# arena.visualize()
arena.set_team_color("yellow")

path_finder = PathFinder(
    logger=finder_logger,
    start=OrientedPoint((10, 10)),
    goal=OrientedPoint((260, 180)),
    grid_manager=arena.grid_manager,
    path_resolution=1
)
path = path_finder.find_oriented_path(smooth_path=True)

#arena.visualize()
arena.grid_manager.visualize(path=path)
