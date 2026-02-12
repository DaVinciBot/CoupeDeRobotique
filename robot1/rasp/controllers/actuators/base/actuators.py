"""Base classes for Teensy-driven actuators."""

from __future__ import annotations

import struct
import time
from typing import TYPE_CHECKING, override

from loggerplusplus import log

from a_config_loader import CONFIG
from teensy import ActuatorType, GPIOComTeensy
from usb_com.python import Messages

if TYPE_CHECKING:
    from loggerplusplus import Logger

I2C_DELAY = 0.03


class Actuators(
    GPIOComTeensy,
):
    """Base class for actuators.

    This class is used to manage the actuators of the robot.
    """

    # TODO : move to common and handle config properly, not the prority yet
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
        """Initialize the Actuators class.

        Args:
            logger (Logger): The logger instance for logging.
            serial_number (int, optional):
                The serial number of the Teensy. Defaults to CONFIG.ACTUATOR_TEENSY_SER.
            vid (int, optional):
                The vendor ID of the Teensy. Defaults to CONFIG.TEENSY_VID.
            pid (int, optional):
                The product ID of the Teensy. Defaults to CONFIG.TEENSY_PID.
            baudrate (int, optional):
                The baud rate for serial communication.
                Defaults to CONFIG.TEENSY_BAUDRATE.
            enable_crc (bool, optional):
                Whether to enable CRC checks. Defaults to CONFIG.TEENSY_CRC.
            enable_dummy (bool, optional):
                Whether to enable dummy mode. Defaults to CONFIG.ACTUATORS_DUMMY.
        """
        # Initialize the parent-GPIOComTeensy class
        super().__init__(
            logger,
            serial_number,
            vid,
            pid,
            baudrate,
            enable_crc=enable_crc,
            enable_dummy=enable_dummy,
        )

        # Admit that default elevator position is at the bottom
        self.elevator_ticks: int = 0
        self.switches_states: dict[int, bool] = {}
        self.t_set_servo_angle_i2c: float = 0.0

        # Register message handlers
        self.add_callback(self.rcv_print, Messages.PRINT.value)
        self.add_callback(self.rcv_unknown_msg, Messages.UNKNOWN_MSG_TYPE.value)
        self.add_callback(
            self.rcv_switch_state_return,
            Messages.SWITCH_STATE_RETURN.value,
        )

    @override
    def __str__(self) -> str:
        """Return class name for debugging.

        Returns:
            str: The class name.
        """
        return self.__class__.__name__

    # region ====== Message Receiving Handlers ======

    def rcv_print(self, msg: bytes) -> None:
        """Handles PRINT messages from the Teensy.

        Args:
            msg (bytes): The received message bytes.
        """
        self._logger.debug(
            f"[CTRL:ACT:Teensy] {msg.decode('ascii', errors='ignore')}",
        )

    def rcv_unknown_msg(self, msg: bytes) -> None:
        """Handles unknown messages from the Teensy.

        Logs a warning indicating that the message type is not recognized.

        Args:
            msg (bytes): The received message bytes.
        """
        self._logger.warning(f"[CTRL:ACT:Teensy] Unknown message type: {msg.hex()}")

    def rcv_switch_state_return(self, msg: bytes) -> None:
        """Handles SWITCH_STATE_RETURN messages from the Teensy.

        Args:
            msg (bytes): The received message bytes.
        """
        self._logger.debug(f"[CTRL:ACT] Switch state: {msg.hex()}")
        # Decode the message
        pin: int = struct.unpack("<B", msg[0:1])[0]
        state: bool = struct.unpack("<?", msg[1:2])[0]
        # Save the switch state
        self.switches_states[pin] = state

    # endregion

    # region ====== Message Sending Methods ======

    @log("Actuators")
    def set_stepper_driver_activation_state(
        self,
        pin_enable: int,
        *,
        enable_driver: bool,
    ) -> None:
        """Sets the activation state of a stepper motor driver through its enable pin.

        Note:
            The enable pin is active LOW,
            meaning True will output LOW to enable the driver

        Args:
            pin_enable (int): The pin number connected to the driver's enable input
            enable_driver (bool):
                ``True`` to enable the driver, ``False`` to disable it.
        """
        msg = (
            Messages.SET_STEPPER_DRIVER_ACTIVATION_STATE.to_bytes()
            + struct.pack("<B", pin_enable)
            + struct.pack("<?", not enable_driver)  # enable driver is active low
        )
        self.send_bytes(msg)

    @log("Actuators")
    def stepper_step(
        self,
        steps: int,
        speed: int,
        *,
        disable_driver: bool = True,
    ) -> None:
        """Moves the stepper motor a specified number of steps.

        Note that the number of motor pin can change depending on the motor.

        Args:
            steps (int): The number of steps to move the motor.
            speed (int): The speed at which to move the motor.
            disable_driver (bool, optional):
                Whether to disable the driver after the movement. Defaults to ``True``.
        """
        # Update elevator theorical steps
        self.elevator_ticks += steps

        # WARNING: pin_driver is also defined in the C++ code
        # It must receive a HIGH at startup to avoid overheating
        pin_dir = 15
        pin_step = 14
        pin_enable_driver = 13

        msg = (
            Messages.STEPPER_STEP.to_bytes()
            + struct.pack("<i", abs(steps))
            + struct.pack("<?", (steps <= 0))
            + struct.pack("<i", speed)
            + struct.pack("<B", pin_dir)
            + struct.pack("<B", pin_step)
            + struct.pack("<B", pin_enable_driver)
        )
        # Send the composed message to the Teensy
        # https://docs.python.org/3/library/struct.html#format-characters
        self.send_bytes(msg)
        # time.sleep(0.01)  # Wait for the Teensy to process the message

        if disable_driver:
            # Disable the driver after the movement
            self.set_stepper_driver_activation_state(
                pin_enable=pin_enable_driver,
                enable_driver=False,
            )
        else:
            # Enable the driver after the movement
            self.set_stepper_driver_activation_state(
                pin_enable=pin_enable_driver,
                enable_driver=True,
            )

    @log("Actuators")
    def set_servo_angle(
        self,
        pin: int,
        angle: int,
        min_angle: int = 0,
        max_angle: int = 180,
        *,
        detach: bool = False,
        # If True, the servo will detach after setting the angle,
        # DO NOT USE DETACH = TRUE AND DETACH = FALSE ON THE SAME SERVO
        detach_delay: int = 1000,
        use_i2c: bool = True,
    ) -> None:
        """Set the angle of the servo at the given pin.

        Args:
            pin (int): The pin-number of the servo.
            angle (int): The angle to set for the servo.
            min_angle (int, optional):
                The minimum angle allowed for the servo. Defaults to 0.
            max_angle (int, optional):
                The maximum angle allowed for the servo. Defaults to 180.
            detach (bool, optional):
                Whether to detach the servo after setting the angle.
                Defaults to ``False``.
            detach_delay (int, optional):
                The time in milliseconds to keep the servo detached. Defaults to 1000.
             Ignored if detach is ``False``.
            use_i2c (bool, optional):
                Whether to use I2C communication for the servo. Defaults to ``True``.
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
                    self._logger.info(f"[CTRL:ACT] Pin {pin} added as servo")
                elif not self.gpio_manager.is_valid_gpio(pin, ActuatorType.SERVO):
                    self._logger.error(
                        f"[CTRL:ACT] Pin {pin} invalid - registered as "
                        f"{self.gpio_manager.get_type_gpio(pin)!s}",
                    )
                    return
                if use_i2c:  # prevent I2C overload
                    # Without this delay, servos took wrong angles when called too fast
                    t = time.time()
                    if t - self.t_set_servo_angle_i2c < I2C_DELAY:
                        time.sleep(I2C_DELAY - (t - self.t_set_servo_angle_i2c))
                        self.t_set_servo_angle_i2c = t
                msg = (
                    (
                        Messages.SET_SERVO_ANGLE_I2C.to_bytes()
                        if use_i2c
                        else Messages.SET_SERVO_ANGLE.to_bytes()
                    )
                    + struct.pack("<B", pin)
                    + struct.pack("<H", angle)
                    + struct.pack("<H", max_angle)
                )
                # https://docs.python.org/3/library/struct.html#format-characters
                self.send_bytes(msg)

        else:
            self._logger.error(
                f"[CTRL:ACT] Angle {angle}° out of range [{min_angle}-{max_angle}°] "
                f"for pin {pin}",
            )

    @log("Actuators")
    def attach_switch(self, pin: int) -> None:
        """Attach a switch to the specified GPIO ``pin``.

        Args:
            pin (int): The GPIO pin number to which the switch is connected.
        """
        msg = Messages.ATTACH_SWITCH.to_bytes() + struct.pack("<B", pin)
        self.send_bytes(msg)

    # endregion
