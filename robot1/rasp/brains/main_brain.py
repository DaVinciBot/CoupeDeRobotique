from config_loader import CONFIG

# ====== Standard Library Imports ======
import matplotlib.pyplot as plt
import numpy as np
import random
import math
import json

# ====== Third-party library imports ======
from ws_comms import WSmsg, WSreceiver, WServerRouteManager, WSender
from loggerplusplus import Logger
from taskbrain import Brain

# ====== Local Library Imports ======
from geometry import OrientedPoint, Point, is_empty
from arena import ShowArena, BaseArenaZone
from navigation import (
    Navigator,
    NavigatorTaskParams,
    TrajectoryPlanCommand,
    PathPlannerPathPlanParamsFactory,
)
from arena import AllyZone, TeamColor

# ====== Internal Project Imports ======
from controllers.rolling_basis import RollingBasis, RollingBasisDummy
from controllers.actuators import Actuators, ActuatorsDummy
from sensors import Lidar
from navigation_tasks.tasks import yellow_start_tasks

from boombot_strategy_old import ShowGameContext

from navigation import (
    DeltaPathPlannerParams,
    SequentialTrajectoryPlannerParams,
    SpeedProfiler,
    StopAndWaitAvoidanceParams,
)


class MainBrain(Brain):
    def __init__(
        self,
        logger: Logger,
        # Sensor
        lidar: Lidar,
        # Environment
        arena: ShowArena,
        # WS routes
        ws_cmd: WServerRouteManager,
    ) -> None:
        self.lidar: Lidar = lidar
        self.arena: ShowArena = arena
        self.ws_cmd: WServerRouteManager = ws_cmd

        # Shared attributes
        self.rolling_basis_odometrie: OrientedPoint = OrientedPoint(0, 0, 0)
        self.navigator_task: NavigatorTaskParams | None = None

        super().__init__(logger, self)

    """
    ### Secondary Processes ###
    """

    """ ### Routines ### """

    @Brain.task(
        process=True,
        run_on_start=False,
        refresh_rate=0.1,
        define_loop_later=True,
        start_loop_marker="# --- MetaProg is insane (loop) --- #",
    )
    def run(self) -> None:
        # --- Initialization --- #
        navigator = Navigator()

        rolling_basis = RollingBasisDummy(
            logger=Logger(identifier="RollingBasis", follow_logger_manager_rules=True)
        )
        rolling_basis.set_odometrie(self.rolling_basis_odometrie)

        # --- MetaProg is insane (loop) --- #
        if self.navigator_task is not None:
            navigator.add_navigation_task(self.navigator_task)
            self.navigator_task = None

        cmd = navigator.handle(
            ally_zone=self.arena.ally_zone,
            enemy_zone=self.arena.enemy_zone,
        )
        rolling_basis.set_speed_and_position(*cmd.get_command())
        self.rolling_basis_odometrie = rolling_basis.odometrie

    """
    ### Main Process ###
    """

    """ ### Routines ### """

    @Brain.task(process=False, run_on_start=True, refresh_rate=0.2)
    async def update_arena(self) -> None:
        # Update the arena with the new position of the robot
        self.arena.update(
            ally_position=self.rolling_basis_odometrie,
            lidar_scan_polars=np.array([]),  # self.lidar.scan_to_polars(),
            optimized_update=True,
            # _enemy_position=self.position_generator(),
        )

    """ ### One-Shot Tasks ### """

    @Brain.task(process=False, run_on_start=True)
    async def start(self):
        self.arena.set_team_color(TeamColor.YELLOW)
        # Start robot position
        start_position = OrientedPoint(20, 25, 0)
        self.arena.enemy_zone.update(
            self.arena.team_color, start_position, Point(290, 190)
        )
        self.rolling_basis_odometrie = start_position

        # Ici met le déplacement que tu veux
        self.navigator_task = NavigatorTaskParams(
            goal=None,
            timeout=None,
            path_planner_params=DeltaPathPlannerParams(distance=10),
            trajectory_planner_params=SequentialTrajectoryPlannerParams(),
            speed_profiler=CONFIG.ROLLING_BASIS_DEFAULT_SPEED_PROFILER,
            avoidance_params=StopAndWaitAvoidanceParams(acs_distance=70, timeout=30),
        )

        await self.run()
