"""LiDAR sensor interfaces."""

from sensors.lidar.lidar import Lidar, LidarError
from sensors.lidar.lidar_dummy import LidarDummy

__all__ = ["Lidar", "LidarDummy", "LidarError"]
