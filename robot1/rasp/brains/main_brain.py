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
from movement import (
    MovementManager,
    GoToParams,
    TrajectoryParams,
    SpeedProfile,
    RollingBasisCommand,
)
from arena import AllyZone, TeamColor

# ====== Internal Project Imports ======
from controllers.rolling_basis import RollingBasis, RollingBasisDummy
from sensors import Lidar


class MainBrain(Brain):
    def __init__(
            self,
            logger: Logger,
            # Sensor
            lidar: Lidar,
            # Environment
            arena: ShowArena,
            # WS routes
            ws_cmd: WServerRouteManager
    ) -> None:
        # Sensor
        self.lidar: Lidar = lidar
        # Environment
        self.arena: ShowArena = arena
        # WS routes
        self.ws_cmd: WServerRouteManager = ws_cmd

        # Shared processes attributes
        self.rolling_basis_odometrie = OrientedPoint(0, 0, 0)

        self.go_to_params: GoToParams | None = None

        # For test purpose
        self.th_ally_zone: AllyZone = AllyZone(
            logger=Logger(identifier="th_ally", follow_logger_manager_rules=True),
            point=self.rolling_basis_odometrie,
            robot_size=5,
        )
        self.th_ally_zone.zone_color = "#82795f"

        self.path: list[OrientedPoint] = []

        super().__init__(logger, self)

        # Attributes for the visualization
        self.fig, self.ax = plt.subplots()

    """
    ### Secondary Processes ###
    """

    """ ### Routines ### """


    @Brain.task(
        process=True,
        run_on_start=True,
        refresh_rate=0.1,
        define_loop_later=True,
        start_loop_marker="# --- MetaProg is insane (loop) --- #",
    )
    def handle_movement_manager(self) -> None:

        # --- Initialization --- #
        movement_manager = MovementManager(
            logger=Logger(identifier="MovementManager", follow_logger_manager_rules=True),
            path_finder_logger=Logger(identifier="PathFinder", follow_logger_manager_rules=True),
            trajectory_computer_logger=Logger(identifier="TrajectoryComputer", follow_logger_manager_rules=True),
            arena_ptr=self.arena,
        )

        rolling_basis = RollingBasisDummy(
            logger=Logger(identifier="RollingBasis", follow_logger_manager_rules=True)
        )

        if isinstance(rolling_basis, RollingBasisDummy):
            rolling_basis.logger.warning("RollingBasisDummy is used")

        # --- MetaProg is insane (loop) --- #

        # Update rolling basis odometrie if main process has updated it
        if self.rolling_basis_odometrie != rolling_basis.odometrie:
            rolling_basis.set_odometrie(self.rolling_basis_odometrie)

        # Force the sync of arena inside the movement_manager
        movement_manager.arena_ptr = self.arena

        # Trigger movement manager to go to the new destination when the params change
        if self.go_to_params != movement_manager.params:

            movement_manager.compute_go_to(
                current_linear_speed=rolling_basis.linear_speed,
                current_angular_speed=rolling_basis.angular_speed,
                params=self.go_to_params,
            )
            movement_manager.logger.info("New GoToParams received")
            movement_manager.timeout_movement(reset=True)

        if movement_manager.timeout_movement():
            rolling_basis.set_speed_and_position(0, 0, self.rolling_basis_odometrie)

        # Handle the 'go to' command
        if movement_manager.params is not None:
            cmd: RollingBasisCommand = movement_manager.handle_go_to()
            if cmd is not None:
                self.th_ally_zone = AllyZone(
                    logger=Logger(identifier="th_ally"), point=cmd.position, robot_size=5
                )
                rolling_basis.set_speed_and_position(*cmd.get_command())
                self.rolling_basis_odometrie = rolling_basis.odometrie
                self.path = movement_manager.trajectory_computer.path_to_follow

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
        )

        # obstacles = self.arena.remove_outside(
        #     self.arena._pol_to_abs_cart(self.lidar.scan_to_polars())
        # )

        # Visualize the arena
        self.ax.clear()
        self.arena.visualize(
            # Visualization options
            show_buffer=True,
            trajectory=self.path,
            display_zones_go_to_positions=True,
            show_ally_direction=True,
            # Plot options
            show=False,
            plot=(self.ax, self.fig),
            # Additional options
            additional_zones=[self.th_ally_zone],
            # additional_points=list(obstacles.geoms) if not is_empty(obstacles) else None,
        )
        plt.pause(0.01)

    @Brain.task(process=False, run_on_start=True, refresh_rate=0.5)
    async def zombie_mode(self):
        """
        executes requests received by the server. Use Postman to send request to the server
        Use eval and await eval to run the code you want. Code must be sent as a string
        """
        # Check cmd
        cmd = await self.ws_cmd.receiver.get(wait_msg=True)

        if cmd != WSmsg():
            self.logger.info(f"Zombie instruction {cmd.msg} received: {cmd.data}")

            instructions = []
            if isinstance(cmd.data, str):
                instructions.append(cmd.data)
            elif isinstance(cmd.data, list):
                instructions = cmd.data

            # Exec: for attribution cases (x = 1)
            if cmd.msg == "exec":
                for instruction in instructions:
                    exec(instruction)

            # Eval: for return cases (print(x))
            elif cmd.msg == "eval":
                instructions = []
                execution = "No instructions"
                if isinstance(cmd.data, str):
                    instructions.append(cmd.data)
                elif isinstance(cmd.data, list):
                    instructions = cmd.data
                for instruction in instructions:
                    if instruction.startswith("await "):
                        execution = await eval(instruction.removeprefix("await "))
                    else:
                        execution = eval(instruction)
                message = WSmsg.from_json({
                    "sender": CONFIG.WS_SENDER_NAME,
                    "msg": "Execution of sender instruction",
                    "data": str(execution)
                })
                await self.ws_cmd.sender.send(message)

            else:
                self.logger.warning(
                    f"Command not implemented: {cmd.msg} / {cmd.data}",
                )

    """ ### One-Shot Tasks ### """

    @Brain.task(process=False, run_on_start=True)
    async def start(self):
        self.arena.set_team_color(TeamColor.YELLOW)
        # Start robot position
        self.rolling_basis_odometrie = OrientedPoint(50, 50, 0)
        self.arena.enemy_zone.update(self.arena.team_color, self.rolling_basis_odometrie, Point(290, 190))


