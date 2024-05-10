# External imports
import asyncio
import time
import math
from dataclasses import dataclass

# Import from common
from config_loader import CONFIG
from brain import Brain

from WS_comms import WSmsg, WSclientRouteManager, WServerRouteManager
from geometry import OrientedPoint, Point, distance, Polygon
from arena import MarsArena, Plants_zone
from logger import Logger, LogLevels
from led_strip import LEDStrip
from utils import Utils
from GPIO import PIN

# Import from local path
from brains.acs import AntiCollisionMode, AntiCollisionHandle
from controllers import RollingBasis, Actuators
from sensors import Lidar


@dataclass
class Objective:
    task: str  # objective type ("pickup","drop_to_zone","drop_to_gardener")
    target_index: int  # index of the target
    time_estimate: float = -1.0  # time estimate (won't try if it's too late)
    elevator_after: str = ""

    def __str__(self):
        r = f"{self.task}, at {self.target_index}, estimated time: {self.time_estimate}"
        match self.elevator_after:
            case "top":
                r += ", then raising elevator for next objective"
            case "bottom":
                r += ", then lowering elevator for next objective"
            case "intermediate":
                r += ", then setting elevator to intermediate position"
            case _:
                r += ", then nothing"
        return r


class MainBrain(Brain):
    """
    This brain is the main controller of ROB (robot1).
    """

    # Controllers functions
    from brains.controllers_brain import (
        deploy_god_hand,
        undeploy_god_hand,
        open_god_hand,
        close_god_hand,
        go_best_zone,
        god_hand_demo,
        smart_go_to,
        vertical_god_hand,
        deploy_right_solar_panel,
        undeploy_right_solar_panel,
        deploy_left_solar_panel,
        undeploy_left_solar_panel,
        deploy_team_solar_panel,
        undeploy_team_solar_panel,
        avoid_obstacle,
    )

    # Sensors functions
    from brains.sensors_brain import (
        compute_ennemy_position,
        pol_to_abs_cart,
        get_ennemy_angle,
    )

    # Com functions
    from brains.com_brain import zombie_mode

    def __init__(
        self,
        logger: Logger,
        ws_cmd: WServerRouteManager,
        ws_pami: WServerRouteManager,
        actuators: Actuators,
        rolling_basis: RollingBasis,
        lidar: Lidar,
        logger_arena: Logger,
        jack: PIN,
        team_switch: PIN,
        leds: LEDStrip,
    ) -> None:

        self.anticollision_mode: AntiCollisionMode = AntiCollisionMode(
            CONFIG.ANTICOLLISION_MODE
        )
        self.anticollision_handle: AntiCollisionHandle = AntiCollisionHandle(
            CONFIG.ANTICOLLISION_HANDLE
        )

        # Save this for later use (when re-creating the arena)
        self.logger_arena: Logger

        self.rolling_basis: RollingBasis
        self.jack: PIN
        self.leds: LEDStrip
        self.team_switch: PIN
        self.actuators: Actuators

        # Init the brain
        super().__init__(logger, self)

        # A default, almost dummy starting situation
        self.team = CONFIG.DEFAULT_TEAM
        self.arena: MarsArena = self.generate_up_to_date_arena()
        self.reset_odo_to_start()

        # The regularly updated variable to estimate time left
        self.return_eta: float = -1.0

        self.score_estimate: int = 0

        # Init CONFIG
        self.logger.log(
            f"Mode: {'zombie' if CONFIG.ZOMBIE_MODE else 'game'}", LogLevels.INFO
        )

    """
        Tasks
    """

    @Brain.task(process=False, run_on_start=False)
    async def setup_actuators(self):
        await self.undeploy_god_hand()
        await self.close_god_hand()
        await self.undeploy_right_solar_panel()
        await self.undeploy_left_solar_panel()
        await self.actuators.elevator_intermediate()
        await asyncio.sleep(3)
        await self.vertical_god_hand()

    @Brain.task(process=False, run_on_start=False)
    async def wait_for_trigger(self):
        # Check jack state
        self.leds.set_jack(False)
        while self.jack.digital_read():
            self.show_team_led()
            await asyncio.sleep(0.1)
        self.leds.set_jack(True)

    @Brain.task(process=False, run_on_start=False)
    async def setup_teams(self):
        self.get_team_from_switch()

        start_zone_id = CONFIG.START_INFO_BY_TEAM[self.team]["start_zone_id"]
        self.logger.log(f"Team {self.team}", LogLevels.INFO)

        self.leds.set_team(self.team)

        self.logger.log(f"Game start, zone chosen: {start_zone_id}", LogLevels.INFO)

        # Arena
        self.arena = self.generate_up_to_date_arena()
        self.reset_odo_to_start()

    def reset_odo_to_start(self) -> None:
        self.rolling_basis.set_odo(
            OrientedPoint(
                (
                    CONFIG.START_INFO_BY_TEAM[self.team]["start_x"],
                    CONFIG.START_INFO_BY_TEAM[self.team]["start_y"],
                ),
                CONFIG.START_INFO_BY_TEAM[self.team]["start_theta"],
            )
        )

    def generate_up_to_date_arena(self) -> MarsArena:
        self.get_team_from_switch()
        self.leds.set_team(self.team)
        return MarsArena(
            CONFIG.START_INFO_BY_TEAM[self.team]["start_zone_id"],
            logger=self.logger_arena,
            border_buffer=CONFIG.ARENA_CONFIG["border_buffer"],
            robot_buffer=CONFIG.ARENA_CONFIG["robot_buffer"],
        )

    def get_team_from_switch(self) -> None:
        if self.team_switch.digital_read():
            self.team = CONFIG.TEAM_SWITCH_ON
        else:
            self.team = CONFIG.TEAM_SWITCH_OFF

    @Brain.task(process=False, run_on_start=not CONFIG.ZOMBIE_MODE)
    async def game(self):

        await self.setup_actuators()

        self.logger.log("Waiting for jack trigger...", LogLevels.INFO, self.leds)

        await self.wait_for_trigger()
        # No matter what, kill rolling_basis ans everything else in 90s
        asyncio.create_task(self.time_bomb(90))

        asyncio.create_task(self.setup_teams())

        await asyncio.sleep(0.5)

        # Solar panels stage
        self.logger.log("Starting solar panels stage...", LogLevels.INFO, self.leds)
        await self.solar_panels_stage()
        asyncio.create_task(self.undeploy_team_solar_panel())

        # Virage contre le mur
        await self.drift()

        # Plant Stage
        self.logger.log("Starting plant stage...", LogLevels.INFO, self.leds)
        await self.plant_stage()

        # Custom return to let PAMIs do their thing
        self.logger.log("Going to custom endzone", LogLevels.INFO)
        custom_return_zone = self.arena.drop_zones[2 if self.team == "y" else 5].zone
        await self.smart_go_to(
            Point(
                custom_return_zone.bounds[0],
                custom_return_zone.bounds[3 if self.team == "y" else 1],
            )
        )

        self.logger.log("Going to regular endzone if needed", LogLevels.INFO)
        await self.go_to_endzone()

        # Clean up
        self.logger.log("Game over", LogLevels.INFO, self.leds)
        await self.endgame()
        exit()

    async def time_bomb(self, time_until_forced_endgame):
        await asyncio.sleep(time_until_forced_endgame)
        self.logger.log("Bombing rolling basis", LogLevels.WARNING)
        await self.endgame()

    @Brain.task(process=False, run_on_start=False, timeout=10)
    async def drift(self):
        self.rolling_basis.stop_and_clear_queue()
        await self.rolling_basis.go_to_and_wait(
            Point(-15, 0),
            timeout=5.0,
            **CONFIG.GO_TO_PROFILES["slow_and_precise"],
        )
        distance = 5
        angle = (-1 if self.team == "y" else 1) * math.pi / 6
        if (
            await self.rolling_basis.go_to_and_wait(
                Point(
                    distance * math.cos(angle),
                    distance * math.sin(angle),
                ),
                relative=True,
                **CONFIG.GO_TO_PROFILES["plant_approach"],
                timeout=5,
            )
        ) == 1:
            await self.rolling_basis.go_to_and_wait(
                Point(
                    10,
                    0,
                ),
                relative=True,
                **CONFIG.GO_TO_PROFILES["plant_approach"],
                timeout=2,
            )

    @Brain.task(process=False, run_on_start=False)
    async def go_to_endzone(self):
        already_there, target = self.compute_return_target()

        if not already_there:
            self.rolling_basis.stop_and_clear_queue()
            await self.smart_go_to(
                target,
                **CONFIG.GO_TO_PROFILES["plant_approach"],
            )

    def show_team_led(self):
        self.get_team_from_switch()
        self.leds.set_team(self.team)

    async def undeploy_all(self):
        asyncio.create_task(self.close_god_hand())
        asyncio.create_task(self.vertical_god_hand())
        asyncio.create_task(self.undeploy_left_solar_panel())
        asyncio.create_task(self.undeploy_right_solar_panel())

    async def back_and_forth(self, distance: float = 50.0):
        await self.rolling_basis.go_to_and_wait(
            Point(distance, 0.0),
            forward=True,
            max_speed=160,
            next_position_delay=100,
            action_error_auth=100,
            traj_precision=50,
            correction_trajectory_speed=0,
            acceleration_start_speed=160,
            acceleration_distance=0,
            deceleration_end_speed=160,
            deceleration_distance=0,
            relative=True,
        )

        await asyncio.sleep(2)
        await self.rolling_basis.go_to_and_wait(
            Point(-distance, 0.0),
            forward=True,
            max_speed=160,
            next_position_delay=100,
            action_error_auth=100,
            traj_precision=50,
            correction_trajectory_speed=0,
            acceleration_start_speed=160,
            acceleration_distance=0,
            deceleration_end_speed=160,
            deceleration_distance=0,
            relative=True,
        )

    async def endgame(self):
        # Keep kill_rolling_basis outside a try to be absolutely sure to get to it
        try:
            # Open and deploy god hand, to macimize odds of being in home zone and to let go af any plant still held by accident
            asyncio.create_task(self.deploy_god_hand())
            asyncio.create_task(self.open_god_hand())
            asyncio.create_task(self.actuators.elevator_bottom())
            self.leds.set_score(35)
        except Exception:
            pass
        finally:
            await self.kill_rolling_basis()

    async def god_hand_timer(self, time_to_close: float):
        await asyncio.sleep(time_to_close)
        await self.close_god_hand()

    async def smart_close_god_hand(self, plant_zone: Polygon):
        is_in_plant_zone = False
        while True:
            if plant_zone.intersects(self.rolling_basis.odometrie):
                is_in_plant_zone = True
            # We have passthrough the plant zone
            if is_in_plant_zone and not plant_zone.intersects(
                self.rolling_basis.odometrie
            ):
                await self.close_god_hand()
                break
            await asyncio.sleep(0.1)

    @Logger
    async def go_and_pickup(
        self,
        target_pickup_zone_id: int,
    ) -> None:
        target_pickup_zone = self.arena.pickup_zones[target_pickup_zone_id]

        asyncio.create_task(self.deploy_god_hand())
        asyncio.create_task(self.open_god_hand())

        pickup_target = self.arena.compute_go_to_destination(
            start_point=self.rolling_basis.odometrie,
            zone=target_pickup_zone.zone,
            delta=-15,
        )

        # Passthrough the target plant zone and pickup plants
        god_hand_closing_task = asyncio.create_task(
            self.smart_close_god_hand(target_pickup_zone.zone)
        )

        asyncio.create_task(self.actuators.elevator_bottom())

        await self.smart_go_to(
            position=pickup_target,
            timeout=15,
            **CONFIG.GO_TO_PROFILES["plant_approach"],
        )
        god_hand_closing_task.cancel()

        # Account for removed plants
        target_pickup_zone.take_plants(5)

    @Logger
    async def go_and_drop_to_zone(self, target_drop_zone: Plants_zone) -> None:

        target = self.arena.compute_go_to_destination(
            start_point=self.rolling_basis.odometrie,
            zone=target_drop_zone.zone,
            delta=20,
        )

        await self.smart_go_to(
            position=target,
            timeout=15,
            **CONFIG.GO_TO_PROFILES["plant_approach"],
        )

        # Drop plants
        asyncio.create_task(self.deploy_god_hand())
        await asyncio.sleep(0.1)
        asyncio.create_task(self.open_god_hand())

        # Account for removed plants
        target_drop_zone.drop_plants(5)

        # Step back
        await self.smart_go_to(
            Point(-30, 0),
            timeout=5,
            forward=False,
            **CONFIG.GO_TO_PROFILES["plant_pickup"],
            relative=True,
        )

    @Logger
    async def go_and_drop_to_gardener(self, target_gardener: Plants_zone) -> None:
        # WARNING: only fit for the top gardeners

        approach_target: Point = Point(
            200 - CONFIG.ARENA_CONFIG["robot_buffer_with_god_hand_deployed"],
            target_gardener.zone.centroid.y,
        )

        await self.smart_go_to(
            approach_target, **CONFIG.GO_TO_PROFILES["garden_approach"], timeout=8
        )

        final_target: Point = Point(
            200 - 12.75, self.rolling_basis.odometrie.y
        )  # To make sure to be orthogonal to the wall, use a relative y

        await self.smart_go_to(
            final_target, **CONFIG.GO_TO_PROFILES["slow_and_precise"], timeout=5
        )

        await self.deploy_god_hand()
        await self.actuators.elevator_intermediate()
        await self.open_god_hand()

        # Step back
        await self.smart_go_to(
            Point(-CONFIG.ARENA_CONFIG["robot_buffer"], 0),
            timeout=5,
            forward=False,
            relative=True,
            **CONFIG.GO_TO_PROFILES["plant_pickup"],
        )

        target_gardener.drop_plants(5)

    async def engage_objective(self, objective: Objective):
        match objective.task:
            case "pickup":
                self.logger.log(
                    f"Going to pickup zone {objective.target_index}",
                    LogLevels.INFO,
                    self.leds,
                )

                await self.go_and_pickup(
                    self.arena.pickup_zones[objective.target_index]
                )

                asyncio.create_task(self.undeploy_god_hand())

            case "drop_to_zone":
                self.logger.log(
                    f"Going to drop zone {objective.target_index}",
                    LogLevels.INFO,
                    self.leds,
                )

                await self.go_and_drop_to_zone(
                    self.arena.drop_zones[objective.target_index]
                )
                self.score_estimate += 3

            case "drop_to_gardener":
                self.logger.log(
                    f"Going to gardener {objective.target_index}",
                    LogLevels.INFO,
                    self.leds,
                )

                await self.go_and_drop_to_gardener(
                    self.arena.gardeners[objective.target_index]
                )
                self.score_estimate += 12

            case _:
                raise Exception("Unknown objective type")

        match objective.elevator_after:
            case "top":
                asyncio.create_task(self.actuators.elevator_top())
            case "bottom":
                asyncio.create_task(self.actuators.elevator_bottom())
            case "intermediate":
                asyncio.create_task(self.actuators.elevator_intermediate())
            case _:
                asyncio.create_task(self.undeploy_god_hand())

    @Brain.task(process=False, run_on_start=False, timeout=50)
    async def plant_stage(self):
        start_stage_time = Utils.get_ts()
        in_yellow_team = self.team == "y"

        await self.deploy_god_hand()

        objectives: list[Objective] = [
            Objective("pickup", 0 if in_yellow_team else 4, 8.0),  # First zone
            Objective("drop_to_zone", 2 if in_yellow_team else 5, 10.0),  # First drop
            Objective(
                "pickup", 1 if in_yellow_team else 3, 12.0, elevator_after="top"
            ),  # etc
            Objective(
                "drop_to_gardener",
                2 if in_yellow_team else 5,
                10.0,
                elevator_after="bottom",
            ),
            # Objective("pickup", 2, 8.0),
            # Objective("drop_to_zone", 4 if in_yellow_team else 1, 10.0),
        ]

        for current_objective in objectives:
            self.logger.log(
                f"Considering objective: {current_objective}", LogLevels.INFO
            )

            if (
                Utils.time_since(start_stage_time) + current_objective.time_estimate
                > 60
                and current_objective.time_estimate >= 0
            ):
                self.logger.log(
                    "Not enough time, gotta go fast; leaving plant_stage",
                    LogLevels.INFO,
                )
                # TODO consider what to do if still holding plants
                break

            else:
                self.logger.log("Engaging objective", LogLevels.INFO)
                await self.engage_objective(current_objective)

    @Brain.task(process=False, run_on_start=False, timeout=30)
    async def solar_panels_stage(self) -> None:
        asyncio.create_task(self.control_solar_panels())
        go_to_result = await self.rolling_basis.go_to_and_wait(
            Point(
                CONFIG.START_INFO_BY_TEAM[self.team]["start_x"],
                185 if self.team == "y" else 105,
            ),
            timeout=30.0,
            **CONFIG.GO_TO_PROFILES["slow_and_precise"],
        )

        if go_to_result == 0:
            # Great success!
            self.score_estimate += 30
        else:
            all_solar_panels_y = self.arena.solar_panels_y[:]
            current_y = (
                self.rolling_basis.odometrie.y
            )  # Copied to avoid changing it between operations
            all_solar_panels_y.append(current_y)
            all_solar_panels_y.sort()
            self.score_estimate += all_solar_panels_y.index(current_y) * 5

    @Brain.task(process=False, run_on_start=False, timeout=30)
    async def control_solar_panels(self, solar_panel_timeout: float = 25.0) -> None:

        start_time = Utils.get_ts()
        remaining_solar_panels_y = self.arena.solar_panels_y[:]

        await self.deploy_team_solar_panel(small=True)

        while Utils.time_since(start_time) < solar_panel_timeout:
            await asyncio.sleep(0.05)
            for i, y in enumerate(remaining_solar_panels_y):
                if (
                    0
                    < (1 if self.team == "y" else -1)
                    * (self.rolling_basis.odometrie.y - y)
                    < 15.0
                ):

                    remaining_solar_panels_y.pop(i)
                    await self.deploy_team_solar_panel(
                        small=(len(remaining_solar_panels_y) > 3)
                    )
                    break

    @Brain.task(process=False, run_on_start=not CONFIG.ZOMBIE_MODE, refresh_rate=2)
    async def update_return_eta(self):
        already_there, target = self.compute_return_target()

        if already_there:
            self.return_eta = 0
        else:
            delta = distance(
                Point(self.rolling_basis.odometrie.x, self.rolling_basis.odometrie.y),
                target,
            )
            self.return_eta = 5 + 0.05 * delta

        self.logger.log(f"Estimated ETA: {self.return_eta}", LogLevels.DEBUG)

    def compute_return_target(self) -> tuple[bool, Point]:
        sorted_zones = self.arena.sort_drop_zone(
            self.rolling_basis.odometrie, friendly_only=True, maxi_plants=20
        )

        picked_zone = (
            sorted_zones[0]
            if sorted_zones[0]
            != self.arena.drop_zones[
                CONFIG.START_INFO_BY_TEAM[self.team]["start_zone_id"]
            ]
            else sorted_zones[1]
        )

        already_there = (
            Point(self.rolling_basis.odometrie.x, self.rolling_basis.odometrie.y)
            .buffer(CONFIG.ARENA_CONFIG["robot_buffer"])
            .intersects(picked_zone.zone)
        )

        return already_there, (
            self.arena.compute_go_to_destination(
                self.rolling_basis.odometrie,
                picked_zone.zone,
                20.0,
            )
            if not already_there
            else Point(self.rolling_basis.odometrie.x, self.rolling_basis.odometrie.y)
        )

    @Brain.task(process=False, run_on_start=False)
    async def kill_rolling_basis(self, timeout=-1):
        if timeout > 0:
            await asyncio.sleep(timeout)

        self.logger.log("Killing rolling basis", LogLevels.WARNING)
        self.rolling_basis.stop_and_clear_queue()
        self.rolling_basis.set_pids(0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
        self.rolling_basis = None
