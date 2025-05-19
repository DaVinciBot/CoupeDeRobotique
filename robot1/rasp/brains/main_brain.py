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

# from navigation_tasks.tasks import yellow_start_tasks

# from boombot_strategy import ShowGameContext

from navigation import (
    Navigator,
    NavigatorTaskParams,
    DeltaPathPlannerParams,
    SequentialTrajectoryPlannerParams,
    SpeedProfiler,
    StopAndWaitAvoidanceParams,
)

from usb_com.python.tools import get_all_serial_number

from navigation.navigator.task import NavigatorTaskState

from GPIO import PIN

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
        #Tirette
        jack: None
    ) -> None:
        self.lidar: Lidar = lidar
        self.arena: ShowArena = arena
        self.ws_cmd: WServerRouteManager = ws_cmd

        # Shared attributes
        self.rolling_basis_odometrie: OrientedPoint = OrientedPoint(0, 0, 0)
        self.navigator_task: NavigatorTaskParams = None
        
        self.jack = jack

        super().__init__(logger, self)

    """
    ### Secondary Processes ###
    """

    """ ### Routines ### """
    
    @Brain.task(process=True, run_on_start=False)
    async def wait_for_trigger(self):
        """
        Waits for a trigger signal from the jack.

        This function continuously checks the state of the jack and waits until it is triggered.
        While waiting, it shows the team LED and sleeps for 0.1 seconds between each check.
        Once triggered, it sets the jack LED to True.
        """
        # Check jack state
        false_jacks_in_a_row = 0
        while false_jacks_in_a_row < 5:
            if self.jack.safe_digital_read():
                false_jacks_in_a_row = 0
            else:
                false_jacks_in_a_row += 1
            await asyncio.sleep(0.1)


    @Brain.task(
        process=True,
        run_on_start=False,
        refresh_rate=0.000001,
        define_loop_later=True,
        start_loop_marker="# --- MetaProg is insane (loop) --- #",
    )
    def run(self) -> None:
        # --- Initialization --- #
        from boombot_strategy import ShowGameContext, yellow_strategy_runner

        navigator = Navigator()

        # Rolling basis & Actuators
        rolling_basis = RollingBasis(
            logger=Logger(identifier="RollingBasis", follow_logger_manager_rules=True)
        )
        rolling_basis.set_odometrie(self.rolling_basis_odometrie)
        
        #self.wait_for_trigger() A faire après avoir fix GPIO
        #time.sleep(500) A utiliser pour les matchs pour l'instant
        
        for i in range(20, 51, 0.5):
            rolling_basis.set_speed_and_position(0.0, 0.0, OrientedPoint(i, 25, 0))
            time.sleep(0.1)

        for i in range(0, 3.14, 0.1):
            rolling_basis.set_speed_and_position(0.0, 0.0, OrientedPoint(50, 25, -i))
            time.sleep(0.1)

        for i in range(51, 21, -0.5):
            rolling_basis.set_speed_and_position(0.0, 0.0, OrientedPoint(i, 25, 3.14))
            time.sleep(0.1)


        # --- MetaProg is insane (loop) --- #
        rolling_basis.logger.info(rolling_basis.odometrie)
        time.sleep(1)
        """if self.navigator_task is not None:
            navigator.add_navigation_task(self.navigator_task)
            self.navigator_task = None

        cmd = navigator.handle(
            ally_zone=self.arena.ally_zone,
            enemy_zone=self.arena.enemy_zone,
        )
        #rolling_basis.set_speed_and_position(*cmd.get_command())
        # yellow_strategy_runner.handle(
        #     ShowGameContext(
        #         arena=self.arena, rolling_basis=rolling_basis, actuators=actuators
        #     )
        # )
        self.rolling_basis_odometrie = rolling_basis.odometrie"""

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
        start_position = OrientedPoint(20, 25, 0)
        self.arena.enemy_zone.update(
            self.arena.team_color, start_position, Point(290, 190)
        )
        self.rolling_basis_odometrie = start_position

        # Ici met le déplacement que tu veux
        # self.navigator_task = NavigatorTaskParams(
        #     goal=None,
        #     timeout=None,
        #     path_planner_params=DeltaPathPlannerParams(distance=10),
        #     trajectory_planner_params=SequentialTrajectoryPlannerParams(),
        #     speed_profiler=CONFIG.ROLLING_BASIS_SPEED_PROFILER_PID,
        #     avoidance_params=StopAndWaitAvoidanceParams(acs_distance=70, timeout=30),
        # )
        # get_all_serial_number()
        # godHand = Actuators(
        #     logger=Logger(identifier="Actuators", follow_logger_manager_rules=True)
        # )
        # godHand.set_servo_angle(
        #     pin=0, angle=90, min_angle=0, max_angle=180, detach=False, detach_delay=1000
        # )
        # godHand.set_servo_angle(
        #     pin=1, angle=90, min_angle=0, max_angle=180, detach=False, detach_delay=1000
        # )
        # godHand.set_  servo_angle(
        #     pin=2, angle=90, min_angle=0, max_angle=180, detach=False, detach_delay=1000
        # )
        # godHand.set_servo_angle(
        #     pin=3, angle=90, min_angle=0, max_angle=180, detach=False, detach_delay=1000
        # )

        # godHand.logger.info("Servo angle set to 90 degrees")
        await self.run()
