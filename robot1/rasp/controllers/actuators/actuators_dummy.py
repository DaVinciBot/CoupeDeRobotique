from config_loader import CONFIG

# ====== Third-party library imports ======
from loggerplusplus import Logger, log

# ====== Local Library Imports ======
from teensy import GPIOComTeensy, ActuatorType


# ====== Class Part ======
class ActuatorsDummy(GPIOComTeensy):
    def __init__(
        self,
        logger: Logger,
        serial_number=CONFIG.ACTUATOR_TEENSY_SER,
        vid=CONFIG.TEENSY_VID,
        pid=CONFIG.TEENSY_PID,
        baudrate=CONFIG.TEENSY_BAUDRATE,
        enable_crc=CONFIG.TEENSY_CRC,
    ):
        # Initialize the parent-GPIOComTeensy class
        super().__init__(logger, serial_number, vid, pid, baudrate, enable_crc, True)

        # Admit that default elevator position is at the bottom
        self.elevator_ticks: int = 0
        self.switches_states: dict[int:bool] = {}

    def __str__(self) -> str:
        return self.__class__.__name__

    @log("DummyActuators")
    def stepper_step(self, steps: int, speed: int) -> None:
        """
        Logs the action of moving the stepper motor a specified number of steps.

        Args:
            steps (int): The number of steps to move the motor.
            speed (int): The speed at which to move the motor.

        Returns:
            None
        """
        # Update elevator theoretical steps
        self.elevator_ticks += steps

        # Log the action instead of sending a message
        self.logger.info(
            f"DummyActuators: Simulating stepper motor move: steps={steps}, speed={speed}"
        )

    @log("DummyActuators")
    def set_servo_angle(
        self,
        pin: int,
        angle: int,
        min_angle: int = 0,
        max_angle: int = 180,
        detach=False,
        detach_delay=1000,
    ) -> None:
        """
        Logs the action of setting the angle of the servo at the given pin.

        Args:
            pin (int): The pin-number of the servo.
            angle (int): The angle to set for the servo.
            min_angle (int, optional): The minimum angle allowed for the servo. Defaults to 0.
            max_angle (int, optional): The maximum angle allowed for the servo. Defaults to 180.
            detach (bool, optional): Whether to detach the servo after setting the angle. Defaults to False.
            detach_delay (int, optional): The time in milliseconds to keep the servo detached. Defaults to 1000.
             Ignored if detach is False.
        """
        if min_angle <= angle <= max_angle:
            if detach:
                self.logger.info(
                    f"DummyActuators: Simulating setting servo angle with detach: pin={pin}, angle={angle}, "
                    f"detach_delay={detach_delay}ms"
                )
            else:
                if not self.gpio_manager.is_declared_gpio(pin):
                    self.gpio_manager.add_gpio(pin, ActuatorType.SERVO)
                    self.logger.info(f"Pin {pin} added as a servo pin")
                elif not self.gpio_manager.is_valid_gpio(pin, ActuatorType.SERVO):
                    self.logger.error(
                        f"Pin {pin} is not a valid servo pin because it is registered as a "
                        f"{str(self.gpio_manager.get_type_gpio(pin))}"
                    )
                    return
                self.logger.info(
                    f"DummyActuators: Simulating setting servo angle: pin={pin}, angle={angle}"
                )
        else:
            self.logger.error(
                f"You tried to write {angle}° on pin {pin}, whereas the angle "
                f"must be between {min_angle} and {max_angle}°"
            )

    @log("DummyActuators")
    def attach_switch(self, pin: int) -> None:
        """
        Logs the action of attaching a switch to the given pin.

        Args:
            pin (int): The pin-number to attach the switch to.

        Returns:
            None
        """
        self.logger.info(f"DummyActuators: Simulating attaching switch to pin {pin}")
