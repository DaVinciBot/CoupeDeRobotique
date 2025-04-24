from config_loader import CONFIG

# ====== Standard Library Imports ======
import struct

# ====== Third-party library imports ======
from loggerplusplus import Logger, log

# ====== Local Library Imports ======
from teensy import GPIOComTeensy, ActuatorType
from usb_com.python import Messages


# ====== Class Part ======
class Actuators(
    GPIOComTeensy
):  # TODO : move to common and handle config properly, not the prority yet
    def __init__(
        self,
        logger: Logger,
        serial_number=CONFIG.ACTUATOR_TEENSY_SER,
        vid=CONFIG.TEENSY_VID,
        pid=CONFIG.TEENSY_PID,
        baudrate=CONFIG.TEENSY_BAUDRATE,
        enable_crc=CONFIG.TEENSY_CRC,
        enable_dummy=CONFIG.TEENSY_DUMMY,
    ):
        # Initialize the parent-GPIOComTeensy class
        super().__init__(
            logger, serial_number, vid, pid, baudrate, enable_crc, enable_dummy
        )

        # Admit that default elevator position is at the bottom
        self.elevator_ticks: int = 0
        self.switches_states: dict[int:bool] = {}

        """
        This is used to match a handling function to a message type.
        add_callback can also be used.
        """
        # Register message handlers
        self.add_callback(self.rcv_print, Messages.PRINT.value)
        self.add_callback(self.rcv_unknown_msg, Messages.UNKNOWN_MSG_TYPE.value)
        self.add_callback(
            self.rcv_switch_state_return, Messages.SWITCH_STATE_RETURN.value
        )

    def __str__(self) -> str:
        return self.__class__.__name__

    ####################################
    # Message Receiving Handlers       #
    ####################################
    def rcv_print(self, msg: bytes):
        """
        Handles PRINT messages from the Teensy.

        Args:
            msg (bytes): The received message bytes.
        """
        self.logger.info(
            "Teensy Actuators says: " + msg.decode("ascii", errors="ignore")
        )

    def rcv_unknown_msg(self, msg: bytes):
        """
        Handles unknown messages from the Teensy.

        Logs a warning indicating that the message type is not recognized.

        Args:
            msg (bytes): The received message bytes.
        """
        self.logger.warning(f"Teensy Actuators does not know the message {msg.hex()}")

    def rcv_switch_state_return(self, msg: bytes):
        """
        Handles SWITCH_STATE_RETURN messages from the Teensy.

        Args:
            msg (bytes): The received message bytes.
        """
        self.logger.info(f"Switch state: {msg.hex()}")
        # Decode the message
        pin: int = struct.unpack("<B", msg[0:1])[0]
        state: bool = struct.unpack("<?", msg[1:2])[0]
        # Save the switch state
        self.switches_states[pin] = state

    ####################################
    # Message Sending Methods          #
    ####################################

    @log("Actuators")
    def stepper_step(self, steps: int, speed: int) -> None:
        """
        Moves the stepper motor a specified number of steps.
        Note that the number of motor pin can change depending on the motor.

        Args:
            steps (int): The number of steps to move the motor.
            speed (int): The speed at which to move the motor.

        Returns:
            None
        """
        # Update elevator theorical steps
        self.elevator_ticks += steps

        # WARNING: pin_driver is also defined in the C++ code,
        # because it needs to receive a HIGH from the beginning, or it will start heating up
        pin_dir = 13
        pin_step = 14
        pin_driver = 15

        msg = (
            Messages.STEPPER_STEP.to_bytes()
            + struct.pack("<i", abs(steps))
            + struct.pack("<?", (steps >= 0))
            + struct.pack("<i", speed)
            + struct.pack("<B", pin_dir)
            + struct.pack("<B", pin_step)
            + struct.pack("<B", pin_driver)
        )
        # Send the composed message to the Teensy
        # https://docs.python.org/3/library/struct.html#format-characters
        self.send_bytes(msg)

    @log("Actuators")
    def set_servo_angle(
        self,
        pin: int,
        angle: int,
        min_angle: int = 0,
        max_angle: int = 180,
        detach=False,
        # If True, the servo will detach after setting the angle,
        # DO NOT USE DETACH = TRUE AND DETACH = FALSE ON THE SAME SERVO
        detach_delay=1000,
        use_I2C=True,
    ) -> None:
        """Set the angle of the servo at the given pin.

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
                msg = (
                    Messages.SET_SERVO_ANGLE_DETACH.to_bytes()
                    + struct.pack("<B", pin)
                    + struct.pack("<H", angle)
                    + struct.pack("<H", max_angle)
                    + struct.pack("<i", detach_delay)
                )
                self.send_bytes(msg)
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
                msg = (
                    (
                        Messages.SET_SERVO_ANGLE_I2C.to_bytes()
                        if use_I2C
                        else Messages.SET_SERVO_ANGLE.to_bytes()
                    )
                    + struct.pack("<B", pin)
                    + struct.pack("<H", angle)
                    + struct.pack("<H", max_angle)
                )
                # https://docs.python.org/3/library/struct.html#format-characters
                self.send_bytes(msg)

        else:
            self.logger.error(
                f"You tried to write {angle}° on pin {pin}, whereas the angle "
                f"must be between {min_angle} and {max_angle}°"
            )

    @log("Actuators")
    def attach_switch(self, pin: int) -> None:
        msg = Messages.ATTACH_SWITCH.to_bytes() + struct.pack("<B", pin)
        self.send_bytes(msg)
