"""Entry point for running the robot's main brain."""

from __future__ import annotations

import ast
import asyncio
import time
from math import pi
from typing import TYPE_CHECKING

import matplotlib.pyplot as plt
import numpy as np
from loggerplusplus import Logger
from taskbrain import Brain
from ws_comms import WServerRouteManager, WSmsg

from a_config_loader import CONFIG
from arena.base_arena import TeamColor
from boombot_strategy import ShowGameContext
from boombot_strategy.strategies import TowerRushAltStrategy
from controllers.actuators import ActuatorsShow, ActuatorsShowDummy
from controllers.rolling_basis import RollingBasis, RollingBasisDummy
from geometry import OrientedPoint

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

        # Shared attributes
        self.rolling_basis_odometrie: OrientedPoint = OrientedPoint(0, 0, 0)
        self.score: int = 0

        self.jack_triggered: bool = False
        self.jack_plugged: bool = False
        super().__init__(logger, self)

        self.ws_cmd: WServerRouteManager = ws_cmd
        self.ws_ui: WServerRouteManager = ws_ui
        self.inputs: Inputs = inputs
        self.score: int

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
    async def run(self) -> None:
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

        strategy = TowerRushAltStrategy(
            ShowGameContext(
                arena=self.arena,
                rolling_basis=rolling_basis,
                actuators=actuators,
                score=self.score,
            ),
        )

        # from strategy.tools import visualize_task_graph
        # visualize_task_graph(strategy.runner.active[0])

        # --- MetaProg is insane (loop) --- #
        context = ShowGameContext(
            arena=self.arena,
            rolling_basis=rolling_basis,
            actuators=actuators,
            score=self.score,
        )
        strategy.runner.handle(context)

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
        start_loop_marker="# --- MetaProg is insane (loop) --- #",
    )
    async def update_ui(self) -> None:
        """Updates the UI with the current state."""

        # --- MetaProg is insane (loop) --- #
        current_snapshot = {
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

    @Brain.task(process=False, run_on_start=True, refresh_rate=0.5)
    async def receive_ui_data(self) -> None:
        """Executes requests received by the server.

        Use Postman to send request to the server
        Use eval and await eval to run the code you want. Code must be sent as a string
        """
        ui = await self.ws_ui.receiver.get()

        if ui != WSmsg():
            self.logger.info(f"UI instruction {ui.msg} received: {ui.data}")
            if ui.msg == "eval":
                instructions = []
                if isinstance(ui.data, str):
                    instructions.append(ui.data)
                elif isinstance(ui.data, list):
                    instructions = ui.data

                for instruction in instructions:
                    if instruction.startswith("await "):
                        await ast.literal_eval(instruction.removeprefix("await "))
                    else:
                        ast.literal_eval(instruction)
            elif ui.msg == "team change":
                if ui.data["team"] in {"yellow", "blue"}:
                    self.arena.set_team_color(TeamColor[ui.data["team"].upper()])
                    self.logger.info(f"Team color set to {ui.data['team']}")
                else:
                    self.logger.warning(f"Invalid team color: {ui.data}")
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
        if CONFIG.LIDAR_DUMMY and CONFIG.ROLLING_BASIS_DUMMY and CONFIG.ACTUATORS_DUMMY:
            self.logger.warning(
                "All subsystems are in dummy mode. The robot will not move.\nWaiting for team color on IIHM...",
            )
            await self.wait_for_team()
        else:
            await self.wait_for_team()

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
