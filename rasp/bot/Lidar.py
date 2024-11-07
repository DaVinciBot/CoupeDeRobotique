import math
import pysicktim as lidar


def scan_values_to_polar(
    scan_values: list[float], min_angle: float, max_angle: float
) -> list[list[float, float]]:
    """permet de

    Args:
        scan_values (_type_): _description_
        min_angle (_type_): _description_
        max_angle (_type_): _description_

    Returns:
        _type_: _description_
    """
    angle_step = (max_angle - min_angle) / len(scan_values)
    polar_coordinates = []
    for i in range(len(scan_values)):
        polar_coordinates.append((min_angle + i * (angle_step), scan_values[i]))
    return polar_coordinates


def polar_to_cartesian(
    polar_coordinates: list[list[float, float, float]]
) -> list[list[float, float]]:
    cartesian_coordinates = []

    for coordinate in polar_coordinates:
        cartesian_coordinates.append(
            (
                coordinate[1] * math.cos(coordinate[0]),
                coordinate[1] * math.sin(coordinate[0]),
            )
        )

    return cartesian_coordinates


def threshold(
    polar_coordinates: list[list[float, float, float]], threshold: float
) -> list[list[float, float, float]]:
    res = []
    for coordinate in polar_coordinates:
        if coordinate[1] < threshold:
            res.append(coordinate)
    return res


def relative_to_absolute_cartesian_coordinates(
    cartesian_coordinates: list[list[float, float]],
    robot_pos: tuple[float, float, float],
) -> list[float]:
    """
    Convertit des coordonnées cartésiennes relatives à un robot en coordonnées absolues de la table

    :param cartesian_coordinates: les coordonnées cartésiennes relatives au robot
    :type cartesian_coordinates: list[float]
    :param robot_pos: la position du robot sur la table (x, y, theta), theta est l'angle de rotation du robot
    :type robot_pos: tuple[float, float, float]
    :return: les coordonnées cartésiennes absolues
    :rtype: list[float]
    """
    res = []
    for coordinate in cartesian_coordinates:
        res.append(
            (
                robot_pos[0] + coordinate[0] * math.cos(robot_pos[2]),
                robot_pos[1] + coordinate[1] * math.sin(robot_pos[2]),
            )
        )
    return res


def is_under_threshold(
    polar_coordinates: list[list[float, float, float]], threshold: float
) -> bool:
    return min([x[1] for x in polar_coordinates]) < threshold


class Lidar:
    """
    Classe permettant de récupérer les données du lidar, et de les traiter, la résultion angulaire est de 1/3 de degré
    """

    def __init__(self, min_angle: float = -math.pi, max_angle: float = math.pi):
        """
        Initialise la connection au lidar

        :param min_angle: l'angle de lecture minimal, defaults to -math.pi
        :type min_angle: float, optional
        :param max_angle: l'angle de lecture maximal, defaults to math.pi
        :type max_angle: float, optional
        """
        self.min_angle = min_angle
        self.max_angle = max_angle
        self.lidar_obj = lidar

    def __scan(self):
        """
        Wrapper de la fonction scan du lidar (lib pysicktim)
        """
        self.lidar_obj.scan()

    def __scan_values(self):
        return self.lidar_obj.scan.distances

    def __scan_values_to_polar(self):
        return scan_values_to_polar(
            self.__scan_values(), self.min_angle, self.max_angle
        )

    def __polar_to_cartesian(self):
        return polar_to_cartesian(self.__scan_values_to_polar())

    def get_nearest_point(self) -> float:
        """
        Retourne la distance du point le plus proche par rapport au lidar

        :return: distance en mètres
        :rtype: float
        """
        lidar.scan()
        points = [val for val in lidar.scan.distances if val > 0.01]
        points.sort()
        return points[0]

    def safe_get_nearest_point(self, nb_mesure: int = 30) -> float:
        points = []
        for _ in range(nb_mesure):
            lidar.scan()
            scan = [val for val in lidar.scan.distances if val > 0.01]
            scan.sort()
            points.append(scan[0])

        points.sort()
        return points[len(points) // 2]

    def safe_get_nearest_point_between(
        self, start_angle: float, end_angle: float
    ) -> float:
        """Retourne la distance du point le plus proche par rapport au lidar entre les angles donnés (testé)

        :param start_angle: l'angle de départ de la mesure, en degrés
        :type start_angle: float
        :param end_angle: l'angle de fin de la mesure, en degrés
        :type end_angle: float
        :return: la distance du point le plus proche, en mètres
        :rtype: float
        """
        points = []

        for _ in range(30):
            lidar.scan()
            scan = [
                val
                for val in lidar.scan.distances[
                    (start_angle + 45) * 3 : (end_angle + 45) * 3
                ]
                if val > 0.01
            ]
            scan.sort()
            points.append(scan[0])

        points.sort()
        return points[len(points) // 2]

    def is_obstacle_infront(self, start_angle=90, end_angle=180, treshold=0.2) -> bool:
        """Retourne True si un obstacle est détecté entre les angles donnés, False sinon

        :param start_angle: l'angle de départ de la mesure, defaults to 90
        :type start_angle: int, optional
        :param end_angle: l'angle de fin de la mesure, defaults to 180
        :type end_angle: int, optional
        :param treshold:  filtre les valeurs plus petites, en mètres, defaults to 0.2
        :type treshold: float, optional
        :return: True si un obstacle est détecté entre les angles donnés
        :rtype: bool
        """
        nearest_point = self.safe_get_nearest_point_between(start_angle, end_angle)
        return nearest_point <= treshold

    def get_cartesian_points(self):
        return self.__polar_to_cartesian()

    def get_polar_points(self):
        return self.__scan_values_to_polar()

    def get_values(self) -> list:
        lidar.scan()
        return self.lidar_obj.scan.distances
