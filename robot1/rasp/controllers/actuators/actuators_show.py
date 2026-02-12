"""Hardware actuator implementation used during demonstrations."""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import TYPE_CHECKING

from a_config_loader import CONFIG
from controllers.actuators.base.actuators import Actuators

ARM_SERVO_PIN = 8

if TYPE_CHECKING:
    from loggerplusplus import Logger


@dataclass
class Servo:
    """Description of a generic servo angle configuration.

    Attributes:
        deploy_angle (int): Angle to deploy the servo (in degrees).
        fold_angle (int): Angle to fold the servo (in degrees).
        max_angle (int): Maximum angle for the servo (in degrees).
    """

    deploy_angle: int
    """Angle to deploy the servo (in degrees)."""
    fold_angle: int
    """Angle to fold the servo (in degrees)."""
    max_angle: int
    """Maximum angle for the servo (in degrees)."""


@dataclass
class ServoDocking(Servo):
    """Servo with an extra docking angle.

    Attributes:
        docking (int): Angle for special movement such as docking.
    """

    docking: int = 0
    """Angle for special movement such as docking."""


@dataclass
class ServoArm(Servo):
    """Servo controlling an arm mechanism.

    Attributes:
        docking (int): Angle for special movement such as docking.
    """

    docking: int
    """Angle for special movement such as docking."""


@dataclass
class ServoPlank(Servo):
    """Servo dedicated to plank maintenance.

    Attributes:
        maintain_plank (int): Angle to maintain the plank position (in degrees).
    """

    maintain_plank: int
    """Angle to maintain the plank position (in degrees)."""


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


