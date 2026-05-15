"""Entry point for running the robot's main brain."""

from __future__ import annotations

import asyncio
import time
import traceback
from contextlib import suppress
from math import pi
from typing import TYPE_CHECKING, Any

import matplotlib.pyplot as plt
import numpy as np
from loggerplusplus import Logger
from taskbrain import Brain
from ws_comms import WServerRouteManager, WSmsg

from a_config_loader import CONFIG
from arena.base_arena import TeamColor
from boombot_strategy import WinterGameContext
from boombot_strategy.strategies import GoBackstageStrategy
from boombot_strategy.sub_graphs import (
    get_banner_deployment_subgraph,
    get_construct_one_floor_subgraph,
    get_construct_subgraph,
    get_pickup_subgraph,
    get_push_one_floor_to_wall_subgraph,
)
from boombot_strategy.tasks.navigation_tasks import (
    GoToOrientedPoint,
    RelativeBackward,
    RelativeForward,
    RelativeRotation,
    SetOdometrie,
)
from controllers.actuators import ActuatorsShow, ActuatorsShowDummy
from controllers.rolling_basis import RollingBasis, RollingBasisDummy
from geometry import OrientedPoint
from log_manager import LogLogger
from sensors import LidarError
from strategy.core import GraphRunner
from strategy.core.task_nodes import BaseTaskNode

NORMAL_MATCH_TIMEOUT_S = 100.0
ZERO_PID = {"kp": 0.0, "ki": 0.0, "kd": 0.0}


def set_zero_pids(rolling_basis: RollingBasis | RollingBasisDummy) -> None:
    """Disable all rolling basis PID controllers."""
    rolling_basis.set_pids(
        linear_position_pid=ZERO_PID,
        angular_position_pid=ZERO_PID,
        left_wheel_position_pid=ZERO_PID,
        right_wheel_position_pid=ZERO_PID,
    )


def get_relative_rotation_sign(team_color: TeamColor) -> float:
    """Return the team-dependent sign for relative rotations.

    Positive relative rotations are calibrated for the blue team.
    """
    if team_color == TeamColor.BLUE:
        return -1.0
    return 1.0


if TYPE_CHECKING:
    from arena.winter_arena import WinterArena
    from sensors import Inputs, Lidar, LidarDummy, UltrasonicDistanceSensor
    from strategy.core.tasks import BaseTask


