"""Simulated LiDAR readings for development and testing."""

from __future__ import annotations

import math
from typing import TYPE_CHECKING

import numpy as np

if TYPE_CHECKING:
    from loggerplusplus import Logger


class LidarDummy:
    """A dummy Lidar class for testing purposes.

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
        """Initialize the dummy lidar object.

        Args:
            logger (Logger): Logger instance for logging events.
            min_angle (float): Minimum angle of the lidar (max angle at left).
            max_angle (float): Maximum angle of the lidar (min angle at right).
            unit_angle (str, optional): Unit of the angles. Defaults to "deg".
            unit_distance (str, optional): Unit of the distances. Defaults to "cm".
            min_distance (float, optional):
                Minimum distance to consider a distance as valid. Defaults to 5.0.
            num_points (int, optional):
                Number of points to simulate in a scan. Defaults to 360.

        """
        self._logger = logger
        self.__min_angle = min_angle
        self.__max_angle = max_angle
        self.__angle_unit = self.__init_angles_unit(unit_angle)
        self.__distance_unit = self.__init_distances_unit(unit_distance)
        self._min_distance = min_distance
        self.__num_points = num_points

        self.__polars_angles = self.__init_polars_angle(
            min_angle,
            max_angle,
            num_points,
        )
        self.__is_connected = True

        self._logger.info("[LidarDummy] Initialized successfully.")

    @staticmethod
    def __init_polars_angle(
        min_angle: float,
        max_angle: float,
        num_points: int,
    ) -> np.ndarray:
        """Initialize the polar angles array for the dummy lidar.

        Args:
            min_angle (float): Minimum angle of the lidar (max angle at left).
            max_angle (float): Maximum angle of the lidar (min angle at right).
            num_points (int): Number of points to simulate in a scan.

        Returns:
            np.ndarray: Array of angles.

        """
        angle_step = abs(max_angle - min_angle) / num_points
        return np.array(
            [min_angle + i * angle_step for i in range(num_points)],
            dtype=np.float32,
        )

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

        self._logger.critical(f"[LidarDummy] Unit of angles not recognized [{unit}]!")
        msg = f"Unit of angles not recognized [{unit}]!"
        raise ValueError(msg)

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

        self._logger.critical(
            f"[LidarDummy] Unit of distances not recognized [{unit}]!",
        )
        msg = f"Unit of distances not recognized [{unit}]!"
        raise ValueError(msg)

    def scan_to_distances(self) -> np.ndarray:
        """Simulate a lidar scan and return fake distance data.

        Returns:
            np.ndarray: numpy array of distances

        """
        # Initialize an array of distances
        distances = np.full(
            self.__num_points,
            5.0,
            dtype=np.float32,
        )  # Default max range

        # Simulate obstacles as clusters of points
        num_obstacles = np.random.default_rng().integers(3, 8)  # Number of obstacles
        for _ in range(num_obstacles):
            center_angle = np.random.default_rng().uniform(
                0,
                self.__num_points,
            )  # Random angle for obstacle
            obstacle_width = np.random.default_rng().integers(
                5,
                20,
            )  # Width of obstacle in lidar points
            obstacle_distance = np.random.default_rng().uniform(
                0.5,
                4.0,
            )  # Random distance for the obstacle

            # Assign distances to points within the obstacle
            start_idx = int(max(0, center_angle - obstacle_width // 2))
            end_idx = int(min(self.__num_points, center_angle + obstacle_width // 2))
            distances[start_idx:end_idx] = (
                np.random.default_rng()
                .uniform(
                    obstacle_distance - 0.1,
                    obstacle_distance + 0.1,
                    size=(end_idx - start_idx),
                )
                .astype(np.float32)
            )

        # Add noise for realism
        distances += (
            np.random.default_rng()
            .normal(0, 0.01, self.__num_points)
            .astype(np.float32)
        )
        distances = np.clip(
            distances,
            0.1,
            5.0,
        )  # Ensure distances are within sensor range

        self._logger.debug("[LidarDummy] Simulated realistic distances generated.")
        return distances * self.__distance_unit

    def scan_to_polars(self) -> np.ndarray:
        """Simulate a lidar scan and return fake polar coordinates.

        Returns:
            np.ndarray: numpy array of [angle, distance] pairs

        """
        distances = self.scan_to_distances()
        polars = np.column_stack((self.__polars_angles, distances))
        polars[polars[:, 1] > self._min_distance]

        self._logger.debug("[LidarDummy] Simulated polar coordinates generated.")
        # return valid_polars
        return np.array([])

    def is_connected(self) -> bool:
        """Check if the dummy lidar is connected.

        Returns:
            bool: connection status

        """
        return self.__is_connected

    @property
    def distances(self) -> np.ndarray:
        """Get the last simulated distances.

        Returns:
            np.ndarray: numpy array of distances

        """
        return self.scan_to_distances()

    @property
    def polars(self) -> np.ndarray:
        """Get the last simulated polar coordinates.

        Returns:
            np.ndarray: numpy array of [angle, distance] pairs

        """
        return self.scan_to_polars()
