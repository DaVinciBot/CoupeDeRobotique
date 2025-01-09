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

ally_finder_logger = Logger(
    identifier="AllyPathFinder",
    decorator_level=LogLevels.INFO,
    print_log_level=LogLevels.DEBUG,
    file_log_level=LogLevels.DEBUG,
)
enemy_finder_logger = Logger(
    identifier="EnemyPathFinder",
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
    obstacle_buffer=1,
    chunk_size=5,
    forbidden_cover_threshold=0.1,
)

start = OrientedPoint((10, 10))
goal = OrientedPoint((280, 120))

enemy_start = OrientedPoint((230, 60))
enemy_goal = OrientedPoint((70, 140))


arena.set_team_color("yellow")

arena.visualize(display_points=[Point(15, 15), Point(30, 30)])

# Ally path
ally_path_finder = PathFinder(
    logger=ally_finder_logger,
    start=start,
    goal=goal,
    grid_manager=arena.grid_manager,
    path_resolution=5,
)
ally_path = ally_path_finder.find_oriented_path(smooth_path=True)

# Enemy path
enemy_path_finder = PathFinder(
    logger=enemy_finder_logger,
    start=enemy_start,
    goal=enemy_goal,
    grid_manager=arena.grid_manager,
    path_resolution=5,
)
enemy_path = enemy_path_finder.find_oriented_path(smooth_path=True)

arena.update(ally_positions=[], enemy_positions=[], optimized_update=True)
arena.grid_manager.visualize(only_static_grid=True, path=[ally_path])

# Visualize the path forwarding
import matplotlib.pyplot as plt

while len(ally_path) > 3:
    plt.close("all")
    plt.ion()

    arena.update(
        ally_positions=[ally_path[1]],
        enemy_positions=[enemy_path[1]],
        optimized_update=True,
    )

    arena.visualize(display_points=[Point(15, 15), Point(30, 30)])
    arena.grid_manager.visualize(only_static_grid=False, path=[ally_path, enemy_path])
    plt.pause(2)
    ally_path_finder.update_current_position(ally_path[1])
    enemy_path_finder.update_current_position(enemy_path[1])

    ally_path = ally_path_finder.find_oriented_path(
        smooth_path=True, use_static_and_dynamic_grid=True
    )
    enemy_path = enemy_path_finder.find_oriented_path(
        smooth_path=True, use_static_and_dynamic_grid=False
    )
