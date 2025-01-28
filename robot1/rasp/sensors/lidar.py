# Import from common
from logger import Logger, LogLevels

# External imports
from typing import TypeVar
import numpy as np
import threading
import time
import math

TLidar = TypeVar("TLidar", bound="pysicktim")


class Lidar:
    """
    This class is a wrapper for the lidar sensor.
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
        """
        Initialize the lidar object and the polars angles.
        It also tests the lidar connection.

        WARNING: The min & max angle have to be given in the trigonometric way and in degrees !

        :param logger: logger to log the lidar's events
        :param min_angle: the minimum angle of the lidar (max angle at left)
        :param max_angle: the maximum angle of the lidar (min angle at right)
        :param unit_angle: the unit of the angles (default: "deg")
        :param unit_distance: the unit of the distances (default: "cm")
        :param min_distance: the minimum distance to consider a distance as valid (default: 5.0 cm)
        :return:
        """
        self._logger = logger
        self.__min_angle = min_angle
        self.__max_angle = max_angle
        self.__angle_unit = self.__init_angles_unit(unit_angle)
        self.__distance_unit = self.__init_distances_unit(unit_distance)

        self._min_distance = min_distance
        self.__initialization_fail_refresh_rate = initialization_fail_refresh_rate

        self.__is_connected = False
        self.__lidar_obj = None
        self.__polars_angles = None
        self.__threading_init_lidar()

    """
        Private methods
    """

    def __init_lidar(self) -> TLidar:
        """
        Initialize the lidar object and test the connection.
        :return: the lidar object
        """
        try:
            import pysicktim as lidar

            if lidar is None:
                self._logger.log(
                    "[init_lidar] Lidar is not connected !", LogLevels.CRITICAL
                )
                raise ConnectionError("Lidar is not connected !")
            else:
                self._logger.log("[init_lidar] Lidar is connected !", LogLevels.INFO)

            # Test lidar connection by testing scan function
            lidar.scan()
            if lidar.scan.distances is None or lidar.scan.distances == []:
                self._logger.log(
                    "[init_lidar] Lidar doesn't work correctly", LogLevels.CRITICAL
                )
                raise ConnectionError("Lidar doesn't work correctly !")

            return lidar

        except Exception as error:
            self._logger.log(
                f"[init_lidar] Error while importing lidar [{error}]",
                LogLevels.CRITICAL,
            )
            raise ImportError(f"Error while importing lidar [{error}] !") from error

    def __threading_init_lidar(self):
        """
        Initialize the lidar in a thread. It will retry to initialize the lidar until is connected.
        :return:
        """

        def init():
            while not self.__is_connected:
                try:
                    self._logger.log(
                        "[init_lidar_in_thread] Try to initialize lidar ...",
                        LogLevels.DEBUG,
                    )
                    self.__lidar_obj = self.__init_lidar()
                    # Initialize the polars angles depends on the lidar number of measurements points
                    self.__polars_angles = self.__init_polars_angle(
                        self.__min_angle, self.__max_angle
                    )
                    self.__is_connected = True
                except Exception as error:
                    self._logger.log(
                        f"[init_lidar_in_thread] Error while initializing lidar [{error}] "
                        f"retry in {self.__initialization_fail_refresh_rate}s ...",
                        LogLevels.WARNING,
                    )
                    time.sleep(self.__initialization_fail_refresh_rate)

        thread = threading.Thread(target=init)
        thread.start()

    def __init_polars_angle(self, min_angle: float, max_angle: float) -> np.ndarray:
        """
        Initialize the polars angles array
        :param min_angle: the minimum angle of the lidar (max angle at left)
        :param max_angle: the maximum angle of the lidar (min angle at right)
        :return:
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
            self._logger.log("Error while initializing polars", LogLevels.CRITICAL)
            raise ValueError("Error while initializing polars !")

        return centered_polars

    def __init_angles_unit(self, unit: str) -> float:
        """
        Initialize the unit of the angles
        :param unit_angle: the unit of the angles
        :return:
        """
        if unit == "deg":
            return 1
        if unit == "rad":
            return math.pi / 180

        self._logger.log(
            f"unit of angles not recognized [{unit}] !", LogLevels.CRITICAL
        )
        raise ValueError(f"unit of angles not recognized [{unit}] !")

    def __init_distances_unit(self, unit: str) -> float:
        """
        Initialize the unit of the distances
        :param unit_distance: the unit of the distances
        :return:
        """
        if unit == "mm":
            return 1000
        if unit == "cm":
            return 100
        if unit == "m":
            return 1
        if unit == "inch":
            return 0.0254

        self._logger.log(
            f"unit of distances not recognized [{unit}] !", LogLevels.CRITICAL
        )
        raise ValueError(f"unit of distances not recognized [{unit}] !")

    def __scan(self):
        """
        Scan the environment with the lidar and store the distances.
        in the lidar object. If the scan fails, it will try to reconnect the lidar.
        """
        try:
            self.__lidar_obj.scan()
        except Exception as error:
            # LiDAR seems to be disconnected
            self._logger.log(
                f"Error while scanning, LiDAR is disconnected ? [{error}]",
                LogLevels.ERROR,
            )
            # Try to reconnect LiDAR if it was connected before
            if self.__is_connected:
                self.__is_connected = False
                self.__threading_init_lidar()

            raise Exception(f"Error while scanning, LiDAR is disconnected ? [{error}]")

    """
        Public methods and properties
    """

    def is_connected(self, force_check=False):
        if force_check:
            self.__scan()
        return self.__is_connected

    @property
    def distances(self) -> np.ndarray:
        """
        Get the distances from the last scan.
        It automatically converts the distances to the right unit.
        :return: the distances array
        """
        return (
                np.array(self.__lidar_obj.scan.distances, dtype=np.float32)
                * self.__distance_unit
        )

    @property
    def polars(self) -> np.ndarray:
        """
        Get the polars array.
        It automatically converts the angles to the right unit.
        :return: the polars array
        """
        return np.column_stack((self.__polars_angles, self.distances))

    def scan_to_distances(self) -> np.ndarray:
        """
        Scan the environment with the lidar and return the distances.
        :return: the distances array
        """
        self.__scan()
        return self.distances

    def scan_to_polars(self) -> np.ndarray:
        """
        Scan the environment with the lidar and return the polars array.
        :return: the polars array
        """
        self.__scan()
        return self.polars[self.polars[:, 1] > self._min_distance]


