# External imports
import asyncio
import time

# Import from common
from config_loader import CONFIG

from brain import Brain

from geometry import OrientedPoint, Point
from arena import MarsArena, Plants_zone
from logger import Logger, LogLevels
from utils import LidarMode, AntiCollisionHandle

# Import from local path
from controllers import RollingBasis, Actuators

from utils import GoToResult


@Logger
async def deploy_right_solar_panel(
    self, small: bool = False, override_angle: float | None = None
):
    await asyncio.sleep(CONFIG.MINIMUM_DELAY)
    servo = CONFIG.SOLAR_PANEL_RIGHT
    await self.actuators.update_servo(
        pin=servo["pin"],
        angle=(
            (servo["deploy_angle"] if not small else servo["small_deploy_angle"])
            if override_angle is None
            else override_angle
        ),
        detach=True,
        detach_delay=CONFIG.SOLAR_PANEL_DETACH_DELAY,
    )


@Logger
async def undeploy_right_solar_panel(self, override_angle: float | None = None):
    await asyncio.sleep(CONFIG.MINIMUM_DELAY)
    servo = CONFIG.SOLAR_PANEL_RIGHT
    await self.actuators.update_servo(
        pin=servo["pin"],
        angle=servo["undeploy_angle"] if override_angle is None else override_angle,
        detach=True,
        detach_delay=CONFIG.SOLAR_PANEL_DETACH_DELAY,
    )


@Logger
async def deploy_left_solar_panel(
    self, small: bool = False, override_angle: float | None = None
):
    await asyncio.sleep(CONFIG.MINIMUM_DELAY)
    servo = CONFIG.SOLAR_PANEL_LEFT
    await self.actuators.update_servo(
        pin=servo["pin"],
        angle=(
            (servo["deploy_angle"] if not small else servo["small_deploy_angle"])
            if override_angle is None
            else override_angle
        ),
        detach=True,
        detach_delay=CONFIG.SOLAR_PANEL_DETACH_DELAY,
    )


@Logger
async def undeploy_left_solar_panel(self, override_angle: float | None = None):
    await asyncio.sleep(CONFIG.MINIMUM_DELAY)
    servo = CONFIG.SOLAR_PANEL_LEFT
    await self.actuators.update_servo(
        pin=servo["pin"],
        angle=servo["undeploy_angle"] if override_angle is None else override_angle,
        detach=True,
        detach_delay=CONFIG.SOLAR_PANEL_DETACH_DELAY,
    )


@Logger
async def deploy_team_solar_panel(
    self, small: bool = False, override_angle: float | None = None
):
    if self.team == "y":
        await self.deploy_left_solar_panel(small, override_angle)
    else:
        await self.deploy_right_solar_panel(small, override_angle)


@Logger
async def undeploy_team_solar_panel(self, override_angle: float | None = None):
    if self.team == "y":
        await self.undeploy_left_solar_panel(override_angle)
    else:
        await self.undeploy_right_solar_panel(override_angle)


@Logger
async def deploy_god_hand(self):
    await asyncio.sleep(CONFIG.MINIMUM_DELAY)
    servo = CONFIG.FRONT_GOD_HAND["deployment_servo"]
    await self.actuators.update_servo(servo["pin"], servo["deploy_angle"])


@Logger
async def undeploy_god_hand(self):
    await asyncio.sleep(CONFIG.MINIMUM_DELAY)
    servo = CONFIG.FRONT_GOD_HAND["deployment_servo"]
    await self.actuators.update_servo(servo["pin"], servo["undeploy_angle"])


@Logger
async def vertical_god_hand(self):
    await asyncio.sleep(CONFIG.MINIMUM_DELAY)
    servo = CONFIG.FRONT_GOD_HAND["deployment_servo"]
    await self.actuators.update_servo(servo["pin"], servo["vertical_angle"])


@Logger
async def open_god_hand(self):
    for servo in CONFIG.FRONT_GOD_HAND["take_servo"]:
        await asyncio.sleep(CONFIG.MINIMUM_DELAY)
        await self.actuators.update_servo(servo["pin"], servo["open_angle"])


@Logger
async def close_god_hand(self):
    for servo in CONFIG.FRONT_GOD_HAND["take_servo"]:
        await asyncio.sleep(CONFIG.MINIMUM_DELAY)
        await self.actuators.update_servo(servo["pin"], servo["close_angle"])


@Logger
async def lift_elevator(self):
    await asyncio.sleep(CONFIG.MINIMUM_DELAY)
    stepper = CONFIG.ELEVATOR
    await self.actuators.stepper_step(
        steps=stepper["up_steps"],
        pin_dir=stepper["pin_dir"],
        pin_step=stepper["pin_step"],
        speed=stepper["speed"],
        driver_on=stepper["driver_on"],
        pin_driver=stepper["pin_driver"],
    )


