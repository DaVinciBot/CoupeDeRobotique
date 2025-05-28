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
from controllers.actuators import ActuatorsShow, ActuatorsDummy
from sensors import Lidar, Inputs

# from navigation_tasks.tasks import yellow_start_tasks

# from boombot_strategy import ShowGameContext

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
        # WS routes
        ws_cmd: WServerRouteManager,
        # Inputs
        inputs: Inputs,
    ) -> None:
        self.lidar: Lidar = lidar
        self.arena: ShowArena = arena

        # Shared attributes
        self.rolling_basis_odometrie: OrientedPoint = OrientedPoint(0, 0, 0)

        super().__init__(logger, self)

        self.ws_cmd: WServerRouteManager = ws_cmd
        self.inputs: Inputs = inputs

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
        from boombot_strategy import ShowGameContext
        from boombot_strategy.strategies.homologation import homologation_runner

        # Rolling basis & Actuators
        rolling_basis = RollingBasis(
            logger=Logger(identifier="RollingBasis", follow_logger_manager_rules=True)
        )
        time.sleep(1)
        rolling_basis.set_odometrie(self.rolling_basis_odometrie)

        actuators = ActuatorsShow(
            logger=Logger(identifier="Actuators", follow_logger_manager_rules=True)
        )

        # --- MetaProg is insane (loop) --- #
        homologation_runner.handle(
            ShowGameContext(
                arena=self.arena, rolling_basis=rolling_basis, actuators=actuators
            )
        )
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
            lidar_scan_polars=np.array([]),  # self.lidar.scan_to_polars(),
            optimized_update=True,
            # _enemy_position=self.position_generator(),
        )

    """ ### One-Shot Tasks ### """

    @Brain.task(process=False, run_on_start=True)
    async def start(self):
        self.arena.set_team_color(TeamColor.YELLOW)
        # Start robot position
        start_position = OrientedPoint(100, 66, 0)

        self.arena.enemy_zone.update(
            self.arena.team_color, start_position, Point(290, 190)
        )
        self.rolling_basis_odometrie = start_position

        await asyncio.sleep(1)
        await self.inputs.wait_for_jack_trigger()
        await self.run()