class ActuatorsShow(Actuators):  # noqa: PLR0904 # pylint: disable=too-many-public-methods
    """Implementation of actuators for the show mode.

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
        self.servos: dict[
            int,
            Servo | ServoArm | ServoPlank | ServoDocking,
        ] = {  # default servo with 2 position
            i: Servo(cfg["deploy_angle"], cfg["fold_angle"], cfg["max_angle"])
            for i, cfg in CONFIG.ACTUATOR_SERVOS_CONFIG.items()
            if i < ARM_SERVO_PIN
        }

        # Modify servos 0 and 2:
        self.servos[0] = ServoDocking(
            self.servos[0].deploy_angle,
            self.servos[0].fold_angle,
            self.servos[0].max_angle,
            CONFIG.ACTUATOR_SERVOS_CONFIG[0]["docking"],
        )

        self.servos[2] = ServoDocking(
            self.servos[2].deploy_angle,
            self.servos[2].fold_angle,
            self.servos[2].max_angle,
            CONFIG.ACTUATOR_SERVOS_CONFIG[2]["docking"],
        )

        # 0: Interior Right Arm
        # 1 : Interior Right Magnet
        # 2 : Interior Left Arm
        # 3 : Interior Left Magnet
        # 4 : Exterior Right Arm
        # 5 : Exterior Right Magnet
        # 6 : Exterior Left Arm
        # 7 : Exterior Left Magnet

        servo_arm = CONFIG.ACTUATOR_SERVOS_CONFIG[ARM_SERVO_PIN]
        self.servos[ARM_SERVO_PIN] = ServoArm(
            servo_arm["deploy_angle"],
            servo_arm["fold_angle"],
            servo_arm["max_angle"],
            servo_arm["docking"],
        )

        servo_plank = CONFIG.ACTUATOR_SERVOS_CONFIG[9]
        self.servos[9] = ServoPlank(
            servo_plank["deploy_angle"],
            servo_plank["fold_angle"],
            servo_plank["max_angle"],
            servo_plank["maintain_plank"],
        )

        # 9 : Folded = Catch plank

        stepper_config = CONFIG.ACTUATOR_ELEVATOR_CONFIG
        self.logger.info(f"{stepper_config}")
        self.stepper = Stepper(
            stepper_config["top_steps"],
            stepper_config["folded_steps"],
            stepper_config["bottom_steps"],
            stepper_config["speed"],
        )

    # Protected methods
    def _check_pin(self, pin: int) -> bool:
        """Checks if the specified pin is a valid servo pin.

        Args:
            pin (int): The pin number to check.

        Returns:
            bool: ``True`` if the pin is a valid servo pin, ``False`` otherwise.
        """
        if pin not in self.servos or self.servos[pin] is None:
            self.logger.warning(f"Pin {pin} is not a servo")
            return False
        return True

    # Private methods
    def __move_to_save_folded_position(self) -> None:
        """Move the elevator to a safe folded position.

        This method ensures that the elevator is in a safe state before the
        servo arm is deployed.
        """
        steps_to_move = self.stepper.folded_steps - self.elevator_ticks + 20
        self.stepper_step(steps_to_move, self.stepper.speed, disable_driver=False)

    def __align_dropping_cans(self) -> None:
        """Align the dropping cans by setting the servos to specific angles.

        This method sets the angles of the servos to predefined values for the
        dropping cans.
        """
        self.set_servo_angle(pin=4, angle=160, max_angle=270)
        self.set_servo_angle(pin=6, angle=90, max_angle=270)

    # Public methods

    def deploy(self, pins: int | list[int]) -> None:
        """Deploy the specified servos to their deploy angle.

        This method sets the given servos to their deploy angle, effectively
        extending the servo arm.

        Args:
            pins (int | list[int]): The pin number or a list of pin numbers to deploy.
        """
        if isinstance(pins, int):
            pins = [pins]
        for pin in pins:
            if pin == ARM_SERVO_PIN:
                self.folded = False
            if self._check_pin(pin):
                self.set_servo_angle(
                    pin,
                    self.servos[pin].deploy_angle,
                    max_angle=self.servos[pin].max_angle,
                )

    def fold(self, pins: int | list[int]) -> None:
        """Fold the specified servos to their fold angle.

        This method sets the specified servos to their fold angle, effectively
        retracting the servo arm.

        Args:
            pins (int | list[int]): The pin number or a list of pin numbers to fold.
        """
        if isinstance(pins, int):
            pins = [pins]
        for pin in pins:
            if self._check_pin(pin):
                if pin == ARM_SERVO_PIN:
                    self.__move_to_save_folded_position()
                    self.folded = True
                self.set_servo_angle(
                    pin,
                    self.servos[pin].fold_angle,
                    max_angle=self.servos[pin].max_angle,
                )

    def deploy_all(self) -> None:
        """Deploy all servos to their deploy angle.

        This method sets all servos to their deploy angle, effectively
        deploying the servo arm.
        """
        if ARM_SERVO_PIN in self.servos:
            # self.deploy(ARM_SERVO_PIN)
            pass

        for i in self.servos:
            if i != ARM_SERVO_PIN:
                self.deploy(i)

    def deploy_all_pickup(self) -> None:
        """Deploy all servos and move the elevator to a safe pickup position.

        This method ensures that the elevator is in a safe position before the
        servo arm is deployed.
        """
        self.folded = False
        self.docking([0, 2])

        for i in self.servos:
            if i != ARM_SERVO_PIN:
                self.deploy(i)

    def fold_all(self) -> None:
        """Fold all servos to their fold angle.

        This method sets all servos to their fold angle, effectively folding the
        servo arm.
        """
        for i in self.servos:
            if i != ARM_SERVO_PIN:
                self.fold(i)

        if ARM_SERVO_PIN in self.servos:
            # self.fold(ARM_SERVO_PIN)
            pass

    def demagnetize_all(self) -> None:
        """Demagnetize servos by setting them to their fold angle.

        This is useful for ensuring that the servos are not holding any
        position when they are not in use.
        """
        pins = [1, 3, 5, 7]
        for pin in pins:
            if self._check_pin(pin):
                self.set_servo_angle(
                    pin,
                    self.servos[pin].fold_angle,
                    max_angle=self.servos[pin].max_angle,
                )

    def magnetize_all(self) -> None:
        """Magnetize servos by setting them to their deploy angle.

        This is useful for ensuring that the servos are holding their position
        when they are in use.
        """
        pins = [1, 3, 5, 7]
        for pin in pins:
            if self._check_pin(pin):
                self.set_servo_angle(
                    pin,
                    self.servos[pin].deploy_angle,
                    max_angle=self.servos[pin].max_angle,
                )

    def docking(self, pins: int | list[int]) -> None:
        """Move the interior servo arms to the docking position.

        Args:
            pins (int | list[int]): Pin or list of pins to move.
        """
        if isinstance(pins, int):
            pins = [pins]
        for pin in pins:
            if self._check_pin(pin):
                servo = self.servos[pin]
                if not isinstance(servo, (ServoDocking, ServoArm)):
                    self.logger.warning(
                        f"Pin {pin} is not a ServoDocking or ServoArm,"
                        " cannot perform docking.",
                    )
                else:
                    self.set_servo_angle(
                        pin,
                        servo.docking,
                        max_angle=servo.max_angle,
                    )

    def deploy_banner(self) -> None:
        """Deploy the banner by extending servos 0 and 2."""
        self.deploy([0, 2])

    def place_upper_cans(self) -> None:
        """Place the upper cans by setting servos to specific angles.

        This sets the angles of the servos to predefined values for the upper
        cans.
        """
        self.set_servo_angle(pin=4, angle=160, max_angle=270)
        self.set_servo_angle(pin=6, angle=90, max_angle=270)

    def raise_plank(self) -> None:
        """Raise the plank by moving the elevator to the top position.

        This method is used to raise the plank to its top position.
        """
        steps_to_move = self.stepper.top_steps
        self.stepper_step(steps_to_move, self.stepper.speed)

    def go_to_top(self) -> None:
        """Move the elevator to the top position.

        If the elevator is folded, it will move to the folded position first.
        """
        if self.folded and not self.elevator_ticks:
            self.elevator_ticks = self.stepper.folded_steps
        steps_to_move = self.stepper.top_steps - self.elevator_ticks
        self.logger.info(f"Moving to top: {steps_to_move} steps")
        self.stepper_step(steps_to_move, self.stepper.speed, disable_driver=False)
        self.logger.info(f"Steps current: {self.elevator_ticks}")

    def elevator_drop_top(self) -> None:
        """Move the elevator to the top position.

        If the elevator is folded, it will move to the folded position first.
        """
        if self.folded and not self.elevator_ticks:
            self.elevator_ticks = self.stepper.folded_steps
        steps_to_move = 600 - self.elevator_ticks
        self.logger.info(f"Moving to top: {steps_to_move} steps")
        self.stepper_step(steps_to_move, self.stepper.speed, disable_driver=False)
        self.logger.info(f"Steps current: {self.elevator_ticks}")

    def go_to_bottom(self) -> None:
        """Move the elevator to the bottom position.

        If the elevator is folded, it will move to the folded position first.
        """
        steps_to_move = self.stepper.bottom_steps - self.elevator_ticks
        self.logger.info(f"Moving to bottom: {steps_to_move} steps")
        self.stepper_step(steps_to_move, self.stepper.speed, disable_driver=True)
        self.logger.info(f"Steps current: {self.elevator_ticks}")

    def build_floors(
        self,
    ) -> None:
        # Ask if I should use time.sleep or asyncio.sleep and making this method async
        """Build the floors by deploying the servos and moving the elevator.

        This method deploys servos and raises the elevator to construct the
        floors.
        """
        self.go_to_top()
        time.sleep(2)
        # Set cans to correct position
        self.__align_dropping_cans()
        time.sleep(2)

        # Demagnetize and release plank
        # self.deploy(ARM_SERVO_PIN)
        self.demagnetize_all()
        # self.deploy(9)

        time.sleep(2)

        # Retrieve actuators
        self.fold(4)
        self.fold(6)
        # self.docking(ARM_SERVO_PIN)

    # def init_actuator(self):
    #     self.stepper_step(
    #         self.stepper.top_steps - self.elevator_ticks, self.stepper.speed
    #     )
    #     self.fold_all()
    #     self.stepper_step(
    #         self.stepper.folded_steps - self.elevator_ticks, self.stepper.speed
    #     )

    def ready_to_pickup(self) -> None:
        """Prepare and magnetize all servos."""
        # Prep and go magnetized
        self.deploy_all_pickup()  # Magnetize
        time.sleep(1)
        # self.deploy(ARM_SERVO_PIN)

    def pick_up(self) -> None:
        """Catch cans and plank."""
        # Catch and raise cans and plank
        self.pickup_planck()
        # self.fold(9)
        time.sleep(0.1)
        # self.docking(ARM_SERVO_PIN)
        time.sleep(1)
        self.fold(4)
        self.fold(6)
        time.sleep(0.5)

    def deplacement_object(self) -> None:
        """Catch cans and plank."""
        # Catch and raise cans and plank
        self.pickup_planck()
        # self.fold(9)
        time.sleep(0.1)

    def ready_to_approach_to_pickup(self) -> None:
        """Prepare servos for approaching a pickup point."""
        self.magnetize_all()
        self.set_stepper_driver_activation_state(13, enable_driver=False)
        self.elevator_ticks = 0
        time.sleep(0.5)
        self.deploy_all_pickup()
        # self.set_servo_angle(ARM_SERVO_PIN, angle=35, max_angle=270)
        # self.set_servo_angle(
        #     ARM_SERVO_PIN,
        #     angle=self.servos[ARM_SERVO_PIN].docking,  # pyright: ignore[reportAttributeAccessIssue] self.servos[ARM_SERVO_PIN] is ServoArm
        #     max_angle=270,
        # )
        # self.deploy(9)

    def pickup_planck(self) -> None:
        """Perform a sequence to grip the plank securely."""

        def _pickup() -> None:
            # self.deploy(9)
            # self.deploy(ARM_SERVO_PIN)
            time.sleep(0.3)
            # self.fold(9)

        _pickup()
        time.sleep(0.2)
        _pickup()

    def build(self) -> None:
        """Execute the full building routine."""
        self.fold(4)
        self.fold(6)
        time.sleep(1.5)
        self.go_to_top()
        time.sleep(1.5)
        self.set_servo_angle(pin=4, angle=160, max_angle=270)
        self.set_servo_angle(pin=6, angle=90, max_angle=270)
        time.sleep(2)
        self.elevator_drop_top()
        time.sleep(1)
        # self.deploy(9)
        time.sleep(1)
        self.demagnetize_all()
        time.sleep(1)
        self.fold(4)
        self.fold(6)
        # self.set_servo_angle(ARM_SERVO_PIN, angle=130, max_angle=270)
        time.sleep(0.1)

    def start_position(self) -> None:
        """Move actuators to the default start position."""
        self.set_stepper_driver_activation_state(13, enable_driver=False)
        self.elevator_ticks = 0
        # self.set_servo_angle(ARM_SERVO_PIN, angle=35, max_angle=270)
        time.sleep(0.5)
        self.deploy(0)
        self.deploy(2)
        self.fold(4)
        self.fold(6)

    def block_banner(self) -> None:
        """Block the banner by moving servos to holding positions."""
        self.set_stepper_driver_activation_state(13, enable_driver=False)
        self.elevator_ticks = 0
        # self.set_servo_angle(ARM_SERVO_PIN, angle=35, max_angle=270)
        # self.set_servo_angle(0, angle=105, max_angle=270)
        # self.set_servo_angle(2, angle=167, max_angle=270)
        self.set_servo_angle(0, angle=100, max_angle=270)
        self.set_servo_angle(2, angle=171, max_angle=270)

    def deplacement_position(self) -> None:
        """Put actuators in position for displacement."""
        time.sleep(0.5)
        self.demagnetize_all()
        self.fold(4)
        self.fold(6)
        self.deploy(2)
        self.deploy(0)
        self.go_to_bottom()
        time.sleep(2)
        # self.set_servo_angle(ARM_SERVO_PIN, angle=35, max_angle=270)
        # self.fold(9)

    # def build(self):
    #     self.fold(self.side_arms)
    #     self.stepper_step(
    #         self.stepper.top_steps - self.elevator_ticks, self.stepper.speed
    #     )
    #     self.deploy(self.side_arms)
    #     self.fold(self.end_servos)

    # def end_build(self):
    #     self.fold(self.side_arms + self.center)
    #     self.stepper_step(
    #         self.stepper.top_steps - self.elevator_ticks, self.stepper.speed
    #     )
