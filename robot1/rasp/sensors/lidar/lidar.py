import math
import threading
import time
from typing import TYPE_CHECKING, TypeVar

import numpy as np
from loggerplusplus import Logger
from numpy.typing import NDArray

if TYPE_CHECKING:
    import pysicktim

TLidar = TypeVar("TLidar", bound="pysicktim")


class Lidar:
    """This class is a wrapper for the lidar sensor.

    * The angles are in degrees (considering the sense in the trigonometric way).
            -> 0° is the front of the robot
            -> 90° is the left of the robot
            -> -90° is the right of the robot
    * The distances are in centimeters.
    * the unities of angles and distances can be changed by changing the default values of the _init_ parameters.
    * The lidar is a SICK TIM 571.
    * The angle and distance are stored in a numpy array (type float32).

    -> The default lidar distance unit is m.
    """

    def __init__(
        self,
        logger: Logger,
        min_angle: float,
        max_angle: float,
        unit_angle: str = "deg",
        unit_distance: str = "cm",
        min_distance: float = 5.0,
        initialization_fail_refresh_rate: float = 0.5,
    ) -> None:
        """Initialize the lidar object and the polars angles.

        It also tests the lidar connection.

        WARNING: The min & max angle have to be given in the trigonometric way and in degrees !

        Args:
            logger (Logger): Logger instance for logging events.
            min_angle (float): Minimum angle of the lidar (max angle at left).
            max_angle (float): Maximum angle of the lidar (min angle at right).
            unit_angle (str, optional): Unit of the angles. Defaults to "deg".
            unit_distance (str, optional): Unit of the distances. Defaults to "cm".
            min_distance (float, optional): Minimum distance to consider a distance as valid. Defaults to 5.0.
            initialization_fail_refresh_rate (float, optional): Refresh rate for initialization failures. Defaults to 0.5.
        """
        self._logger = logger
        self.__min_angle = min_angle
        self.__max_angle = max_angle
        self.__angle_unit = self.__init_angles_unit(unit_angle)
        self.__distance_unit = self.__init_distances_unit(unit_distance)

        self._min_distance = min_distance
        self.__initialization_fail_refresh_rate = initialization_fail_refresh_rate

        self.__is_connected = False
        self.__lidar_obj: TLidar | None = None
        self.__polars_angles = None
        self.__threading_init_lidar()

    """
        Private methods
    """

    def __init_lidar(self) -> TLidar:
        """Initialize the lidar object and test the connection.

        Returns:
            TLidar: the lidar object

        Raises:
            ConnectionError: If the lidar is not connected or does not work correctly.
            ImportError: If the lidar module cannot be imported.
        """
        try:
            import pysicktim as lidar

            if lidar is None:
                self._logger.critical("[init_lidar] Lidar is not connected !")
                raise ConnectionError("Lidar is not connected !")
            self._logger.info("[init_lidar] Lidar is connected !")

            # Test lidar connection by testing scan function
            lidar.scan()
            if lidar.scan.distances is None or lidar.scan.distances == []:
                self._logger.critical("[init_lidar] Lidar doesn't work correctly")
                raise ConnectionError("Lidar doesn't work correctly !")

            return lidar

        except Exception as error:
            self._logger.critical(f"[init_lidar] Error while importing lidar [{error}]")
            raise ImportError(f"Error while importing lidar [{error}] !") from error

    def __threading_init_lidar(self) -> None:
        """Initialize the lidar in a thread. It will retry to initialize the lidar until is connected."""

        def init() -> None:
            while not self.__is_connected:
                try:
                    self._logger.debug(
                        "[init_lidar_in_thread] Try to initialize lidar ...",
                    )
                    self.__lidar_obj = self.__init_lidar()
                    # Initialize the polars angles depends on the lidar number of measurements points
                    self.__polars_angles = self.__init_polars_angle(
                        self.__min_angle,
                        self.__max_angle,
                    )
                    self.__is_connected = True
                except Exception as error:
                    self._logger.warning(
                        f"[init_lidar_in_thread] Error while initializing lidar [{error}] "
                        f"retry in {self.__initialization_fail_refresh_rate}s ...",
                    )
                    time.sleep(self.__initialization_fail_refresh_rate)

        thread = threading.Thread(target=init)
        thread.start()

    def __init_polars_angle(self, min_angle: float, max_angle: float) -> np.ndarray:
        """Initialize the polar angles array.

        Args:
            min_angle (float): Minimum angle of the lidar (max angle at left).
            max_angle (float): Maximum angle of the lidar (min angle at right).

        Returns:
            np.ndarray: numpy array of angles centered around 0°.

        Raises:
            ValueError: If the polars array cannot be initialized.
        """
        n = len(self.distances)  # Number of distances
        if n == 0:
            self.__scan()
            n = len(self.distances)  # Number of distances

        angle_step = abs(max_angle - min_angle) / n

        # Init the polars array with zeros, then fill it with angles centered, so that the "front" of the lidar is 0
        centered_polars = np.zeros(n, dtype=np.float32)
        for i in range(n):
            centered_polars[i] = -((max_angle - min_angle) / 2) + i * angle_step

        if centered_polars.size == 0:
            self._logger.critical("Error while initializing polars")
            raise ValueError("Error while initializing polars !")

        return centered_polars

    def __init_angles_unit(self, unit: str) -> float:
        """Initialize the unit of the angles.

        Args:
            unit (str): The unit of the angles.

        Returns:
            float: conversion factor for the angles

        Raises:
            ValueError: If the unit is not recognized.
        """
        if unit == "deg":
            return 1
        if unit == "rad":
            return math.pi / 180

        self._logger.critical(f"unit of angles not recognized [{unit}] !")
        raise ValueError(f"unit of angles not recognized [{unit}] !")

    def __init_distances_unit(self, unit: str) -> float:
        """Initialize the unit of the distances.

        Args:
            unit (str): The unit of the distances.

        Returns:
            float: conversion factor for the distances

        Raises:
            ValueError: If the unit is not recognized.
        """
        if unit == "mm":
            return 1000
        if unit == "cm":
            return 100
        if unit == "m":
            return 1
        if unit == "inch":
            return 0.0254

        self._logger.critical(f"unit of distances not recognized [{unit}] !")
        raise ValueError(f"unit of distances not recognized [{unit}] !")

    def __scan(self) -> None:
        """Scan the environment with the lidar and store the distances in the lidar object.

        If the scan fails, it will try to reconnect the lidar.

        Raises:
            Exception: If the lidar is disconnected or if the scan fails.
        """
        try:
            self.__lidar_obj.scan()
        except Exception as error:
            # LiDAR seems to be disconnected
            self._logger.error(
                f"Error while scanning, LiDAR is disconnected ? [{error}]",
            )
            # Try to reconnect LiDAR if it was connected before
            if self.__is_connected:
                self.__is_connected = False
                self.__threading_init_lidar()

            raise Exception(f"Error while scanning, LiDAR is disconnected ? [{error}]")

    """
        Public methods and properties
    """

    def is_connected(self, force_check: bool = False) -> bool:
        """Check if the lidar is connected.

        Args:
            force_check (bool, optional): Force a check of the connection status. Defaults to `False`.

        Returns:
            bool: `True` if the lidar is connected, `False` otherwise.
        """
        if force_check:
            self.__scan()
        return self.__is_connected

    @property
    def distances(self) -> NDArray[np.float32]:
        """Get the distances from the last scan.

        It automatically converts the distances to the right unit.

        Returns:
            NDArray[np.float32]: the distances array
        """
        return (
            np.array(self.__lidar_obj.scan.distances, dtype=np.float32)
            * self.__distance_unit
        )

    @property
    def polars(self) -> NDArray[np.float32]:
        """Get the polars array.

        It automatically converts the angles to the right unit.

        Returns:
            NDArray[np.float32]: the polars array
        """
        return np.column_stack((self.__polars_angles, self.distances))

    def scan_to_distances(self) -> NDArray[np.float32]:
        """Scan the environment with the lidar and return the distances.

        Returns:
            NDArray[np.float32]: the distances array
        """
        self.__scan()
        return self.distances

    def scan_to_polars(self) -> NDArray[np.float32]:
        """Scan the environment with the lidar and return the polars array.

        Returns:
            NDArray[np.float32]: the polars array
        """
        self.__scan()
        return self.polars[self.polars[:, 1] > self._min_distance]
