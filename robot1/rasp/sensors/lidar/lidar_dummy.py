# ====== Standard Library Imports ======
import numpy as np
import math

# ====== Third-party library imports ======
from loggerplusplus import Logger


# ====== Class Part ======
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

        self._logger.info("[LidarDummy] Initialized successfully.")

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

        self._logger.critical(
            f"[LidarDummy] Unit of angles not recognized [{unit}]!"
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

        self._logger.critical(
            f"[LidarDummy] Unit of distances not recognized [{unit}]!"
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

        self._logger.debug("[LidarDummy] Simulated realistic distances generated.")
        return distances * self.__distance_unit

    def scan_to_polars(self) -> np.ndarray:
        """
        Simulate a lidar scan and return fake polar coordinates.

        :return: numpy array of [angle, distance] pairs
        """
        distances = self.scan_to_distances()
        polars = np.column_stack((self.__polars_angles, distances))
        valid_polars = polars[polars[:, 1] > self._min_distance]

        self._logger.debug("[LidarDummy] Simulated polar coordinates generated.")
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