async def lower_elevator(self):
    await asyncio.sleep(CONFIG.MINIMUM_DELAY)
    stepper = CONFIG.ELEVATOR
    await self.actuators.stepper_step(
        steps=stepper["down_steps"],
        pin_dir=stepper["pin_dir"],
        pin_step=stepper["pin_step"],
        speed=stepper["speed"],
        driver_on=stepper["driver_on"],
        pin_driver=stepper["pin_driver"],
    )


async def elevator_top(self, speed: int = CONFIG.ELEVATOR["speed"]) -> None:
    await self.actuators.stepper_step(
        CONFIG.ELEVATOR["top_steps"] - self.elevator_ticks, speed
    )


async def elevator_bottom(self, speed: int = CONFIG.ELEVATOR["speed"]) -> None:
    await self.actuators.stepper_step(
        CONFIG.ELEVATOR["bottom_steps"] - self.elevator_ticks, speed
    )


async def elevator_intermediate(self, speed: int = CONFIG.ELEVATOR["speed"]) -> None:
    await self.actuators.stepper_step(
        CONFIG.ELEVATOR["intermediate_steps"] - self.elevator_ticks, speed
    )


async def god_hand_demo(self):
    while True:
        await self.vertical_god_hand()
        await asyncio.sleep(0.5)
        await self.undeploy_god_hand()
        await asyncio.sleep(0.5)
        await self.deploy_god_hand()
        await asyncio.sleep(1)
        await self.open_god_hand()
        await asyncio.sleep(1)
        await self.close_god_hand()
        await asyncio.sleep(1)
        await self.undeploy_god_hand()
        await asyncio.sleep(0.5)
        await self.vertical_god_hand()
        await asyncio.sleep(0.5)


async def smart_go_to(
    self,
    position: Point,
    *,  # force keyword arguments
    tolerance: float = 5,
    timeout: float = -1,  # in seconds
    skip_and_clear_queue: bool = False,
    forward: bool = True,
    relative: bool = False,
    max_speed: int = 160,
    next_position_delay: int = 100,
    action_error_auth: int = 30,
    traj_precision: int = 30,
    correction_trajectory_speed: int = 160,
    acceleration_start_speed: int = 160,
    acceleration_distance: float = 0,
    deceleration_end_speed: int = 160,
    deceleration_distance: float = 0,
    fails: int = 0,
) -> GoToResult:

    result: int = await self.rolling_basis.go_to_and_wait(
        position,
        skip_and_clear_queue=skip_and_clear_queue,
        tolerance=tolerance,
        timeout=timeout,
        forward=forward,
        relative=relative,
        max_speed=max_speed,
        next_position_delay=next_position_delay,
        action_error_auth=action_error_auth,
        traj_precision=traj_precision,
        correction_trajectory_speed=correction_trajectory_speed,
        acceleration_start_speed=acceleration_start_speed,
        acceleration_distance=acceleration_distance,
        deceleration_end_speed=deceleration_end_speed,
        deceleration_distance=deceleration_distance,
    )
    if result == GoToResult.STOPPED:
        # ACS handling strategy:
        result = await self.handle_acs(
            position,
            skip_and_clear_queue=skip_and_clear_queue,
            tolerance=tolerance,
            timeout=timeout,
            forward=forward,
            relative=relative,
            max_speed=max_speed,
            next_position_delay=next_position_delay,
            action_error_auth=action_error_auth,
            traj_precision=traj_precision,
            correction_trajectory_speed=correction_trajectory_speed,
            acceleration_start_speed=acceleration_start_speed,
            acceleration_distance=acceleration_distance,
            deceleration_end_speed=deceleration_end_speed,
            deceleration_distance=deceleration_distance,
            fails=0,
        )

    return result


