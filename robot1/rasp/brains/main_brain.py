"""Entry point for running the robot's main brain."""

from __future__ import annotations

import asyncio
import time
from math import pi
from typing import TYPE_CHECKING, Any

import matplotlib.pyplot as plt
import numpy as np
from loggerplusplus import Logger
from taskbrain import Brain
from ws_comms import WServerRouteManager, WSmsg

from a_config_loader import CONFIG
from arena.base_arena import TeamColor
from boombot_strategy import ShowGameContext
from boombot_strategy.strategies import TowerRushAltStrategy
from boombot_strategy.sub_graphs import (
    get_banner_deployment_subgraph,
    get_construct_one_floor_subgraph,
    get_construct_subgraph,
    get_pickup_subgraph,
    get_push_one_floor_to_wall_subgraph,
)
from boombot_strategy.tasks.navigation_tasks import GoToOrientedPoint, SetOdometrie
from controllers.actuators import ActuatorsShow, ActuatorsShowDummy
from controllers.rolling_basis import RollingBasis, RollingBasisDummy
from geometry import OrientedPoint
from strategy.core import GraphRunner
from strategy.core.task_nodes import BaseTaskNode

if TYPE_CHECKING:
    from strategy.core.tasks import BaseTask

if TYPE_CHECKING:
    from arena.show_arena import ShowArena
    from sensors import Inputs, Lidar, LidarDummy


