"""Hardware actuator implementation used during demonstrations."""

from __future__ import annotations

import time
from enum import Enum, auto
from dataclasses import dataclass
from typing import TYPE_CHECKING

from a_config_loader import CONFIG
from controllers.actuators.base.actuators import Actuators


R_ARM_SERVO_PIN = 0
L_ARM_SERVO_PIN = 1
R_ROTATE_SERVO_PIN = 2
L_ROTATE_SERVO_PIN = 3
CURSOR_SERVO_PIN = 4

if TYPE_CHECKING:
    from loggerplusplus import Logger


class ActuatorState(Enum):
    EXTENDING = auto()
    RETRACTING = auto()
    STOPPED = auto()


@dataclass
class Servo:
    """Description of a generic servo angle configuration.

    Attributes:
        retract_angle (int): Retract angle for the servo (in degrees).
        max_angle (int): Maximum angle for the servo (in degrees).
    """
    retract_angle: int
    """Default angle for the servo (in degrees)."""

    max_angle: int
    """Maximum angle for the servo (in degrees)."""


@dataclass
class ArmServo(Servo):
    extend_angle: int
    """Angle to extend the servo (in degrees)."""


@dataclass
class RotateServo(Servo):

    rotation_angle: int
    """Angle to rotate the servo (in degrees)."""


@dataclass
class CursorServo(Servo):

    deploy_angle: int
    """Angle to rotate the servo (in degrees)."""


@dataclass
class LinearActuator:
    extend_time: float
    """Time to extend the linear actuator (in seconds)."""
    retract_time: float
    """Time to retract the linear actuator (in seconds)."""
    state: ActuatorState = ActuatorState.STOPPED
    """Current state of the linear actuator."""


@dataclass
class Stepper:
    """Parameters for a stepper motor.

    Attributes:
        top_steps (int): Number of steps to reach the top position.
        folded_steps (int): Number of steps to reach the folded position.
        bottom_steps (int): Number of steps to reach the bottom position.
        speed (int): Speed of the stepper motor.
    """

    top_steps: int
    """Number of steps to reach the top position."""
    folded_steps: int
    """Number of steps to reach the folded position."""
    bottom_steps: int
    """Number of steps to reach the bottom position."""
    speed: int
    """Speed of the stepper motor."""


