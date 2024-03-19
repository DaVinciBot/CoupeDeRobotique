from config_loader import CONFIG

# Import from common
from geometry import OrientedPoint, Point

import math


class Lidar:
    """
    Classe permettant de rÃ©cupÃ©rer les donnÃ©es du lidar, et de les traiter, la rÃ©sultion angulaire est de 1/3 de degrÃ©
    """

    def __init__(self, min_angle: float = -math.pi, max_angle: float = math.pi):
        """
        Initialise la connection au lidar

        :param min_angle: l'angle de lecture minimal, defaults to -math.pi
        :type min_angle: float, optional
        :param max_angle: l'angle de lecture maximal, defaults to math.pi
        :type max_angle: float, optional
        """
        import pysicktim as lidar

        # TODO: mise en place d'un erreur si le lidar n'est pas trouvé !
        self.min_angle = min_angle
        self.max_angle = max_angle
        self.lidar_obj = lidar

    def __scan(self):
        self.lidar_obj.scan()

    def __get_scan_distances(self) -> list[float]:
        return self.lidar_obj.scan.distances

    def __get_polar(self) -> list[tuple[float, float]]:
        angle_step = (self.max_angle - self.min_angle) / len(
            self.__get_scan_distances()
        )
        polar_coordinates = []
        for i in range(len(self.__get_scan_distances())):
            polar_coordinates.append(
                (self.min_angle + (i * angle_step), self.__get_scan_distances()[i])
            )
        return polar_coordinates

    def __get_cartesian(self) -> list[tuple[float, float]]:
        cartesian_coordinates = []
        for coordinate in self.__get_polar():
            cartesian_coordinates.append(
                (
                    coordinate[1] * math.cos(coordinate[0]),
                    coordinate[1] * math.sin(coordinate[0]),
                )
            )
        return cartesian_coordinates

    def __get_absolute_cartesian(self, robot_pos: OrientedPoint) -> list[Point]:
        """
        Convertit des coordonnÃ©es cartÃ©siennes relatives Ã  un robot en coordonnÃ©es absolues de la table

        :param cartesian_coordinates: les coordonnÃ©es cartÃ©siennes relatives au robot
        :type cartesian_coordinates: list[float]
        :param robot_pos: la position du robot sur la table (x, y, theta), theta est l'angle de rotation du robot
        :type robot_pos: tuple[float, float, float]
        :return: les coordonnÃ©es cartÃ©siennes absolues
        :rtype: list[float]
        """
        res = []
        for coordinate in self.__get_cartesian():
            res.append(
                Point(
                    robot_pos.x + coordinate[0] * math.cos(robot_pos.theta),
                    robot_pos.y + coordinate[1] * math.sin(robot_pos.theta),
                )
            )
        return res

    def scan_to_polar(self) -> list[tuple[float, float]]:
        self.__scan()
        return self.__get_polar()

    def scan_to_cartesian(self) -> list[tuple[float, float]]:
        self.__scan()
        return self.__get_cartesian()

    def scan_to_absolute_cartesian(self, robot_pos: OrientedPoint) -> list[Point]:
        self.__scan()
        return self.__get_absolute_cartesian(robot_pos)
    
    def scan_distance(self,start_angle, end_angle, step_angle=1/3):
        """return a list of distances between start_angle and end engle 

        Args:
            start_angle (float): the angle from were to start mesuring
            end_angle (float): the last angle of the mesure 
            step_angle (float): every mesure from the lidar is separeted from a given angle

        Returns:
            _type_: a list of float representing the distance between the lidar and detected points at each angle between the required ones
        """
        self.__scan()
        return [self.lidar_obj.scan.distances[i] for i in range(int(start_angle/step_angle), int(end_angle/step_angle)) if self.lidar_obj.scan.distances[i] > 0.01]