class MainBrain(Brain):
    """Main brain for the robot."""

    def __init__(
        self,
        logger: Logger,
        # Sensor
        lidar: Lidar | LidarDummy,
        # Environment
        arena: ShowArena,
        # WS routes
        ws_cmd: WServerRouteManager,
        ws_ui: WServerRouteManager,
        # Inputs
        inputs: Inputs,
    ) -> None:
        """Initializes the MainBrain with the necessary components.

        Args:
            logger (Logger): Logger instance for logging messages.
            lidar (Lidar | LidarDummy): Lidar instance for distance measurements.
            arena (ShowArena): Arena instance for representing the game arena.
            ws_cmd (WServerRouteManager): WebSocket command route manager.
            ws_ui (WServerRouteManager): WebSocket UI route manager.
            inputs (Inputs): Inputs instance for handling sensor data.
        """
        self.lidar: Lidar | LidarDummy = lidar
        self.arena: ShowArena = arena
        self.mode: str | None = None
        self.status: str = "launching"

        # Shared attributes
        self.rolling_basis_odometrie: OrientedPoint = OrientedPoint(0, 0, 0)
        self.task_name: str = ""
        self.task_todo: list[BaseTask[ShowGameContext]] = []
        self.task_type: str = ""
        self.should_update_task: bool = False
        self.score: int = 0

        self.should_update_pid: bool = False
        self.pid_type: str = ""
        self.pid_kp: float = 0.0
        self.pid_ki: float = 0.0
        self.pid_kd: float = 0.0

        self.jack_triggered: bool = False
        self.jack_plugged: bool = False
        super().__init__(logger, self)

        self.ws_cmd: WServerRouteManager = ws_cmd
        self.ws_ui: WServerRouteManager = ws_ui
        self.inputs: Inputs = inputs
        self.score: int
        self.should_send_start: bool = False

        self.bau_state: bool = True
        self.odemetrie_state: OrientedPoint = OrientedPoint(0, 0, 0)
        self.enemy_odemetrie_state: OrientedPoint = OrientedPoint(0, 0, 0)
        self.pamis_states: dict[str, bool] = {
            "superstar": False,
            "groupie_1": False,
            "groupie_2": False,
            "groupie_3": False,
        }

    # ====== Secondary Processes =======

    # region ====== Routines =======

    @Brain.task(
        process=True,
        run_on_start=False,
        refresh_rate=0.01,  # 100Hz
        define_loop_later=True,
        start_loop_marker="# --- MetaProg is insane (loop) --- #",
    )
    def run(self) -> None:
        """Runs the main control loop for the robot."""
        # --- Initialization --- #
        # --- 1) Initialize subsystems --- #
        if CONFIG.ROLLING_BASIS_DUMMY:
            rolling_basis: RollingBasis | RollingBasisDummy = RollingBasisDummy(
                logger=Logger(
                    identifier="RollingBasisDummy",
                    follow_logger_manager_rules=True,
                ),
            )
        else:
            rolling_basis = RollingBasis(
                logger=Logger(
                    identifier="RollingBasis",
                    follow_logger_manager_rules=True,
                ),
            )
        rolling_basis.set_odometrie(self.rolling_basis_odometrie)
        rolling_basis.initialize_pids()

        if CONFIG.ACTUATORS_DUMMY:
            actuators: ActuatorsShow | ActuatorsShowDummy = ActuatorsShowDummy(
                logger=Logger(
                    identifier="Actuators",
                    follow_logger_manager_rules=True,
                ),
            )
        else:
            actuators = ActuatorsShow(
                logger=Logger(
                    identifier="Actuators",
                    follow_logger_manager_rules=True,
                ),
            )
        actuators.deplacement_position()
        # --- 2) Wait for jack plug ● Deploy banner block ● Wait for trigger --- #
        if (
            not CONFIG.LIDAR_DUMMY
            or not CONFIG.ROLLING_BASIS_DUMMY
            or not CONFIG.ACTUATORS_DUMMY
        ):
            while not self.jack_plugged:  # wait until cable is plugged
                time.sleep(0.1)
        else:
            time.sleep(2)
        actuators.block_banner()  # engage the banner blocker
        rolling_basis.set_odometrie(self.rolling_basis_odometrie)
        rolling_basis.initialize_pids()
        while not self.jack_triggered:  # wait for the trigger event
            time.sleep(0.1)

        # --- 3) Build the strategy --- #

        # Choose strategy based on configuration
        strategy: TowerRushAltStrategy | None = None
        action_holder: list[GraphRunner | None] = [None]

        if self.mode == "iihm":
            self.logger.info("IIHM mode: Waiting for first task...")
        else:
            strategy = TowerRushAltStrategy(
                ShowGameContext(
                    arena=self.arena,
                    rolling_basis=rolling_basis,
                    actuators=actuators,
                    score=self.score,
                ),
            )
        rolling_basis.set_odometrie(OrientedPoint(0, 0, 0))

        self.should_send_start = True
        self.status = "starting"

        # from strategy.tools import visualize_task_graph
        # visualize_task_graph(strategy.runner.active[0])

        # --- MetaProg is insane (loop) --- #
        context = ShowGameContext(
            arena=self.arena,
            rolling_basis=rolling_basis,
            actuators=actuators,
            score=self.score,
        )

        if strategy:
            strategy.runner.handle(context)
        else:
            if self.should_update_task:
                zone: int | None = self.arena.get_current_zone_id()
                if self.task_type == "navigation":
                    action_holder[0] = GraphRunner(
                        logger=Logger(
                            identifier="IIHMRunner",
                            follow_logger_manager_rules=True,
                        ),
                        start=BaseTaskNode(
                            name=f"[Debug] {self.task_name}",
                            tasks=self.task_todo,
                        ),
                    )
                elif self.task_type == "banner_deploy":
                    action_holder[0] = GraphRunner(
                        logger=Logger(
                            identifier="IIHMRunner",
                            follow_logger_manager_rules=True,
                        ),
                        start=get_banner_deployment_subgraph().get_entry(),
                    )
                elif self.task_type == "construct" and zone is not None:
                    action_holder[0] = GraphRunner(
                        logger=Logger(
                            identifier="IIHMRunner",
                            follow_logger_manager_rules=True,
                        ),
                        start=get_construct_subgraph(
                            zone,
                        ).get_entry(),
                    )
                elif self.task_type == "pickup" and zone is not None:
                    action_holder[0] = GraphRunner(
                        logger=Logger(
                            identifier="IIHMRunner",
                            follow_logger_manager_rules=True,
                        ),
                        start=get_pickup_subgraph(
                            zone,
                        ).get_entry(),
                    )
                elif self.task_type == "push_floor" and zone is not None:
                    action_holder[0] = GraphRunner(
                        logger=Logger(
                            identifier="IIHMRunner",
                            follow_logger_manager_rules=True,
                        ),
                        start=get_push_one_floor_to_wall_subgraph(
                            zone,
                            30,
                        ).get_entry(),
                    )
                elif self.task_type == "construct_one_floor" and zone is not None:
                    action_holder[0] = GraphRunner(
                        logger=Logger(
                            identifier="IIHMRunner",
                            follow_logger_manager_rules=True,
                        ),
                        start=get_construct_one_floor_subgraph(
                            zone,
                        ).get_entry(),
                    )
                elif self.task_type == "reset_odometry":
                    action_holder[0] = GraphRunner(
                        logger=Logger(
                            identifier="IIHMRunner",
                            follow_logger_manager_rules=True,
                        ),
                        start=BaseTaskNode(
                            name="[Debug] Reset Odometry",
                            tasks=[
                                SetOdometrie(0, 0, 0),
                            ],
                        ),
                    )
                self.should_update_task = False
            if action_holder[0] is not None:
                action_holder[0].handle(context)

        if self.should_update_pid:
            if self.pid_type == "linear":
                rolling_basis.set_linear_position_pid(
                    kp=self.pid_kp,
                    ki=self.pid_ki,
                    kd=self.pid_kd,
                )
            elif self.pid_type == "angular":
                rolling_basis.set_angular_position_pid(
                    kp=self.pid_kp,
                    ki=self.pid_ki,
                    kd=self.pid_kd,
                )
            self.should_update_pid = False

        # Update shared state from the context
        self.score = context.score
        self.odemetrie_state = context.arena.ally_zone.point
        self.enemy_odemetrie_state = context.arena.enemy_zone.point
        self.rolling_basis_odometrie = rolling_basis.odometrie

    @Brain.task(
        process=True,
        run_on_start=True,  # True to get visualization
        refresh_rate=0.01,
        define_loop_later=True,
        start_loop_marker="# --- MetaProg is insane (loop) --- #",
    )
    def visualize_arena(self) -> None:
        """Visualizes the arena."""
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
            # additional_points=list(obstacles.geoms)
            # if not is_empty(obstacles)
            # else None,
        )
        plt.pause(0.01)

    # endregion

    # ====== Main Process ======

    # region ====== Routines ======

    @Brain.task(
        process=False,
        run_on_start=True,
        refresh_rate=0.5,
    )
    async def update_ui(self) -> None:
        """Updates the UI with the current state."""
        current_snapshot: dict[str, Any] = {
            "jack_state": not self.jack_triggered,
            "bau_state": self.bau_state,
            "odometrie": {
                "x": self.odemetrie_state.x,
                "y": self.odemetrie_state.y,
                "theta": self.odemetrie_state.theta,
            },
            "enemy_odometrie": {
                "x": self.enemy_odemetrie_state.x,
                "y": self.enemy_odemetrie_state.y,
                "theta": self.enemy_odemetrie_state.theta,
            },
            "pamis_states": self.pamis_states,
            "arena_info": {
                "width": self.arena.width,
                "height": self.arena.height,
            },
            "score": self.score,
        }
        if self.arena.team_color and self.arena.team_color != TeamColor.UNDEFINED:
            to_send = {
                "jack_state": current_snapshot["jack_state"],
                "bau_state": current_snapshot["bau_state"],
                "odometrie": current_snapshot["odometrie"],
                "enemy_odometrie": current_snapshot["enemy_odometrie"],
                "pamis_states": current_snapshot["pamis_states"],
                "arena_info": current_snapshot["arena_info"],
                "score": current_snapshot["score"],
            }
            await self.ws_ui.sender.send(
                WSmsg(sender="server", msg="update ui data", data=to_send),
            )
            if self.should_send_start:
                self.should_send_start = False
                await self.ws_ui.sender.send(
                    WSmsg(sender="server", msg="starting", data={}),
                )

    @Brain.task(process=False, run_on_start=True, refresh_rate=0.5)
    async def receive_ui_data(self) -> None:
        """Executes requests received by the server.

        Use Postman to send request to the server
        Use eval and await eval to run the code you want. Code must be sent as a string
        """
        ui = await self.ws_ui.receiver.get()

        if ui != WSmsg():
            self.logger.info(f"UI instruction {ui.msg} received: {ui.data}")
            if ui.msg == "team change":
                if ui.data["team"] in {"yellow", "blue"}:
                    self.arena.set_team_color(TeamColor[ui.data["team"].upper()])
                    self.logger.info(f"Team color set to {ui.data['team']}")
                else:
                    self.logger.warning(f"Invalid team color: {ui.data}")
            elif ui.msg == "mode change":
                if ui.data["mode"] in {"normal", "iihm"}:
                    self.mode = ui.data["mode"]
                    self.logger.info(f"Mode set to {ui.data['mode']}")
                    await self.ws_ui.sender.send(
                        WSmsg(
                            sender="server",
                            msg="mode set",
                            data={"mode": self.mode},
                        ),
                    )
                else:
                    self.logger.warning(f"Invalid mode: {ui.data}")
            elif ui.msg == "hello":
                await self.receive_hello()
            elif ui.msg == "action":
                if ui.data["type"] == "go to point":
                    x = float(ui.data["data"]["x"])
                    y = float(ui.data["data"]["y"])
                    theta = float(ui.data["data"]["theta"])
                    self.task_name = f"Go to point ({x}, {y}, {theta})"
                    self.task_todo = [
                        GoToOrientedPoint(OrientedPoint(x, y, theta)),
                    ]
                    self.task_type = "navigation"
                    self.should_update_task = True
                    self.logger.info(
                        f"Set task to {self.task_name}",
                    )
                elif ui.data["type"] in {
                    "banner_deploy",
                    "construct",
                    "pickup",
                    "push_floor",
                    "construct_one_floor",
                    "reset_odometry",
                }:
                    self.task_type = ui.data["type"]
                    self.should_update_task = True
                    self.logger.info(
                        f"Set task to {self.task_name}",
                    )
                else:
                    self.logger.warning(f"Unknown action type: {ui.data['type']}")
            elif ui.msg == "pid update":
                kp = float(ui.data["data"]["kp"])
                ki = float(ui.data["data"]["ki"])
                kd = float(ui.data["data"]["kd"])
                pid_type: str = str(ui.data["type"])
                self.pid_kp = kp
                self.pid_ki = ki
                self.pid_kd = kd
                self.logger.info(
                    f"Updating {pid_type} PID to Kp: {kp}, Ki: {ki}, Kd: {kd}",
                )
                self.pid_type = pid_type
                self.should_update_pid = True
            else:
                self.logger.warning(f"Command not implemented: {ui.msg} / {ui.data}")

    @Brain.task(process=False, run_on_start=True, refresh_rate=0.01)
    async def update_arena(self) -> None:
        """Updates the arena with the current position of the robot."""
        self.arena.update(
            ally_position=self.rolling_basis_odometrie,
            lidar_scan_polars=self.lidar.scan_to_polars(),
            optimized_update=True,
            # _enemy_position=self.position_generator(),
        )

    # @Brain.task(process=False, run_on_start=False, refresh_rate=0.1)
    # async def print_odo(self) -> None:
    #     self.logger.info(f"Rolling basis odometrie: {self.rolling_basis_odometrie}")

    # endregion

    # region ====== One-Shot Tasks ======

    @Brain.task(process=False, run_on_start=False)
    async def receive_hello(self) -> None:
        """Sends the current status to the UI upon receiving a hello message."""
        current_status = "unknown"
        data = {}
        if not self.mode:
            current_status = "waiting for mode"
        elif self.arena.team_color == TeamColor.UNDEFINED:
            current_status = "waiting for team color"
            data = {"mode": self.mode}
        elif self.status == "initializing":
            current_status = "initializing"
            data = {
                "mode": self.mode,
                "team": self.arena.team_color.name.lower(),
            }
        elif self.status == "starting":
            current_status = "starting"
            data = {
                "mode": self.mode,
                "team": self.arena.team_color.name.lower(),
            }

        await self.ws_ui.sender.send(
            WSmsg(
                sender="server",
                msg="status",
                data={
                    "status": current_status,
                    "data": data,
                },
            ),
        )

    @Brain.task(process=False, run_on_start=False)
    async def wait_for_mode(self) -> None:
        """Waits for the mode to be set before starting the brain."""
        while self.mode is None:
            await asyncio.sleep(0.1)

        self.logger.info(
            f"Mode is set to {self.mode}.Continuing.",
        )

    @Brain.task(process=False, run_on_start=False)
    async def wait_for_team(self) -> None:
        """Waits for the team color to be set before starting the brain."""
        while self.arena.team_color == TeamColor.UNDEFINED:
            await asyncio.sleep(0.1)

        self.logger.info(
            f"Team color is set to {self.arena.team_color.name.lower()}."
            "Starting the brain.",
        )

    @Brain.task(process=False, run_on_start=True)
    async def wait_jack_trigger(self) -> None:
        """Wait for the jack to be triggered."""
        while not self.jack_plugged:
            await asyncio.sleep(0.1)
        await self.inputs.wait_for_jack_trigger()
        self.jack_triggered = True
        self.jack_plugged = False

    @Brain.task(process=False, run_on_start=True)
    async def wait_jack_plug(self) -> None:
        """Wait for the jack to be plugged."""
        await self.inputs.wait_for_jack_plugged()
        self.jack_plugged = True

    @Brain.task(process=False, run_on_start=True)
    async def start(self) -> None:
        """Starts the main brain process."""
        self.logger.info(
            "Waiting for mode on IIHM...",
        )
        await self.wait_for_mode()
        self.logger.info(
            "Waiting for team color on IIHM...",
        )
        if CONFIG.LIDAR_DUMMY and CONFIG.ROLLING_BASIS_DUMMY and CONFIG.ACTUATORS_DUMMY:
            await self.wait_for_team()
            self.logger.warning(
                "All subsystems are in dummy mode. The robot will not move.",
            )
        else:
            await self.wait_for_team()

        await self.ws_ui.sender.send(
            WSmsg(sender="server", msg="initializing", data={}),
        )
        self.status = "initializing"

        start_position = OrientedPoint(0, 0, 0)
        enemy_position = OrientedPoint(150, 200, -pi / 2)
        if self.arena.team_color == TeamColor.YELLOW:
            self.logger.info("Starting as YELLOW team.")
            start_position = OrientedPoint(122.5, 21, -pi / 2)
            enemy_position = OrientedPoint(177.5, 21, -pi / 2)
        elif self.arena.team_color == TeamColor.BLUE:
            self.logger.info("Starting as BLUE team.")
            start_position = OrientedPoint(177.5, 21, -pi / 2)
            enemy_position = OrientedPoint(122.5, 21, -pi / 2)

        # 3. Update the arena with the starting position
        self.arena.enemy_zone.update(
            self.arena.team_color,
            start_position,
            enemy_position,
        )
        self.arena.ally_zone.update(
            self.arena.team_color,
            start_position,
            enemy_position,
        )
        self.odemetrie_state = start_position
        self.enemy_odemetrie_state = enemy_position
        self.arena.update(
            ally_position=start_position,
            lidar_scan_polars=np.array([]),
            optimized_update=False,
        )
        self.rolling_basis_odometrie = start_position
        await asyncio.sleep(1)  # Allow time for the arena to update
        await self.run()  # pyright: ignore[reportGeneralTypeIssues] don't touch

    # endregion