class ActuatorsWinter(Actuators):  # noqa: PLR0904 # pylint: disable=too-many-public-methods
    """Implementation of actuators for the winter mode.

    Inherits from :class:`Actuators` and overrides its methods to provide
    hardware-specific functionality.
    """

    def __init__(
        self,
        logger: Logger,
        serial_number: int = CONFIG.ACTUATOR_TEENSY_SER,
        vid: int = CONFIG.TEENSY_VID,
        pid: int = CONFIG.TEENSY_PID,
        baudrate: int = CONFIG.TEENSY_BAUDRATE,
        *,
        enable_crc: bool = CONFIG.TEENSY_CRC,
        enable_dummy: bool = CONFIG.ACTUATORS_DUMMY,
    ) -> None:
        """Initialize the ``ActuatorsShow`` class.

        Args:
            logger (Logger): The logger instance for logging.
            serial_number (int, optional):
                The serial number of the Teensy. Defaults to CONFIG.ACTUATOR_TEENSY_SER.
            vid (int, optional):
                The vendor ID of the Teensy. Defaults to CONFIG.TEENSY_VID.
            pid (int, optional):
                The product ID of the Teensy. Defaults to CONFIG.TEENSY_PID.
            baudrate (int, optional): The baud rate for serial communication.
                Defaults to CONFIG.TEENSY_BAUDRATE.
            enable_crc (bool, optional):
                Whether to enable CRC checks. Defaults to CONFIG.TEENSY_CRC.
            enable_dummy (bool, optional):
                Whether to enable dummy mode. Defaults to CONFIG.ACTUATORS_DUMMY.
        """
        super().__init__(
            logger=logger,
            serial_number=serial_number,
            vid=vid,
            pid=pid,
            baudrate=baudrate,
            enable_crc=enable_crc,
            enable_dummy=enable_dummy,
        )  # Call the parent constructor
        self.folded: bool = True  # Indicates if the actuators are folded
        self.elevator_ticks: int = 0
        self.servos: dict[int, Servo] = {}

        for pin_str, cfg in CONFIG.ACTUATOR_SERVOS_CONFIG.items():
            pin = int(pin_str)
            if "extend_angle" in cfg:
                self.servos[pin] = ArmServo(
                    retract_angle=cfg["retract_angle"],
                    max_angle=cfg["max_angle"],
                    extend_angle=cfg["extend_angle"]
                )
            elif "rotate_angle" in cfg:
                self.servos[pin] = RotateServo(
                    retract_angle=cfg["retract_angle"],
                    max_angle=cfg["max_angle"],
                    rotation_angle=cfg["rotate_angle"]
                )
            else:
                self.servos[pin] = CursorServo(
                    retract_angle=cfg["retract_angle"],
                    max_angle=cfg["max_angle"],
                    deploy_angle=cfg["deploy_angle"]
                )

        stepper_config = CONFIG.ACTUATOR_ELEVATOR_CONFIG
        self._logger.info(f"[CTRL:ACT] Stepper config: {stepper_config}")
        self.stepper = Stepper(
            stepper_config["top_steps"],
            stepper_config["folded_steps"],
            stepper_config["bottom_steps"],
            stepper_config["speed"],
        )

        linear_actuator_config = CONFIG.ACTUATOR_LINEAR_CONFIG
        self._logger.info(f"[CTRL:ACT] Linear actuator config: {linear_actuator_config}")

        self.gripper = LinearActuator(
            linear_actuator_config["extend_time"],
            linear_actuator_config["retract_time"]
        )

    # Protected methods
    def _check_pin(self, pin: int) -> bool:
        """Checks if the specified pin is a valid servo pin.

        Args:
            pin (int): The pin number to check.

        Returns:
            bool: ``True`` if the pin is a valid servo pin, ``False`` otherwise.
        """
        if pin not in self.servos:
            self._logger.warning(
                f"[CTRL:ACT] Invalid servo pin {pin}, not configured",
            )
            return False
        return True

    # Public methods
    def extend(self, pin: int) -> None:
        """Extend the servo connected to the specified pin.

        Args:
            pin (int): The pin number of the servo to extend.
        """
        if not self._check_pin(pin):
            return

        servo = self.servos[pin]

        if isinstance(servo, ArmServo):
            angle = servo.extend_angle
        elif isinstance(servo, RotateServo):
            angle = servo.rotation_angle
        else:
            return

        self.set_servo_angle(pin, angle, max_angle=servo.max_angle)

    def retract(self, pin):
        if self._check_pin(pin):
            self.set_servo_angle(
                pin,
                self.servos[pin].retract_angle,
                max_angle=self.servos[pin].max_angle,
            )

    def extend_arm(self) -> None:
        """Extend the specified servos to their extend angle.

        This method sets the specified servos to their extend angle, effectively
        extending the servo arm.
        """
        pins = [R_ARM_SERVO_PIN, L_ARM_SERVO_PIN]
        for pin in pins:
            if isinstance(self.servos[pin], ArmServo):
                self.extend(pin)

    def retract_arm(self) -> None:
        """Retract the specified servos to their retract angle.

        This method sets the specified servos to their retract angle, effectively
        retracting the servo arm.
        """
        pins = [R_ARM_SERVO_PIN, L_ARM_SERVO_PIN]
        for pin in pins:
            if isinstance(self.servos[pin], ArmServo):
                self.retract(pin)

    def retract_all(self) -> None:
        """Retract all servos to their retract angle.

         This method sets all configured servos to their retract angle, effectively
         retracting all servo arms."""
        # A voir pour l'ordre extact des actionneurs pour que ça se pète pas mais osef je sors tout de mon cul la
        for i in self.servos:
            self.retract(i)

    def deploy_cursor(self) -> None:
        """Deploy the cursor by setting the specified servo to its deployment angle.

        This method sets the specified servo to its deployment angle, effectively
        deploying the cursor.
        """
        servo = self.servos[CURSOR_SERVO_PIN]
        if isinstance(servo, CursorServo):
            angle = servo.deploy_angle
            self.set_servo_angle(
                CURSOR_SERVO_PIN,
                angle,
                max_angle=self.servos[CURSOR_SERVO_PIN].max_angle)

    def rotate_gripper(self) -> None:
        """Rotate the gripper by setting the specified servos to their rotation angle.

        This method sets the specified servos to their rotation angle, effectively
        rotating the gripper.
        """
        pins = [R_ROTATE_SERVO_PIN, L_ROTATE_SERVO_PIN]
        for pin in pins:
            servo = self.servos[pin]
            if isinstance(servo, RotateServo):
                angle = servo.rotation_angle
                self.set_servo_angle(
                    pin,
                    angle,
                    max_angle=self.servos[pin].max_angle)

    def unrotate_gripper(self) -> None:
        """Unrotate the gripper by setting the specified servos to their retract angle.

        This method sets the specified servos to their retract angle, effectively
        unrotating the gripper."""
        pins = [R_ROTATE_SERVO_PIN, L_ROTATE_SERVO_PIN]
        for pin in pins:
            if isinstance(self.servos[pin], RotateServo):
                self.retract(pin)

    def grab_jenga(self) -> None:
        """Grab the Jenga block by extending the linear actuator.

        This method extends the linear actuator to grab the Jenga block, and then
        stops the actuator after the specified extend time.
        """
        actuator = self.gripper
        actuator.state = ActuatorState.EXTENDING

        self._logger.info("[CTRL:ACT] Grabbing Jenga (linear actuators extend)")
        time.sleep(actuator.extend_time)

        actuator.state = ActuatorState.STOPPED

    def release_jenga(self) -> None:
        """ Release the Jenga block by retracting the linear actuator.

        This method retracts the linear actuator to release the Jenga block, and then
        stops the actuator after the specified retract time.
        """
        actuator = self.gripper
        actuator.state = ActuatorState.RETRACTING

        self._logger.info("[CTRL:ACT] Releasing Jenga (linear actuators retract)")
        time.sleep(actuator.retract_time)

        actuator.state = ActuatorState.STOPPED

    def prepare_to_rotate(self) -> None:
        """Prepare the gripper for rotation by retracting the linear actuator.

        This method retracts the linear actuator to prepare the gripper for rotation, and then
        stops the actuator after the specified retract time."""
        self._logger.info("[CTRL:ACT] Preparing to rotate (retracting gripper)")

        self.extend_arm()

        actuator = self.gripper
        if actuator.state != ActuatorState.RETRACTING:
            actuator.state = ActuatorState.RETRACTING
            time.sleep(actuator.retract_time)
            actuator.state = ActuatorState.STOPPED

    def rotate_jenga(self):
        """Rotate the gripper by extending the linear actuator.

         This method extends the linear actuator to rotate the gripper, and then
         stops the actuator after the specified extend time."""
        # Pareil j'ai pas tout capté de la mécanique du truc mais osef, je sors tout de mon cul, on modif apres
        self._logger.info("[CTRL:ACT] Rotating Jenga (extending gripper)")
        self.grab_jenga()
        self.rotate_gripper()
        self.release_jenga()
        self.unrotate_gripper()

    def block_jenga(self) -> None:
        """Block Jenga blocks by doing idk what
        """
        # J'ai pas capté comment on bloque les jengas pour les déplacer avec le moddé, je demande a Anais ou Adrien
        self._logger.info("[CTRL:ACT] Blocking Jengas to move around.")


    def go_to_top(self) -> None:
        """Move the elevator to the top position.

        If the elevator is folded, it will move to the folded position first.
        """
        if self.folded and not self.elevator_ticks:
            self.elevator_ticks = self.stepper.folded_steps
        steps_to_move = self.stepper.top_steps - self.elevator_ticks
        self._logger.info(f"[CTRL:ACT] Elevator to top: {steps_to_move} steps")
        self.stepper_step(steps_to_move, self.stepper.speed, disable_driver=False)
        self._logger.debug(
            f"[CTRL:ACT] Elevator position: {self.elevator_ticks} steps",
        )

    def go_to_bottom(self) -> None:
        """Move the elevator to the bottom position.

        If the elevator is folded, it will move to the folded position first.
        """
        steps_to_move = self.stepper.bottom_steps - self.elevator_ticks
        self._logger.info(f"[CTRL:ACT] Elevator to bottom: {steps_to_move} steps")
        self.stepper_step(steps_to_move, self.stepper.speed, disable_driver=True)
        self._logger.debug(
            f"[CTRL:ACT] Elevator position: {self.elevator_ticks} steps",
        )




