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
from controllers.actuators import Actuators, ActuatorsDummy
from sensors import Lidar

from GPIO import PIN

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
)

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
        ws_ui: WServerRouteManager,
        # Tirette
        jack: PIN = None,
    ) -> None:
        self.lidar: Lidar = lidar
        self.arena: ShowArena = arena
        self.ws_cmd: WServerRouteManager = ws_cmd
        self.ws_ui: WServerRouteManager = ws_ui

        # Shared attributes
        self.rolling_basis_odometrie: OrientedPoint = OrientedPoint(0, 0, 0)
        self.navigator_task: NavigatorTaskParams = None

        self.ui_state = {
            "jack_state": False,
            "acs_state": False,
            "odometrie_state": OrientedPoint(0, 0, 0),
            "pamis_state": False,
        }

        self.jack = jack
        
        self.lidar_points: list[Point] = []

        super().__init__(logger, self)

    """
    ### Secondary Processes ###
    """

    """ ### Routines ### """

    # Deactivate for now
    @Brain.task(process=False, run_on_start=False)
    async def wait_for_trigger(self):
        false_jacks_in_a_row = 0
        while false_jacks_in_a_row < 5:
            if self.jack.safe_digital_read():
                false_jacks_in_a_row = 0
                jack_state: bool = self.jack.digital_read()
                self.ui_state["jack_state"] = jack_state
                self.logger.info(f"Jack state: {jack_state}")
            else:
                false_jacks_in_a_row += 1
                self.logger.info(f"Jack state: {self.jack.digital_read()}")
            await asyncio.sleep(0.1)

    @Brain.task(
        process=True,
        run_on_start=False,
        refresh_rate=0.001,
        define_loop_later=True,
        start_loop_marker="# --- MetaProg is insane (loop) --- #",
    )
    def run(self) -> None:
        # --- Initialization --- #
        from boombot_strategy import ShowGameContext, yellow_strategy_runner, NavigationTask

        navigator = Navigator()

        # Rolling basis & Actuators
        rolling_basis = RollingBasis(
            logger=Logger(identifier="RollingBasis", follow_logger_manager_rules=True)
        )
        rolling_basis.set_odometrie(self.rolling_basis_odometrie)
        time.sleep(1)

        navigator.add_navigation_task(
            NavigatorTaskParams(
                goal=OrientedPoint(40, 50, 0),
                timeout=None,
                path_planner_params=BasicPathPlannerParams(),
                trajectory_planner_params=SequentialTrajectoryPlannerParams(),
                speed_profiler=CONFIG.ROLLING_BASIS_DEFAULT_SPEED_PROFILER,
                avoidance_params=StopAndWaitAvoidanceParams(
                    acs_distance=100, timeout=30
                ),
            )
        )

        # --- MetaProg is insane (loop) --- #

        if navigator.current_task is not None:
            cmd = navigator.handle(
                ally_zone=self.arena.ally_zone,
                enemy_zone=self.arena.enemy_zone,
            )
            rolling_basis.set_speed_and_position(*cmd.get_command())

        # yellow_strategy_runner.handle(
        #     ShowGameContext(
        #         arena=self.arena, rolling_basis=rolling_basis, actuators=actuators
        #     )
        # )

        # if navigator.current_task.state == NavigatorTaskState.AVOIDING:
        #       self.ui_state["acs_state"] = True
        if isinstance(yellow_strategy_runner.active[0].tasks[0], NavigationTask):
            if yellow_strategy_runner.active[0].tasks[0].navigator_task.state == NavigatorTaskState.AVOIDING :
                self.ui_state["acs_state"] = True

        self.rolling_basis_odometrie = rolling_basis.odometrie
        self.ui_state["odometrie_state"] = rolling_basis.odometrie

    @Brain.task(
        process=True,
        run_on_start=True,
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
            additional_points=self.lidar_points,
        )
        plt.pause(0.01)

    """
    ### Main Process ###
    """

    """ ### Routines ### """

    @Brain.task(
        process=False,
        run_on_start=True,
        refresh_rate=1,
        define_loop_later=True,
        start_loop_marker="# --- MetaProg is insane (loop) --- #",
    )
    async def update_ui(self):
        previous_state = self.ui_state.copy()

        # --- MetaProg is insane (loop) --- #
        current_state = self.ui_state.copy()

        if current_state != previous_state:
            previous_state = current_state
            to_send = {
                "jack_state": current_state["jack_state"],
                "acs_state": current_state["acs_state"],
                "odometrie": {
                    "x": current_state["odometrie_state"].x,
                    "y": current_state["odometrie_state"].y,
                    "theta": current_state["odometrie_state"].theta,
                },
                "pamis_state": current_state["pamis_state"],
            }
            await self.ws_ui.sender.send(
                WSmsg(sender="server", msg="update ui data", data=to_send),
                clients=self.ws_ui.get_client("ui")
            )

    @Brain.task(process=False, run_on_start=True, refresh_rate=0.01)
    async def update_arena(self) -> None:
        # Update the arena with the new position of the robot
        self.arena.update(
            ally_position=self.rolling_basis_odometrie,
            lidar_scan_polars=self.lidar.scan_to_polars(),  # np.array([]),
            optimized_update=True,
            # _enemy_position=self.position_generator(),
        )

        self.lidar_points = self.arena.remove_outside(
            self.arena._pol_to_abs_cart(self.lidar.scan_to_polars())
        )


    @Brain.task(process=False, run_on_start=True, refresh_rate=1)
    async def print_odo(self) -> None:
        self.logger.info(f"Rolling basis odometrie: {self.rolling_basis_odometrie}")

    """ ### One-Shot Tasks ### """

    @Brain.task(process=False, run_on_start=True)
    async def start(self):
        await self.wait_for_trigger()
        self.arena.set_team_color(TeamColor.YELLOW)
        # Start robot position
        start_position = OrientedPoint(13, 17, 0)
        self.arena.enemy_zone.update(
            self.arena.team_color, start_position, Point(290, 190)
        )
        self.rolling_basis_odometrie = start_position
        await asyncio.sleep(1)

        await self.run()