class MainBrain(Brain):
    """Main brain for the robot."""

    def __init__(
        self,
        logger: Logger,
        # Sensor
        lidar: Lidar | LidarDummy | UltrasonicDistanceSensor,
        # Environment
        arena: WinterArena,
        # WS routes
        ws_cmd: WServerRouteManager,
        ws_ui: WServerRouteManager,
        # Inputs
        inputs: Inputs,
    ) -> None:
        """Initializes the MainBrain with the necessary components.

        Args:
            logger (Logger): Logger instance for logging messages.
            lidar (Lidar | LidarDummy | UltrasonicDistanceSensor):
                Distance sensor instance for obstacle measurements.
            arena (ShowArena): Arena instance for representing the game arena.
            ws_cmd (WServerRouteManager): WebSocket command route manager.
            ws_ui (WServerRouteManager): WebSocket UI route manager.
            inputs (Inputs): Inputs instance for handling sensor data.
        """
        self.lidar: Lidar | LidarDummy | UltrasonicDistanceSensor = lidar
        self.arena: WinterArena = arena
        self.mode: str | None = None
        self.status: str = "launching"

        # Shared attributes
        self.rolling_basis_odometrie: OrientedPoint = OrientedPoint(0, 0, 0)
        self.task_name: str = ""
        self.task_todo: list[BaseTask[WinterGameContext]] = []
        self.task_type: str = ""
        self.task_data: dict[str, Any] = {}
        self.should_update_task: bool = False
        self.score: int = 0

        self.should_update_pid: bool = False
        self.pid_type: str = ""
        self.pid_kp: float = 0.0
        self.pid_ki: float = 0.0
        self.pid_kd: float = 0.0
        self.should_export_debug_report: bool = False
        self.should_send_direct_pwm: bool = False
        self.direct_pwm_left: int = 0
        self.direct_pwm_right: int = 0
        self.direct_pwm_duration_ms: int = 500
        self.pid_debug_live: dict[str, Any] = {
            "enabled": 0,
            "time_s": 0.0,
            "last_event": "init",
            "sample_count": 0,
            "target_linear_cm_s": None,
            "target_angular_rad_s": None,
            "actual_linear_cm_s": None,
            "actual_angular_rad_s": None,
            "linear_error_cm_s": None,
            "angular_error_rad_s": None,
            "odom_x_cm": None,
            "odom_y_cm": None,
            "odom_theta_rad": None,
            "pids": {},
        }

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
        strategy: GoBackstageStrategy | None = None
        action_holder: list[GraphRunner | None] = [None]
        init_stage = "rolling basis setup"
        try:
            # --- 1) Initialize subsystems --- #
            if CONFIG.ROLLING_BASIS_DUMMY:
                rolling_basis: RollingBasis | RollingBasisDummy = RollingBasisDummy(
                    logger=LogLogger(
                        identifier="RollingBasisDummy",
                        follow_logger_manager_rules=True,
                    ),
                    enable_realtime_simulation=True,
                    enable_debug_report=True,
                )
            else:
                rolling_basis = RollingBasis(
                    logger=LogLogger(
                        identifier="RollingBasis",
                        follow_logger_manager_rules=True,
                    ),
                )

            init_stage = "rolling basis PID disable before jack plug"
            rolling_basis.set_odometrie(self.rolling_basis_odometrie)
            set_zero_pids(rolling_basis)

            init_stage = "actuators setup"
            if CONFIG.ACTUATORS_DUMMY:
                actuators: ActuatorsShow | ActuatorsShowDummy = ActuatorsShowDummy(
                    logger=LogLogger(
                        identifier="Actuators",
                        follow_logger_manager_rules=True,
                    ),
                )
            else:
                actuators = ActuatorsShow(
                    logger=LogLogger(
                        identifier="Actuators",
                        follow_logger_manager_rules=True,
                    ),
                )

            # --- 2) Wait for jack plug ● Deploy banner block ● Wait for trigger --- #
            init_stage = "jack plug wait"
            if (
                not CONFIG.LIDAR_DUMMY
                or not CONFIG.ROLLING_BASIS_DUMMY
                or not CONFIG.ACTUATORS_DUMMY
            ):
                while not self.jack_plugged:  # wait until cable is plugged
                    time.sleep(0.1)
            else:
                time.sleep(2)

            init_stage = "rolling basis reinitialization"
            rolling_basis.set_odometrie(self.rolling_basis_odometrie)
            rolling_basis.initialize_pids()

            init_stage = "jack trigger wait"
            while not self.jack_triggered:  # wait for the trigger event
                time.sleep(0.1)

            match_start_time = time.monotonic()
            normal_match_timeout_sent = False

            # --- 3) Build the strategy --- #
            init_stage = "strategy creation"
            if self.mode == "iihm":
                self.logger.info("IIHM mode: Waiting for first task...")
            else:
                strategy = GoBackstageStrategy(
                    WinterGameContext(
                        arena=self.arena,
                        rolling_basis=rolling_basis,
                        actuators=actuators,
                        point=self.score,
                    ),
                    rotation_sign=get_relative_rotation_sign(self.arena.team_color),
                )

            self.should_send_start = True
            self.status = "starting"
        except Exception:
            self.logger.error(
                f"[run] Initialization failed during {init_stage}: "
                f"{traceback.format_exc()}",
            )
            raise

        # from strategy.tools import visualize_task_graph
        # visualize_task_graph(strategy.runner.active[0])

        # --- MetaProg is insane (loop) --- #
        normal_match_timed_out = (
            self.mode == "normal"
            and time.monotonic() - match_start_time >= NORMAL_MATCH_TIMEOUT_S
        )

        context = WinterGameContext(
            arena=self.arena,
            rolling_basis=rolling_basis,
            actuators=actuators,
            point=self.score,
        )

        if normal_match_timed_out:
            action_holder[0] = None
            if not normal_match_timeout_sent:
                self.logger.info(
                    "[BRAIN:Match] Normal mode timeout reached; stopping robot.",
                )
                rolling_basis.set_target_position(rolling_basis.odometrie)
                rolling_basis.set_motors_pwm(
                    left_pwm=0,
                    right_pwm=0,
                    duration_ms=100,
                )
                normal_match_timeout_sent = True
        elif strategy:
            strategy.runner.handle(context)
        else:
            if self.should_update_task:
                zone: int | None = self.arena.get_current_zone_id()
                if self.task_type == "navigation":
                    action_holder[0] = GraphRunner(
                        logger=LogLogger(
                            identifier="IIHMRunner",
                            follow_logger_manager_rules=True,
                        ),
                        start=BaseTaskNode(
                            name=f"[Debug] {self.task_name}",
                            tasks=self.task_todo,
                        ),
                    )
                elif self.task_type == "relative_forward":
                    distance = float(self.task_data.get("distance", 0.0))
                    action_holder[0] = GraphRunner(
                        logger=LogLogger(
                            identifier="IIHMRunner",
                            follow_logger_manager_rules=True,
                        ),
                        start=BaseTaskNode(
                            name=f"[Debug] Relative forward {distance} cm",
                            tasks=[RelativeForward(distance)],
                        ),
                    )
                elif self.task_type == "relative_backward":
                    distance = float(self.task_data.get("distance", 0.0))
                    action_holder[0] = GraphRunner(
                        logger=LogLogger(
                            identifier="IIHMRunner",
                            follow_logger_manager_rules=True,
                        ),
                        start=BaseTaskNode(
                            name=f"[Debug] Relative backward {distance} cm",
                            tasks=[RelativeBackward(distance)],
                        ),
                    )
                elif self.task_type == "relative_turn":
                    angle = float(self.task_data.get("angle", 0.0))
                    action_holder[0] = GraphRunner(
                        logger=LogLogger(
                            identifier="IIHMRunner",
                            follow_logger_manager_rules=True,
                        ),
                        start=BaseTaskNode(
                            name=f"[Debug] Relative turn {angle} rad",
                            tasks=[RelativeRotation(angle)],
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

        if self.should_send_direct_pwm and not normal_match_timed_out:
            action_holder[0] = None
            rolling_basis.set_motors_pwm(
                left_pwm=self.direct_pwm_left,
                right_pwm=self.direct_pwm_right,
                duration_ms=self.direct_pwm_duration_ms,
            )
            self.should_send_direct_pwm = False
        elif self.should_send_direct_pwm and normal_match_timed_out:
            self.logger.warning(
                "[BRAIN:Match] Ignoring direct PWM request after normal mode timeout.",
            )
            self.should_send_direct_pwm = False

        if self.should_update_pid:
            if self.pid_type in {"linear", "linear_position"}:
                rolling_basis.set_linear_position_pid(
                    kp=self.pid_kp,
                    ki=self.pid_ki,
                    kd=self.pid_kd,
                )
            elif self.pid_type in {"angular", "angular_position"}:
                rolling_basis.set_angular_position_pid(
                    kp=self.pid_kp,
                    ki=self.pid_ki,
                    kd=self.pid_kd,
                )
            elif self.pid_type in {"left_wheel", "left_wheel_position"}:
                rolling_basis.set_left_wheel_position_pid(
                    kp=self.pid_kp,
                    ki=self.pid_ki,
                    kd=self.pid_kd,
                )
            elif self.pid_type in {"right_wheel", "right_wheel_position"}:
                rolling_basis.set_right_wheel_position_pid(
                    kp=self.pid_kp,
                    ki=self.pid_ki,
                    kd=self.pid_kd,
                )
            self.should_update_pid = False

        # Update shared state from the context
        self.score = context.point
        self.odemetrie_state = context.arena.ally_zone.point
        self.enemy_odemetrie_state = context.arena.enemy_zone.point
        self.rolling_basis_odometrie = rolling_basis.odometrie
        self.pid_debug_live = rolling_basis.get_debug_snapshot()

        if self.should_export_debug_report:
            rolling_basis.export_debug_report(reason="shutdown_request")
            self.should_export_debug_report = False

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
        refresh_rate=0.1,
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
            "pid_debug": self.pid_debug_live,
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
                "pid_debug": current_snapshot["pid_debug"],
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
            self.logger.info(f"[WS:UI] Instruction {ui.msg} | data: {ui.data}")
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
                    "relative_forward",
                    "relative_backward",
                    "relative_turn",
                }:
                    self.task_type = str(ui.data["type"])
                    self.task_data = dict(ui.data.get("data", {}))
                    self.task_name = self.task_type
                    self.should_update_task = True
                    self.logger.info(
                        f"Set task to {self.task_type}: {self.task_data}",
                    )
                elif ui.data["type"] == "direct_pwm":
                    self.direct_pwm_left = int(ui.data["data"].get("left_pwm", 0))
                    self.direct_pwm_right = int(ui.data["data"].get("right_pwm", 0))
                    self.direct_pwm_duration_ms = int(
                        ui.data["data"].get("duration_ms", 500),
                    )
                    self.should_send_direct_pwm = True
                    self.logger.info(
                        "Direct PWM request: "
                        f"left={self.direct_pwm_left}, "
                        f"right={self.direct_pwm_right}, "
                        f"duration={self.direct_pwm_duration_ms}ms",
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
                self.logger.warning(
                    f"[WS:UI] Command not implemented: {ui.msg} / {ui.data}",
                )

    @Brain.task(process=False, run_on_start=True, refresh_rate=0.01)
    async def update_arena(self) -> None:
        """Updates the arena with the current position of the robot."""
        lidar_scan_polars = np.empty((0, 2), dtype=np.float32)
        if self.lidar.is_connected():
            with suppress(LidarError):
                lidar_scan_polars = self.lidar.scan_to_polars()

        self.arena.update(
            ally_position=self.rolling_basis_odometrie,
            lidar_scan_polars=lidar_scan_polars,
            optimized_update=True,
            # _enemy_position=self.position_generator(),
        )

    # @Brain.task(process=False, run_on_start=False, refresh_rate=0.1)
    # async def print_odo(self) -> None:
    #     self.logger.info(
    #         f"[CTRL:RB] Rolling basis odometrie: {self.rolling_basis_odometrie}"
    #     )

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
            f"[BRAIN:Init] Team color set to {self.arena.team_color.name.lower()}. "
            "Starting brain.",
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
        if CONFIG.LIDAR_DUMMY and CONFIG.ROLLING_BASIS_DUMMY:
            await self.wait_for_team()
            self.logger.warning(
                "[BRAIN:Init] All subsystems in DUMMY mode.",
            )
            self.jack_plugged = True
            self.jack_triggered = True
            self.logger.info(
                "[BRAIN:Init] Auto-triggering jack in full dummy mode.",
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
            self.logger.info("[BRAIN:Init] Starting as YELLOW team")
            start_position = OrientedPoint(30, 180, -pi / 2)
            enemy_position = OrientedPoint(270, 180, -pi / 2)
        elif self.arena.team_color == TeamColor.BLUE:
            self.logger.info("[BRAIN:Init] Starting as BLUE team")
            start_position = OrientedPoint(270, 180, -pi / 2)
            enemy_position = OrientedPoint(30, 180, -pi / 2)
        else:
            start_position = OrientedPoint(0, 0, 0)
            enemy_position = OrientedPoint(150, 200, -pi / 2)

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
