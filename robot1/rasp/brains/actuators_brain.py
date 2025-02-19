# External imports
import asyncio
import math

# Import from common
from config_loader import CONFIG

from taskbrain import Brain

from geometry import OrientedPoint, Point
from arena import ShowArena, BaseArenaZone
from loggerplusplus import Logger, log
from utils import LidarMode, AntiCollisionHandle

# Import from local path
from controllers import RollingBasis, RollingBasisDummy, Actuators

from utils import GoToResult


# Actions for servos
@log("Actuator Brain")
async def bring_inside_left(self):
    await asyncio.sleep(CONFIG.MINIMUM_DELAY)
    servo = CONFIG.MAGNET_ARM_LEFT
    await self.actuators.update_servo(servo["pin"], servo["catch_angle"])


@log("Actuator Brain")
async def bring_inside_right(self):
    await asyncio.sleep(CONFIG.MINIMUM_DELAY)
    servo = CONFIG.MAGNET_ARM_RIGHT
    await self.actuators.update_servo(servo["pin"], servo["catch_angle"])


@log("Actuator Brain")
async def bring_outside_left(self):
    await asyncio.sleep(CONFIG.MINIMUM_DELAY)
    servo = CONFIG.MAGNET_ARM_LEFT
    await self.actuators.update_servo(servo["pin"], servo["release_angle"])


@log("Actuator Brain")
async def bring_outside_right(self):
    await asyncio.sleep(CONFIG.MINIMUM_DELAY)
    servo = CONFIG.MAGNET_ARM_RIGHT
    await self.actuators.update_servo(servo["pin"], servo["release_angle"])


# Possible de faire une fonction différente pour droite et gauche (ça enlèverai "pin: int")
@log("Actuator Brain")
async def magnetize(self, pin: int):
    await asyncio.sleep(CONFIG.MINIMUM_DELAY)
    servo = CONFIG.MAGNET_ARMS
    await self.actuators.update_servo(pin, servo["magnetize_angle"])


@log("Actuator Brain")
async def demagnetize(self, pin: int):
    await asyncio.sleep(CONFIG.MINIMUM_DELAY)
    servo = CONFIG.MAGNET_ARMS
    await self.actuators.update_servo(pin, servo["demagnetize_angle"])


# Actions for stepper
@log("Actuator Brain")
async def elevator_bottom(self, speed=CONFIG.ELEVATOR_SPEED):
    # Ajout bouton poussoire incessamment  sous peu
    # Donc il suffira de descendre jusqu'à qu'il soit touché
    await self.actuators.stepper_step(
        CONFIG.ELEVATOR["bottom_steps"] - self.actuators.elevator_ticks, speed
    )


@log("Actuator Brain")
async def elevator_top(self, speed=CONFIG.ELEVATOR_SPEED):
    await self.actuators.stepper_step(
        CONFIG.ELEVATOR["top_steps"] - self.actuators.elevator_ticks, speed
    )


@log("Actuator Brain")
async def elevator_floor0(self, speed=CONFIG.ELEVATOR_SPEED):
    await self.actuators.stepper_step(
        CONFIG.ELEVATOR["floor0_steps"] - self.actuators.elevator_ticks, speed
    )


@log("Actuator Brain")
async def elevator_floor1(self, speed=CONFIG.ELEVATOR_SPEED):
    await self.actuators.stepper_step(
        CONFIG.ELEVATOR["floor1_steps"] - self.actuators.elevator_ticks, speed
    )


@log("Actuator Brain")
async def elevator_floor2(self, speed=CONFIG.ELEVATOR_SPEED):
    await self.actuators.stepper_step(
        CONFIG.ELEVATOR["floor2_steps"] - self.actuators.elevator_ticks, speed
    )


# Test entièrement arbitraire qui ne marchera pas pour l'instant
# Faudrait voir si le robot doit bouger pour faire les étages
# ou s'il peut rester sur place tout du long
async def test_build_floor_0_1(self):
    while True:
        await self.elevator_bottom()
        await asyncio.sleep(0.5)
        await self.elevator_floor0()
        await asyncio.sleep(0.5)
        await self.magnetize(pin=37)
        await self.magnetize(pin=38)
        await asyncio.sleep(0.5)
        await self.bring_inside_left()
        await self.bring_inside_right()
        await asyncio.sleep(1)
        await self.bring_outside_left()
        await self.bring_outside_right()
        await asyncio.sleep(1)
        await self.elevator_floor1()
        await asyncio.sleep(1)
        await self.bring_inside_left()
        await self.bring_inside_right()
        await asyncio.sleep(1)
        await self.demagnetize(pin=37)
        await self.demagnetize(pin=38)

