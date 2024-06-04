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
from utils import LidarMode, AntiCollisionHandle
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
    
    def enough_time(self,start_time)->bool:
    
        if (
            Utils.get_ts()+self.time_estimate-start_time>70
            and self.time_estimate >= 0
        ):
            self.logger.log(
                "Not enough time, gotta go fast; leaving plant_stage",
                LogLevels.INFO,
            )
            return False
        return True

    def is_intresting(self)->bool:
        if(self.task=="pickup") and self.arena.pickup_zones[self.target_index].visited and self.arena.pickup_zones[self.target_index].nb_plant < CONFIG.ARENA_CONFIG["limit_plant_pickup"]:
            self.logger.log(f"pickup zone {self.target_index} not interesting anymore", LogLevels.INFO)
            return False
        return True

    def evaluate(self,start_time)->bool:
        if not self.enough_time(start_time):
            return False
        if not self.is_intresting():
            return False
        return True


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
        handle_acs,
        elevator_bottom,
        elevator_intermediate,
        elevator_top
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

        self.anticollision_mode: LidarMode = LidarMode(
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
        self.leds.set_score(self.score_estimate)
        
        self.start_time = -1

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
        await self.elevator_intermediate()
        await asyncio.sleep(3)
        await self.vertical_god_hand()

    @Brain.task(process=False, run_on_start=False)
    async def wait_for_trigger(self):
        """
        Waits for a trigger signal from the jack.
        
        This function continuously checks the state of the jack and waits until it is triggered.
        While waiting, it shows the team LED and sleeps for 0.1 seconds between each check.
        Once triggered, it sets the jack LED to True.
        """
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
        """
        Generates an up-to-date MarsArena object based on the current team.

        Returns:
            MarsArena: The generated MarsArena object.
        """
        self.get_team_from_switch()
        self.leds.set_team(self.team)
        return MarsArena(
            CONFIG.START_INFO_BY_TEAM[self.team]["start_zone_id"],
            logger=self.logger_arena,
            border_buffer=CONFIG.ARENA_CONFIG["border_buffer"],
            robot_buffer=CONFIG.ARENA_CONFIG["robot_buffer"],
        )

    def get_team_from_switch(self) -> None:
        """
        Reads the team switch and sets the team attribute accordingly.

        If the team switch is in the ON position, the team attribute is set to CONFIG.TEAM_SWITCH_ON.
        If the team switch is in the OFF position, the team attribute is set to CONFIG.TEAM_SWITCH_OFF.
        """
        if self.team_switch.digital_read():
            self.team = CONFIG.TEAM_SWITCH_ON
        else:
            self.team = CONFIG.TEAM_SWITCH_OFF

    @Brain.task(process=False, run_on_start=not CONFIG.ZOMBIE_MODE)
    async def game(self):
        self.start_time = Utils.get_ts()
        await self.setup_actuators()

        self.logger.log("Waiting for jack trigger...", LogLevels.INFO, self.leds)

        await self.wait_for_trigger()
        # No matter what, kill rolling_basis ans everything else in 90s
        asyncio.create_task(self.time_bomb(90))

        asyncio.create_task(self.setup_teams())

        await asyncio.sleep(0.5)

        # Solar panels stage
        solar_panel_control = asyncio.create_task(self.control_solar_panels())
        self.logger.log("Starting solar panels stage...", LogLevels.INFO, self.leds)
        await self.solar_panels_stage()
        solar_panel_control.cancel()
        await self.undeploy_team_solar_panel()

        # Virage contre le mur
        await self.drift()

        # Plant Stage
        self.logger.log(
            "Starting plant stage and solar panels control...",
            LogLevels.INFO,
            self.leds,
        )

        await self.plant_stage()

        self.logger.log("Going to regular endzone if needed", LogLevels.INFO)
        await self.go_to_endzone()

        # Clean up
        self.logger.log("Game over", LogLevels.INFO, self.leds)
        await self.endgame()
        exit()

    async def time_bomb(self, time_until_forced_endgame):
        """
        Sleeps for the specified time and then triggers the endgame.

        Args:
            time_until_forced_endgame (float): The time in seconds until the endgame is triggered.

        Returns:
            None
        """
        await asyncio.sleep(time_until_forced_endgame)
        self.logger.log("Bombing rolling basis", LogLevels.WARNING)
        await self.endgame()

    @Brain.task(process=False, run_on_start=False, timeout=10)
    async def drift(self):
        """
        Drifts the robot by moving it to a specified point and then moving it relative to that point.

        Args:
            self: The instance of the class.

        Returns:
            None
        """
        self.rolling_basis.stop_and_clear_queue()
        await self.rolling_basis.go_to_and_wait(
            Point(-15, 0),
            timeout=2.5,
            **CONFIG.GO_TO_PROFILES["slow_and_precise"],
            forward=False,
            relative=True,
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
                timeout=2,
            )
        ) == 1:
            await self.rolling_basis.go_to_and_wait(
                Point(
                    10,
                    0,
                ),
                relative=True,
                **CONFIG.GO_TO_PROFILES["plant_approach"],
                timeout=1.5,
            )

    @Brain.task(process=False, run_on_start=False)
    async def go_to_endzone(self):
        """
        Go to the endzone.

        This method calculates the target location and moves the robot to the endzone.
        If the robot is already in the endzone, it does nothing.
        If the robot is not in the endzone, it checks if the target location is within the custom return zone.
        If it is, the robot moves to the custom return zone without blocking pami.
        If it is not, the robot stops and clears the queue, then moves to the target location using the plant_approach profile.

        Args:
            self: The instance of the class.

        Returns:
            None
        """
        already_there, target = self.compute_return_target()

        if not already_there:
            if self.arena.drop_zones[2 if self.team == "y" else 5].zone.contains(
                target
            ):
                # Custom return to let PAMIs do their thing
                self.logger.log("Going to custom endzone", LogLevels.INFO)
                custom_return_zone = self.arena.drop_zones[
                    2 if self.team == "y" else 5
                ].zone
                await self.smart_go_to(
                    Point(
                        custom_return_zone.bounds[0],
                        custom_return_zone.bounds[3 if self.team == "y" else 1],
                    )
                )
            else:  # Regular operation
                self.rolling_basis.stop_and_clear_queue()
                await self.smart_go_to(
                    target,
                    **CONFIG.GO_TO_PROFILES["plant_approach"],
                )

    def show_team_led(self):
        self.get_team_from_switch()
        self.leds.set_team(self.team)
        
    def show_team_lcd(self):
        self.get_team_from_switch()
        self.actuators.lcd_print(f"Team : {self.team}")

    async def undeploy_all(self):
        asyncio.create_task(self.close_god_hand())
        asyncio.create_task(self.vertical_god_hand())
        asyncio.create_task(self.undeploy_left_solar_panel())
        asyncio.create_task(self.undeploy_right_solar_panel())

    async def back_and_forth(self, distance: float = 50.0):
        """
        Moves the robot back and forth in a straight line.

        Args:
            distance (float): The distance to travel in millimeters. Default is 50.0.
            
        Note: useful to move plants' pot to not hinder the robot's movement

        Returns:
            None
        """
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
            asyncio.create_task(self.elevator_bottom())
            if self.compute_return_target()[0] == True:
                self.score_estimate += (
                    10  # For going to a safe zone that isn't the starting one
                )
                self.leds.set_score(self.score_estimate)
                self.logger.log(
                    "Scored 10 for going to a safe zone that isn't the starting one",
                    LogLevels.DEBUG,
                )
            elif (
                self.arena.drop_zones[0 if self.team == "y" else 3].zone.contains(
                    self.rolling_basis.odometrie
                )
                and self.score_estimate > 0
            ):
                self.score_estimate += 5  # For going to a safe zone but the wrong one
                self.logger.log(
                    "Scored 5 for going to the starting zone (after leaving)",
                    LogLevels.DEBUG,
                )
                self.leds.set_score(self.score_estimate)
            self.score_estimate += 5  # Pami
            self.leds.set_score(self.score_estimate)
            self.logger.log("Scored 5 from PAMI (hopefully)", LogLevels.DEBUG)

            self.logger.log(
                f"Displaying total score: {self.score_estimate}", LogLevels.DEBUG
            )
            self.leds.set_score(self.score_estimate)
            self.actuators.lcd_print(f"Score: {self.score_estimate}")
        except Exception:
            pass
        finally:
            await self.kill_rolling_basis()

    async def god_hand_timer(self, time_to_close: float):
        await asyncio.sleep(time_to_close)
        await self.close_god_hand()

    async def smart_close_god_hand(self, plant_zone: Polygon):
        """
        Closes the god hand when the robot is inside the specified plant zone.

        Args:
            plant_zone (Polygon): The plant zone represented as a Polygon object.

        Returns:
            None
        """
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
        target_pickup_zone: Plants_zone,
    ) -> None:

        asyncio.create_task(self.deploy_god_hand())
        asyncio.create_task(self.open_god_hand())

        pickup_target = self.arena.compute_go_to_destination(
            start_point=self.rolling_basis.odometrie,
            zone=target_pickup_zone.zone,
            delta=-20,
        )

        # Passthrough the target plant zone and pickup plants
        god_hand_closing_task = asyncio.create_task(
            self.smart_close_god_hand(target_pickup_zone.zone)
        )

        asyncio.create_task(self.elevator_bottom())

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

        r = await self.smart_go_to(
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

        if r == 0:
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

        if (
            await self.smart_go_to(
                approach_target, **CONFIG.GO_TO_PROFILES["garden_approach"], timeout=10
            )
            == 0
        ):

            final_target: Point = Point(
                200 - 10, self.rolling_basis.odometrie.y
            )  # To make sure to be orthogonal to the wall, use a relative y

            if await self.smart_go_to(
                final_target,
                **CONFIG.GO_TO_PROFILES["slow_and_precise"],
                timeout=4,
            ) in [0, 1]:

                await self.deploy_god_hand()
                await self.elevator_intermediate()
                await self.open_god_hand()

                target_gardener.drop_plants(5)

            else:
                await self.deploy_god_hand()
                await self.elevator_bottom()
                await self.open_god_hand()

            # Step back
            await self.smart_go_to(
                Point(-CONFIG.ARENA_CONFIG["robot_buffer"], 0),
                timeout=5,
                forward=False,
                relative=True,
                **CONFIG.GO_TO_PROFILES["plant_pickup"],
            )

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

                if not (objective.elevator_after in ["top", "intermediate"]):
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
                self.leds.set_score(self.score_estimate)
                self.logger.log(
                    f"Scored 3 for dropping to drop_zone {objective.target_index}",
                    LogLevels.DEBUG,
                )

            case "drop_to_gardener":
                self.logger.log(
                    f"Going to gardener {objective.target_index}",
                    LogLevels.INFO,
                    self.leds,
                )

                await self.go_and_drop_to_gardener(
                    self.arena.gardeners[objective.target_index]
                )
                self.score_estimate += 8
                self.leds.set_score(self.score_estimate)
                self.logger.log(
                    f"Scored 8 for dropping to gardener {objective.target_index}",
                    LogLevels.DEBUG,
                )

            case _:
                raise Exception("Unknown objective type")

        match objective.elevator_after:
            case "top":
                asyncio.create_task(self.elevator_top())
            case "bottom":
                asyncio.create_task(self.elevator_bottom())
            case "intermediate":
                asyncio.create_task(self.elevator_intermediate())
            case _:
                asyncio.create_task(self.undeploy_god_hand())
                
    

    @Brain.task(process=False, run_on_start=False, timeout=60)
    async def plant_stage(self):
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
                12.0,
                elevator_after="bottom",
            ),
            Objective("pickup", 3 if in_yellow_team else 1, 8.0),
            Objective("drop_to_zone", 4 if in_yellow_team else 1, 3.0),
            # Objective("pickup", 2, 8.0),
            # Objective("drop_to_zone", 4 if in_yellow_team else 1, 10.0),
        ]
        previous_anticollision_handle = self.anticollision_handle
        if self.trigger_acs : self.anticollision_handle = AntiCollisionHandle.DO_NOTHING
        first = True
        for current_objective in objectives:
            self.logger.log(
                f"Considering objective: {current_objective}, estimated finishing time: {Utils.get_ts()-self.start_time + current_objective.time_estimate}",
                LogLevels.INFO,
            )
            if current_objective.evaluate(self.start_time):
                self.logger.log("Engaging objective", LogLevels.INFO)
                await self.engage_objective(current_objective)
            if first:
                self.anticollision_handle = previous_anticollision_handle
            else:
                break
            

    @Brain.task(process=False, run_on_start=False, timeout=21)
    async def solar_panels_stage(self) -> None:
        target_y = (
            (max(self.arena.solar_panels_y) + 7.0)
            if self.team == "y"
            else (min(self.arena.solar_panels_y) - 7.0)
        )

        go_to_result = await self.smart_go_to(
            Point(CONFIG.START_INFO_BY_TEAM[self.team]["start_x"], target_y),
            timeout=20.0,
            **CONFIG.GO_TO_PROFILES["slow_and_precise"],
        )

        if go_to_result.value in [0, 3]:
            self.score_estimate += 1
            self.leds.set_score(self.score_estimate)
            self.logger.log(f"Scored 1 for leaving starting zone", LogLevels.DEBUG)
            
        self.anticollision_handle = AntiCollisionHandle.DO_NOTHING
        


    @Brain.task(process=False, run_on_start=False, timeout=30)
    async def control_solar_panels(
        self,
    ) -> None:

        self.logger.log("Started controlling solar panels", LogLevels.INFO)
        remaining_solar_panels_y = self.arena.solar_panels_y[:]

        await self.deploy_team_solar_panel(small=True)
        while len(remaining_solar_panels_y) > 0:
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
                    self.score_estimate += 5
                    self.leds.set_score(self.score_estimate)
                    self.logger.log(
                        f"New solar panel done, total score: {self.score_estimate}",
                        LogLevels.DEBUG,
                    )
                    break

    @Brain.task(process=False, run_on_start=not CONFIG.ZOMBIE_MODE, refresh_rate=2)
    async def update_return_eta(self):
        already_safe, target = self.compute_return_target()

        if already_safe:
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
