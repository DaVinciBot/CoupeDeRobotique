"""GPIO-based front obstacle detector exposed through the lidar-like scan API."""

from __future__ import annotations

import math
from typing import TYPE_CHECKING

import numpy as np
from gpiozero import DigitalInputDevice
from gpiozero.exc import BadPinFactory

if TYPE_CHECKING:
    from loggerplusplus import Logger
    from numpy.typing import NDArray

GPIO_BACKEND_ERROR = (
    "GPIO backend unavailable. Install/enable a Raspberry Pi GPIO backend "
    "or run with access to /dev/gpiomem. On the robot, try running as root "
    "or adding the user to the gpio group, then restart the session."
)

DETECTOR_GPIO_PIN = 27
FAKE_OBSTACLE_DISTANCE_CM = 1.0
FAKE_CLEAR_DISTANCE_CM = 80.0
LOW_READS_TO_CONFIRM_OBSTACLE = 3
DEFAULT_TIMEOUT_S = 0.03


class UltrasonicDistanceSensor:
    """Read an active-low obstacle GPIO and expose the old lidar scan API."""

    def __init__(
        self,
        logger: Logger,
        trigger_pin: int,
        echo_pin: int,
        stop_distance: float = 20.0,
        timeout: float = DEFAULT_TIMEOUT_S,
    ) -> None:
        """Initialize the front obstacle detector.

        Args:
            logger (Logger): Logger instance for logging events.
            trigger_pin (int): Kept for compatibility; ignored.
            echo_pin (int): Kept for compatibility; ignored.
            stop_distance (float, optional):
                Compatibility value; fake obstacle distance stays very close.
            timeout (float, optional):
                Kept for compatibility; ignored.

        Raises:
            RuntimeError: If the Raspberry Pi GPIO backend is unavailable.
        """
        self._logger = logger
        self._stop_distance = stop_distance
        self._timeout = timeout
        self._last_distance: float | None = None
        self._low_reads_count = 0
        self.__is_connected = False

        try:
            self._detector = DigitalInputDevice(DETECTOR_GPIO_PIN, pull_up=False)
            self.__is_connected = True
        except BadPinFactory:
            raise RuntimeError(GPIO_BACKEND_ERROR) from None

        self._logger.info(
            "[SENSOR:Ultrasonic] Active-low GPIO detector initialized "
            f"(detector=GPIO{DETECTOR_GPIO_PIN}, obstacle=0, clear=1)",
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
            self._last_distance = self._read_fake_distance()
        return self.__is_connected

    def _read_fake_distance(self) -> float | None:
        """Read the active-low detector and convert it to a fake distance.

        Returns:
            float | None:
                A very close distance when GPIO27 is low, otherwise ``None``.
        """
        if int(self._detector.value) == 0:
            self._low_reads_count = 0
            self._last_distance = None
            return None

        self._low_reads_count += 1
        if self._low_reads_count < LOW_READS_TO_CONFIRM_OBSTACLE:
            self._last_distance = None
            return None

        self._last_distance = FAKE_OBSTACLE_DISTANCE_CM
        return self._last_distance

    def scan_to_distances(self) -> NDArray[np.float32]:
        """Read the detector and return a fake one-value distance array.

        Returns:
            NDArray[np.float32]: Very close distance for GPIO low, or empty for high.
        """
        distance = self._read_fake_distance()
        if distance is None:
            return np.empty(0, dtype=np.float32)
        return np.array([distance], dtype=np.float32)

    def scan_to_polars(self) -> NDArray[np.float32]:
        """Return fake lidar points for the current detector state.

        Empty scans keep the previous enemy position in the arena, so the clear
        state publishes far points instead of nothing.
        """
        distance = self._read_fake_distance()
        if distance is None or distance > self._stop_distance:
            # self._logger.info(
            #     "[SENSOR:Ultrasonic] No obstacle detected. Publishing fake clear scan.",
            # )
            return np.array(
                [
                    [0.0, FAKE_CLEAR_DISTANCE_CM],
                    [math.pi / 2, FAKE_CLEAR_DISTANCE_CM],
                    [-math.pi / 2, FAKE_CLEAR_DISTANCE_CM],
                    [math.pi, FAKE_CLEAR_DISTANCE_CM],
                ],
                dtype=np.float32,
            )

        self._logger.warning(
            f"[SENSOR:Ultrasonic] Obstacle detected at {distance:.1f} cm. "
            "Publishing fake obstacle scan.",
        )

        return np.array([[0.0, distance]], dtype=np.float32)

    @property
    def distances(self) -> NDArray[np.float32]:
        """Read the detector and return the current fake distance."""
        return self.scan_to_distances()

    @property
    def polars(self) -> NDArray[np.float32]:
        """Read the detector and return the current fake obstacle point."""
        return self.scan_to_polars()
