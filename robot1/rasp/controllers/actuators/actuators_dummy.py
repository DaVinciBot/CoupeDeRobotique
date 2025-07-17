from config_loader import CONFIG
from loggerplusplus import Logger, log

from controllers.actuators.actuators_show import ActuatorsShow


class ActuatorsShowDummy(ActuatorsShow):
    """Dummy version of ActuatorsShow that simulates all actuator and stepper actions via logging,
    without any real hardware interaction.
    """

    def __init__(
        self,
        logger: Logger,
        serial_number: int = CONFIG.ACTUATOR_TEENSY_SER,
        vid: int = CONFIG.TEENSY_VID,
        pid: int = CONFIG.TEENSY_PID,
        baudrate: int = CONFIG.TEENSY_BAUDRATE,
        enable_crc: bool = CONFIG.TEENSY_CRC,
    ) -> None:
        """Initialize the dummy actuators wrapper.

        Args:
            logger (Logger): Logger used for output.
            serial_number (int): Teensy serial number.
            vid (int): USB vendor ID.
            pid (int): USB product ID.
            baudrate (int): Serial communication baud rate.
            enable_crc (bool): Whether CRC is enabled.
        """
        # Initialize parent with a dummy flag to bypass hardware
        super().__init__(
            logger,
            serial_number,
            vid,
            pid,
            baudrate,
            enable_crc,
            True,  # dummy hardware flag
        )
        # Default elevator position at bottom
        self.elevator_ticks: int = 0

    def __str__(self) -> str:
        return self.__class__.__name__

    @log("DummyActuatorsShow")
    def stepper_step(
        self,
        steps: int,
        speed: int,
        disable_driver: bool = False,
    ) -> None:
        """Simulate moving the stepper motor.

        Args:
            steps (int): Number of steps to move.
            speed (int): Speed of the movement.
            disable_driver (bool): Whether to disable the driver afterwards.
        """
        self.elevator_ticks += steps
        self.logger.info(
            f"DummyActuatorsShow: Simulating stepper move: steps={steps},"
            f" speed={speed}, disable_driver={disable_driver}",
        )

    @log("DummyActuatorsShow")
    def set_servo_angle(
        self,
        pin: int,
        angle: int,
        max_angle: int = 180,
        detach: bool = False,
        detach_delay: int = 1000,
    ) -> None:
        """Simulate setting the servo angle.

        Args:
            pin (int): Servo pin number.
            angle (int): Desired angle in degrees.
            max_angle (int): Maximum allowed angle.
            detach (bool): Detach the servo after moving if ``True``.
            detach_delay (int): Delay before detaching in milliseconds.
        """
        # Check if pin is valid; if not, log and return
        if not self._check_pin(pin):
            return

        # Retrieve minimum angle from config if available
        servo = self.servos.get(pin)
        # Default min_angle from deploy and fold
        min_angle = min(
            getattr(servo, "deploy_angle", 0),
            getattr(servo, "fold_angle", 0),
        )

        # Pin-specific exceptions
        pin_exceptions = {
            8: getattr(servo, "docking_angle", 0),
            6: 90,
        }

        min_angle = pin_exceptions.get(pin, min_angle)

        if min_angle <= angle <= max_angle:
            if detach:
                self.logger.info(
                    f"DummyActuatorsShow: Simulating set_servo_angle with detach:"
                    f" pin={pin}, angle={angle}, detach_delay={detach_delay}ms",
                )
            else:
                self.logger.info(
                    f"DummyActuatorsShow: Simulating set_servo_angle: pin={pin}, angle={angle}",
                )
        else:
            self.logger.error(
                f"DummyActuatorsShow: Angle {angle}° out of range [{min_angle},{max_angle}] for pin {pin}",
            )
