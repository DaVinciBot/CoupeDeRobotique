import random

from config_loader import CONFIG

# ====== Standard Library Imports ======
import numpy as np
import matplotlib.pyplot as plt
import time
from math import pi


# ====== Third-party library imports ======
from ws_comms import WSmsg, WSreceiver, WServerRouteManager, WSender
from loggerplusplus import Logger
from taskbrain import Brain

# ====== Local Library Imports ======
from geometry import OrientedPoint, Point, is_empty
from arena import ShowArena, BaseArenaZone
from arena import AllyZone, TeamColor

# ====== Internal Project Imports ======
from controllers.rolling_basis import RollingBasis, RollingBasisDummy
from controllers.actuators import ActuatorsShow, ActuatorsShowDummy
from sensors import Lidar, Inputs

from navigation import (
    Navigator,
    NavigatorTaskParams,
    DeltaPathPlannerParams,
    SequentialTrajectoryPlannerParams,
    SpeedProfiler,
    StopAndWaitAvoidanceParams,
    BasicPathPlannerParams,
    NoAvoidanceParams,
)

from navigation.avoidance.acs_detection_profiles import (
    RectangularProjectionAcsDetectionProfileParams,
    NoAcsDetectionProfileParams,
)

from navigation.trajectory_planner import Direction
from usb_com.python.tools import get_all_serial_number

from navigation.navigator.task import NavigatorTaskState

import asyncio


class MainBrain(Brain):
    def __init__(
        self,
        logger: Logger,
        # Sensor
        lidar: Lidar,
        # Environment
        arena: ShowArena,
    ) -> None:
        self.lidar: Lidar = lidar
        self.arena: ShowArena = arena

        # Shared attributes
        self.rolling_basis_odometrie: OrientedPoint = OrientedPoint(0, 0, 0)
        super().__init__(logger, self)

    """
    ### Secondary Processes ###
    """

    """ ### Routines ### """

    @Brain.task(
        process=True,
        run_on_start=False,
        refresh_rate=0.001,
        define_loop_later=True,
        start_loop_marker="# --- MetaProg is insane (loop) --- #",
    )
    def run(self) -> None:
        # --- Initialization --- #
        # from boombot_strategy import ShowGameContext
        # from boombot_strategy.strategies.basic_strategy import BasicStrategy

        # Rolling basis & Actuators
        rolling_basis = RollingBasis(
            logger=Logger(identifier="RollingBasis", follow_logger_manager_rules=True)
        )
        time.sleep(0.01)
        rolling_basis.set_odometrie(self.rolling_basis_odometrie)

        navigator = Navigator()
        navigator.add_navigation_task(
            NavigatorTaskParams(
                goal=None,
                timeout=None,
                path_planner_params=DeltaPathPlannerParams(rotation=pi, distance=40),
                trajectory_planner_params=SequentialTrajectoryPlannerParams(),
                speed_profiler=CONFIG.ROLLING_BASIS_DEFAULT_SPEED_PROFILER,
                avoidance_params=NoAvoidanceParams(),
                acs_detection_profile_params=NoAcsDetectionProfileParams(),
            )
        )

        # --- MetaProg is insane (loop) --- #
        if navigator.current_task is not None:
            cmd = navigator.handle(
                ally_zone=self.arena.ally_zone,
                enemy_zone=self.arena.enemy_zone,
            )
            rolling_basis.set_target_position(cmd.get_position_command())

        self.rolling_basis_odometrie = rolling_basis.odometrie

    @Brain.task(
        process=True,
        run_on_start=True,  # True to get visualization
        refresh_rate=0.01,
        define_loop_later=True,
        start_loop_marker="# --- MetaProg is insane (loop) --- #",
    )
    def visualize_arena(self) -> None:
        # --- Initialization --- #
        fig, ax = plt.subplots()

        # --- MetaProg is insane (loop) --- #
        ax.clear()
        self.arena.visualize(
            # Visualization options
            show_buffer=True,
            # trajectory=self.path,
            display_zones_go_to_positions=True,
            show_ally_direction=True,
            # Plot options
            show=False,
            plot=(ax, fig),
            # Additional options
            # additional_zones=[self.th_ally_zone],
            # additional_points=list(obstacles.geoms) if not is_empty(obstacles) else None,
        )
        plt.pause(0.01)

    """
    ### Main Process ###
    """

    """ ### Routines ### """

    @Brain.task(process=False, run_on_start=True, refresh_rate=0.01)
    async def update_arena(self) -> None:
        # Update the arena with the new position of the robot
        self.arena.update(
            ally_position=self.rolling_basis_odometrie,
            # lidar_scan_polars=np.array([]),
            lidar_scan_polars=self.lidar.scan_to_polars(),  # np.array([]),
            optimized_update=True,
            # _enemy_position=self.position_generator(),
        )

    @Brain.task(process=False, run_on_start=True, refresh_rate=0.1)
    async def print_odo(self) -> None:
        self.logger.info(f"Rolling basis odometrie: {self.rolling_basis_odometrie}")

    """ ### One-Shot Tasks ### """

    @Brain.task(process=False, run_on_start=True)
    async def start(self):
        start_position = OrientedPoint(0, 0, 0)
        # 3. Update the arena with the starting position
        self.arena.enemy_zone.update(
            self.arena.team_color, start_position, Point(300, 200)
        )
        self.arena.update(
            ally_position=start_position,
            lidar_scan_polars=np.array([]),
            optimized_update=False,
        )
        self.rolling_basis_odometrie = start_position
        await self.run()
