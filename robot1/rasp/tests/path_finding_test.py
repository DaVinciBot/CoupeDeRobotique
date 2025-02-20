import matplotlib.pyplot as plt
import numpy as np
import math
import random
import time

from matplotlib.animation import FuncAnimation
from config_loader import CONFIG

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

# Import from common
from geometry import OrientedPoint

from arena import (
    ShowArena,
    BaseArenaZone,
    ZoneType,
    EnemyZone,
    StuffZone,
    ForbiddenZone,
    BlueReservedZone,
    YellowReservedZone,
    BorderZone,
)
from movement_manager import MovementManager, GoToParams, MovementStatus
from rolling_basis_handler import SpeedProfile
from pathfinding.core.grid import Grid, GridNode
from loggerplusplus import Logger

from path_finding import PathFinder

start = OrientedPoint(30, 30, 0.0)
goal = OrientedPoint(250, 140, 0.0)

ally_finder_logger = Logger(
    identifier="AllyPathFinder",
    follow_logger_manager_rules=True,
)
enemy_finder_logger = Logger(
    identifier="EnemyPathFinder",
    follow_logger_manager_rules=True,
)

arena_logger = Logger(
    identifier="ShowArena",
    follow_logger_manager_rules=True,
)

arena = ShowArena(
    logger=arena_logger,
    border_buffer=2,
    obstacle_buffer=1,
    chunk_size=5,
    forbidden_cover_threshold=0.1,
)

arena_grid = arena.grid_manager.static_grid

speed_profile: SpeedProfile = SpeedProfile(
    max_linear_speed=5.0,  # cm/s
    max_angular_speed=3.0,  # rad/s
    max_linear_acceleration=5.0,  # cm/s^2
    max_angular_acceleration=3.0,  # rad/s^2
    max_linear_deceleration=10.0,  # cm/s^2
    max_angular_deceleration=3.0,  # rad/s^2
)
go_to_params = GoToParams(
    initial_linear_speed=0,
    initial_angular_speed=0,
    speed_profile=speed_profile,
    goal=OrientedPoint(250, 140),
    acs_distance=10,
    path_finder_recompute_distance=80,
    timeout=-1.0,
    is_mandatory=False,
    smooth_trajectory=False,
    goal_tolerance=0.1,
)

arena.set_team_color("yellow")
arena.update(
    ally_position=start,
    lidar_scan_polars=np.array([]),
)

for i in range(1, 10):
    path_finder = PathFinder(
        logger=Logger(identifier="PathFinder"),
        start=start,
        goal=arena.zones[i].get_go_to_position(start, "yellow"),
        grid_manager=arena.grid_manager,
        path_resolution=1,
    )

    path_finder.find_oriented_path(
        smooth_path=True,
        use_static_and_dynamic_grid=True,
    )

    arena.visualize(trajectory=path_finder.oriented_path_found)
