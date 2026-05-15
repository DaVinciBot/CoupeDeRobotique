"""HC-SR04 ultrasonic distance sensor used as a simple front obstacle detector."""

from __future__ import annotations

import time
from typing import TYPE_CHECKING

import numpy as np
from gpiozero import DigitalInputDevice, DigitalOutputDevice
from gpiozero.exc import BadPinFactory

if TYPE_CHECKING:
    from loggerplusplus import Logger
    from numpy.typing import NDArray

GPIO_BACKEND_ERROR = (
    "GPIO backend unavailable. Install/enable a Raspberry Pi GPIO backend "
    "or run with access to /dev/gpiomem. On the robot, try running as root "
    "or adding the user to the gpio group, then restart the session."
)

SPEED_OF_SOUND_CM_S = 34300.0
TRIGGER_PULSE_S = 0.00001
DEFAULT_TIMEOUT_S = 0.03


class UltrasonicDistanceSensor:
    """Read an HC-SR04 sensor and expose the same scan API as the old lidar."""

    def __init__(
        self,
        logger: Logger,
        trigger_pin: int,
        echo_pin: int,
        stop_distance: float = 20.0,
        timeout: float = DEFAULT_TIMEOUT_S,
    ) -> None:
        """Initialize the HC-SR04 front distance sensor.

        Args:
            logger (Logger): Logger instance for logging events.
            trigger_pin (int): BCM GPIO pin connected to the Trigger pin.
            echo_pin (int): BCM GPIO pin connected to the Echo pin.
            stop_distance (float, optional):
                Distance under which an obstacle is reported. Defaults to 20 cm.
            timeout (float, optional):
                Maximum wait time for the echo pulse. Defaults to 30 ms.

        Raises:
            RuntimeError: If the Raspberry Pi GPIO backend is unavailable.
        """
        self._logger = logger
        self._stop_distance = stop_distance
        self._timeout = timeout
        self._last_distance: float | None = None
        self.__is_connected = False

        try:
            self._trigger = DigitalOutputDevice(trigger_pin, initial_value=False)
            self._echo = DigitalInputDevice(echo_pin, pull_up=False)
            self.__is_connected = True
        except BadPinFactory:
            raise RuntimeError(GPIO_BACKEND_ERROR) from None

        self._logger.info(
            "[SENSOR:Ultrasonic] HC-SR04 initialized "
            f"(trigger=GPIO{trigger_pin}, echo=GPIO{echo_pin}, "
            f"stop={stop_distance:.1f}cm)",
        )

    def is_connected(self, *, force_check: bool = False) -> bool:
        """Check if the sensor is available.

        Args:
            force_check (bool, optional):
                If ``True``, performs one distance measurement. Defaults to ``False``.

        Returns:
            bool: ``True`` if the sensor is usable, ``False`` otherwise.
        """
        if force_check:
            self._last_distance = self._measure_distance()
        return self.__is_connected

    def _wait_for_echo_state(self, *, state: bool) -> float | None:
        """Wait until Echo reaches the requested state.

        Args:
            state (bool): Expected Echo pin state.

        Returns:
            float | None: Timestamp when the state is reached, or ``None`` on timeout.
        """
        deadline = time.perf_counter() + self._timeout
        while self._echo.is_active != state:
            if time.perf_counter() >= deadline:
                return None
        return time.perf_counter()

    def _measure_distance(self) -> float | None:
        """Measure the front distance.

        Returns:
            float | None: Measured distance in centimeters, or ``None`` on timeout.
        """
        self._trigger.off()
        time.sleep(0.000002)
        self._trigger.on()
        time.sleep(TRIGGER_PULSE_S)
        self._trigger.off()

        pulse_start = self._wait_for_echo_state(state=True)
        if pulse_start is None:
            self._logger.debug("[SENSOR:Ultrasonic] Echo start timeout")
            return None

        pulse_end = self._wait_for_echo_state(state=False)
        if pulse_end is None:
            self._logger.debug("[SENSOR:Ultrasonic] Echo end timeout")
            return None

        pulse_duration = pulse_end - pulse_start
        distance = pulse_duration * SPEED_OF_SOUND_CM_S / 2.0
        self._last_distance = distance
        return distance

    def scan_to_distances(self) -> NDArray[np.float32]:
        """Measure the front distance and return it as a one-value array.

        Returns:
            NDArray[np.float32]: One distance in centimeters, or an empty array.
        """
        distance = self._measure_distance()
        if distance is None:
            return np.empty(0, dtype=np.float32)
        return np.array([distance], dtype=np.float32)

    def scan_to_polars(self) -> NDArray[np.float32]:
        """Return a front obstacle point when it is inside the stop distance."""
        distance = self._measure_distance()
        if distance is None or distance > self._stop_distance:
            return np.empty((0, 2), dtype=np.float32)

        return np.array([[0.0, distance]], dtype=np.float32)

    @property
    def distances(self) -> NDArray[np.float32]:
        """Get the latest measured distance in centimeters."""
        if self._last_distance is None:
            return self.scan_to_distances()
        return np.array([self._last_distance], dtype=np.float32)

    @property
    def polars(self) -> NDArray[np.float32]:
        """Get the latest front obstacle point if it is inside the stop distance."""
        if self._last_distance is None or self._last_distance > self._stop_distance:
            return np.empty((0, 2), dtype=np.float32)
        return np.array([[0.0, self._last_distance]], dtype=np.float32)