"""
This main brain is dedicated to test the robot movement WITHOUT Lidar.

Use ZOMBIE_MODE to send instructions to the robot.
Instruction example:
---
self.go_to_params = GoToParams(
    trajectory_params=TrajectoryParams(
        speed_profile=SpeedProfile.from_dict(
            CONFIG.ROLLING_BASIS_HIGH_SPEED_PROFILE
        ),
        goal=OrientedPoint(250, 140),
        resolution=1,
        smooth_trajectory=True,
    ),
    acs_distance=30,
    path_finder_recompute_distance=80,
    timeout=-1.0,
    is_mandatory=False,
    goal_tolerance=0.1,
    distance_to_goal_to_dont_recompute_path=10,
)
---

Exemple in postman with zombie mode:
url: ws://rob.local:8080/cmd?sender=postman_zombie
url: ws://localhost:8080/cmd?sender=postman_zombie
message:
{
    "sender": "zombie_master",
    "msg": "exec",
    "data": "self.go_to_params = GoToParams(trajectory_params=TrajectoryParams(speed_profile=SpeedProfile.from_dict(CONFIG.ROLLING_BASIS_HIGH_SPEED_PROFILE), goal=OrientedPoint(250, 140), resolution=1, smooth_trajectory=True), acs_distance=30, path_finder_recompute_distance=80, timeout=-1.0, is_mandatory=False, goal_tolerance=0.1, distance_to_goal_to_dont_recompute_path=10)"
}
"""
