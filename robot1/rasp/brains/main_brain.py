"""Entry point for running the robot's main brain."""

from __future__ import annotations

import ast
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
from boombot_strategy import WinterGameContext
from boombot_strategy.strategies import TowerRushAltStrategy
from controllers.actuators import ActuatorsShow, ActuatorsShowDummy
from controllers.rolling_basis import RollingBasis, RollingBasisDummy
from services import WinterSpatialComputation, WinterSpatialComputationDummy
from geometry import OrientedPoint
from common.stuff import CrateRenderer

if TYPE_CHECKING:
    from arena.winter_arena import WinterArena
    from sensors import Inputs, Lidar, LidarDummy


class MainBrain(Brain):
    """Main brain for the robot."""

    def __init__(
        self,
        logger: Logger,
        # Sensor
        lidar: Lidar | LidarDummy,
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
            lidar (Lidar | LidarDummy): Lidar instance for distance measurements.
            arena (WinterArena): Arena instance for representing the game arena.
            ws_cmd (WServerRouteManager): WebSocket command route manager.
            ws_ui (WServerRouteManager): WebSocket UI route manager.
            inputs (Inputs): Inputs instance for handling sensor data.
        """
        self.lidar: Lidar | LidarDummy = lidar
        self.arena: WinterArena = arena

        # Shared attributes
        self.rolling_basis_odometrie: OrientedPoint = OrientedPoint(0, 0, 0)
        self.score: int = 0

        self.ui_state: dict[str, Any] = {
            "jack_state": True,
            "bau_state": True,
            "odometrie_state": OrientedPoint(0, 0, 0),
            "pamis_states": {
                "superstar": False,
                "groupie_1": False,
                "groupie_2": False,
                "groupie_3": False,
            },
            "score": 0.0,
        }

        self.jack_triggered: bool = False
        self.jack_plugged: bool = False
        self.shared_crates: dict = {}


        super().__init__(logger, self)

        self.ws_cmd: WServerRouteManager = ws_cmd
        self.ws_ui: WServerRouteManager = ws_ui
        self.inputs: Inputs = inputs
        self.score: int




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

        def _crates_to_dict(crates):
            return {
                zone_id: [
                    {"x": c.x, "y": c.y, "color": c.color, "color_id": c.color_id, "zone_id": c.zone_id}
                    for c in lst
                ]
                for zone_id, lst in crates.items()
            }


        # --- Initialization --- #
        if CONFIG.ROLLING_BASIS_DUMMY:
            rolling_basis: RollingBasis | RollingBasisDummy = RollingBasisDummy(
                logger=Logger(identifier="RollingBasisDummy", follow_logger_manager_rules=True),
            )
        else:
            rolling_basis = RollingBasis(
                logger=Logger(identifier="RollingBasis", follow_logger_manager_rules=True),
            )
        rolling_basis.set_odometrie(self.rolling_basis_odometrie)
        rolling_basis.initialize_pids()

        if CONFIG.ACTUATORS_DUMMY:
            actuators: ActuatorsShow | ActuatorsShowDummy = ActuatorsShowDummy(
                logger=Logger(identifier="Actuators", follow_logger_manager_rules=True),
            )
        else:
            actuators = ActuatorsShow(
                logger=Logger(identifier="Actuators", follow_logger_manager_rules=True),
            )

        if CONFIG.SPATIAL_COMPUTATION_DUMMY:
            sc: WinterSpatialComputation | WinterSpatialComputationDummy = WinterSpatialComputationDummy(
                logger=Logger(identifier="SpatialComputationDummy", follow_logger_manager_rules=True),
                arena=self.arena,
            )
        else:
            sc = WinterSpatialComputation(
                logger=Logger(identifier="SpatialComputation", follow_logger_manager_rules=True),
                arena=self.arena,
            )

        self.shared_crates = _crates_to_dict(sc.crates)

        actuators.deplacement_position()

        # --- 2) Wait for jack plug --- #
        while not self.jack_plugged:
            sc.receive_data()
            time.sleep(0.1)

        actuators.block_banner()
        rolling_basis.set_odometrie(self.rolling_basis_odometrie)
        rolling_basis.initialize_pids()

        # --- Wait for trigger --- #
        while not self.jack_triggered:
            sc.receive_data()
            time.sleep(0.1)

        # --- 3) Build the strategy --- #
        strategy = TowerRushAltStrategy(
            WinterGameContext(
                arena=self.arena,
                rolling_basis=rolling_basis,
                actuators=actuators,
                spatial_computation=sc,
                score=self.score,
            ),
        )

        # --- MetaProg is insane (loop) --- #
        sc.receive_data()
        self.shared_crates = _crates_to_dict(sc.crates)

        context = WinterGameContext(
            arena=self.arena,
            rolling_basis=rolling_basis,
            actuators=actuators,
            spatial_computation=sc,
            score=self.score,
        )

        strategy.runner.handle(context)

        self.score = context.score
        self.ui_state["score"] = self.score
        self.rolling_basis_odometrie = rolling_basis.odometrie
        self.ui_state["odometrie_state"] = self.rolling_basis_odometrie



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

        CrateRenderer.plot(ax, self.shared_crates)

        plt.pause(0.01)


    # endregion

    # ====== Main Process ======

    # region ====== Routines ======

    @Brain.task(
        process=False,
        run_on_start=True,
        refresh_rate=1,
        start_loop_marker="# --- MetaProg is insane (loop) --- #",
    )
    async def update_ui(self) -> None:
        """Updates the UI with the current state."""
        previous_state = self.ui_state.copy()

        # --- MetaProg is insane (loop) --- #
        current_state = self.ui_state.copy()
        current_state["jack_state"] = not self.jack_triggered
        if current_state != previous_state:
            previous_state = current_state
            to_send = {
                "jack_state": current_state["jack_state"],
                "bau_state": current_state["bau_state"],
                "odometrie": {
                    "x": current_state["odometrie_state"].x,
                    "y": current_state["odometrie_state"].y,
                    "theta": current_state["odometrie_state"].theta,
                },
                "pamis_states": current_state["pamis_states"],
                "score": current_state["score"],
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
                "All subsystems are in dummy mode. The robot will not move.",
            )
            self.arena.set_team_color(TeamColor.YELLOW)
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
        self.arena.update(
            ally_position=start_position,
            lidar_scan_polars=np.array([]),
            optimized_update=False,
        )
        self.rolling_basis_odometrie = start_position
        await asyncio.sleep(1)  # Allow time for the arena to update
        await self.run()  # pyright: ignore[reportGeneralTypeIssues] don't touch

    # endregion