class LidarDummy:
    """
    A dummy Lidar class for testing purposes.
    Simulates the behavior of a real lidar sensor.
    """

    def __init__(
            self,
            logger: Logger,
            min_angle: float,
            max_angle: float,
            unit_angle: str = "deg",
            unit_distance: str = "cm",
            min_distance: float = 5.0,
            num_points: int = 360,
    ) -> None:
        """
        Initialize the dummy lidar object.

        :param logger: logger to log the lidar's events
        :param min_angle: the minimum angle of the lidar (max angle at left)
        :param max_angle: the maximum angle of the lidar (min angle at right)
        :param unit_angle: the unit of the angles (default: "deg")
        :param unit_distance: the unit of the distances (default: "cm")
        :param min_distance: the minimum distance to consider a distance as valid (default: 5.0 cm)
        :param num_points: number of points to simulate in a scan
        """
        self._logger = logger
        self.__min_angle = min_angle
        self.__max_angle = max_angle
        self.__angle_unit = self.__init_angles_unit(unit_angle)
        self.__distance_unit = self.__init_distances_unit(unit_distance)
        self._min_distance = min_distance
        self.__num_points = num_points

        self.__polars_angles = self.__init_polars_angle(min_angle, max_angle, num_points)
        self.__is_connected = True

        self._logger.log("[LidarDummy] Initialized successfully.", LogLevels.INFO)

    def __init_polars_angle(self, min_angle: float, max_angle: float, num_points: int) -> np.ndarray:
        """
        Initialize the polar angles array for the dummy lidar.

        :param min_angle: the minimum angle of the lidar (max angle at left)
        :param max_angle: the maximum angle of the lidar (min angle at right)
        :param num_points: the number of points in a scan
        :return: numpy array of angles
        """
        angle_step = abs(max_angle - min_angle) / num_points
        return np.array(
            [min_angle + i * angle_step for i in range(num_points)], dtype=np.float32
        )

    def __init_angles_unit(self, unit: str) -> float:
        """
        Initialize the unit of the angles.

        :param unit: the unit of the angles
        :return: conversion factor
        """
        if unit == "deg":
            return 1
        if unit == "rad":
            return math.pi / 180

        self._logger.log(
            f"[LidarDummy] Unit of angles not recognized [{unit}]!", LogLevels.CRITICAL
        )
        raise ValueError(f"Unit of angles not recognized [{unit}]!")

    def __init_distances_unit(self, unit: str) -> float:
        """
        Initialize the unit of the distances.

        :param unit: the unit of the distances
        :return: conversion factor
        """
        if unit == "mm":
            return 1000
        if unit == "cm":
            return 100
        if unit == "m":
            return 1
        if unit == "inch":
            return 0.0254

        self._logger.log(
            f"[LidarDummy] Unit of distances not recognized [{unit}]!", LogLevels.CRITICAL
        )
        raise ValueError(f"Unit of distances not recognized [{unit}]!")

    def scan_to_distances(self) -> np.ndarray:
        """
        Simulate a lidar scan and return fake distance data.

        :return: numpy array of distances
        """
        # Initialize an array of distances
        distances = np.full(self.__num_points, 5.0, dtype=np.float32)  # Default max range

        # Simulate obstacles as clusters of points
        num_obstacles = np.random.randint(3, 8)  # Number of obstacles
        for _ in range(num_obstacles):
            center_angle = np.random.uniform(0, self.__num_points)  # Random angle for obstacle
            obstacle_width = np.random.randint(5, 20)  # Width of obstacle in lidar points
            obstacle_distance = np.random.uniform(0.5, 4.0)  # Random distance for the obstacle

            # Assign distances to points within the obstacle
            start_idx = int(max(0, center_angle - obstacle_width // 2))
            end_idx = int(min(self.__num_points, center_angle + obstacle_width // 2))
            distances[start_idx:end_idx] = np.random.uniform(
                obstacle_distance - 0.1, obstacle_distance + 0.1, size=(end_idx - start_idx)
            ).astype(np.float32)

        # Add noise for realism
        distances += np.random.normal(0, 0.01, self.__num_points).astype(np.float32)
        distances = np.clip(distances, 0.1, 5.0)  # Ensure distances are within sensor range

        self._logger.log("[LidarDummy] Simulated realistic distances generated.", LogLevels.DEBUG)
        return distances * self.__distance_unit

    def scan_to_polars(self) -> np.ndarray:
        """
        Simulate a lidar scan and return fake polar coordinates.

        :return: numpy array of [angle, distance] pairs
        """
        distances = self.scan_to_distances()
        polars = np.column_stack((self.__polars_angles, distances))
        valid_polars = polars[polars[:, 1] > self._min_distance]

        self._logger.log("[LidarDummy] Simulated polar coordinates generated.", LogLevels.DEBUG)
        return valid_polars

    def is_connected(self) -> bool:
        """
        Check if the dummy lidar is connected.

        :return: connection status
        """
        return self.__is_connected

    @property
    def distances(self) -> np.ndarray:
        """
        Get the last simulated distances.

        :return: numpy array of distances
        """
        return self.scan_to_distances()

    @property
    def polars(self) -> np.ndarray:
        """
        Get the last simulated polar coordinates.

        :return: numpy array of [angle, distance] pairs
        """
        return self.scan_to_polars()