async def handle_acs(
    self,
    original_target: Point,
    *,  # force keyword arguments
    skip_and_clear_queue: bool = False,
    tolerance: float = 5,
    timeout: float = -1,  # in seconds
    forward: bool = True,
    relative: bool = False,
    max_speed: int = 160,
    next_position_delay: int = 100,
    action_error_auth: int = 30,
    traj_precision: int = 30,
    correction_trajectory_speed: int = 160,
    acceleration_start_speed: int = 160,
    acceleration_distance: float = 0,
    deceleration_end_speed: int = 160,
    deceleration_distance: float = 0,
    fails: int = 0,
) -> int:
    if self.anticollision_mode != AntiCollisionHandle.DO_NOTHING:
        self.logger.log(
            f"ACS triggered, performing emergency stop", LogLevels.WARNING, self.leds
        )
        self.rolling_basis.stop_and_clear_queue()
    else:
        self.logger.log(
            f"ACS triggered, no emergency stop", LogLevels.WARNING, self.leds
        )
    match self.anticollision_handle:
        case AntiCollisionHandle.DO_NOTHING:
            return GoToResult.STOPPED
        case AntiCollisionHandle.WAIT_AND_FAIL:
            await asyncio.sleep(CONFIG.ANTICOLLISION_WAIT_AND_FAIL_DELAY)
            return GoToResult.STOPPED
        case AntiCollisionHandle.WAIT_AND_RETRY:
            if fails < CONFIG.ANTICOLLISION_WAIT_AND_RETRY_MAX_TRIES:
                await asyncio.sleep(CONFIG.ANTICOLLISION_WAIT_AND_RETRY_DELAY)
                return await self.smart_go_to(
                    original_target,
                    skip_and_clear_queue=skip_and_clear_queue,
                    tolerance=tolerance,
                    timeout=timeout,
                    forward=forward,
                    relative=relative,
                    max_speed=max_speed,
                    next_position_delay=next_position_delay,
                    action_error_auth=action_error_auth,
                    traj_precision=traj_precision,
                    correction_trajectory_speed=correction_trajectory_speed,
                    acceleration_start_speed=acceleration_start_speed,
                    acceleration_distance=acceleration_distance,
                    deceleration_end_speed=deceleration_end_speed,
                    deceleration_distance=deceleration_distance,
                    fails=fails + 1,
                )
            else:
                return GoToResult.STOPPED

        case AntiCollisionHandle.AVOID:
            if fails < CONFIG.ANTICOLLISION_WAIT_AND_AVOID_MAX_TRIES:

                old_anticollision_handle = self.anticollision_handle

                async def reset_anticollision_handle():
                    await asyncio.sleep(
                        CONFIG.ANTICOLLISION_WAIT_AND_AVOID_TIME_WITHOUT_ACS
                    )
                    self.anticollision_mode = old_anticollision_handle

                await asyncio.sleep(
                    0.5
                )  # Time to stabilise to make sure the estimation of CONFIG.ANTICOLLISION_WAIT_AND_AVOID_TIME_WITHOUT_ACS is ok

                self.anticollision_handle = LidarMode.DISABLED

                # In case of timeout
                safety = asyncio.create_task(reset_anticollision_handle())

                await self.rolling_basis.go_to_and_wait(
                    Point(-CONFIG.ANTICOLLISION_WAIT_AND_AVOID_DISTANCE, 0),
                    skip_and_clear_queue=skip_and_clear_queue,
                    tolerance=tolerance,
                    timeout=min(timeout, 3),
                    forward=not forward,
                    relative=True,
                    **CONFIG.GO_TO_PROFILES["slow_and_precise"],
                )

                # Reset without waiting for the trigger
                self.self.anticollision_handle = old_anticollision_handle
                # Avoid the risk of triggering during another temporary disable
                safety.cancel()

                return await self.smart_go_to(
                    original_target,
                    skip_and_clear_queue=skip_and_clear_queue,
                    tolerance=tolerance,
                    timeout=timeout,
                    forward=forward,
                    relative=relative,
                    max_speed=max_speed,
                    next_position_delay=next_position_delay,
                    action_error_auth=action_error_auth,
                    traj_precision=traj_precision,
                    correction_trajectory_speed=correction_trajectory_speed,
                    acceleration_start_speed=acceleration_start_speed,
                    acceleration_distance=acceleration_distance,
                    deceleration_end_speed=deceleration_end_speed,
                    deceleration_distance=deceleration_distance,
                    fails=fails + 1,
                )
            else:
                return GoToResult.STOPPED

        case _:
            raise Exception(
                f"No AntiCollisionHandle{self.anticollision_handle.value} implementation"
            )


async def go_best_zone(self, plant_zones: list[Plants_zone]):
    destination_point = None
    destination_plant_zone = None
    for plant_zone in plant_zones:
        target = self.arena.compute_go_to_destination(
            start_point=self.rolling_basis.odometrie,
            zone=plant_zone.zone,
        )
        print("Target:", destination_point)
        # if self.arena.enable_go_to_point(
        #     self.rolling_basis.odometrie,
        #     target,
        # ):
        #     pass
        destination_point = target
        destination_plant_zone = plant_zone
        break
    print("Destination:", destination_point)
    if (
        destination_point != None
        and (
            await self.smart_go_to(
                position=destination_point,
                timeout=30,
                **CONFIG.SPEED_PROFILES["cruise_speed"],
                **CONFIG.PRECISION_PROFILES["classic_precision"],
            )
        )
        == 0
    ):
        return True, destination_plant_zone
    return False, destination_plant_zone
