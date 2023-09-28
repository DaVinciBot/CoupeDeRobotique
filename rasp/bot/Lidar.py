import math
import pysicktim as lidar


def scan_values_to_polar(scan_values: list, min_angle: float, max_angl: float) -> list[list[float,float,float]]:
    angle_step = (max_angle - min_angle) / len(scan_values)
    polar_coordinates = []
    for i in range(len(scan_values)):
        polar_coordinates.append((min_angle + i * (angle_step), scan_values[i]))
    return polar_coordinates


def polar_to_cartesian(polar_coordinates: list[list[float, float, float]]) -> list[list[float,float]]:
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
    Classe permettant de récupérer les données du lidar, et de les traiter
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

    def get_face_nearest_point(self) -> float:
        """
        Retourne le point le plus proche en face du lidar

        :return: _description_
        :rtype: float
        """
        lidar.scan()
        points = [val for val in lidar.scan.distances[269:-271] if val > 0.01]
        points.sort()
        return points[0]

    def safe_get_nearest_point(self, nombre_essai: int = 10) -> float:
        """
        Renvoie le point le plus proche par rapport au lidar, en prennant la médianne de {nombre_essai} mesures pour éviter les erreurs


        :param nombre_essai: le nombre de detection du lidar sur lequels faire une médianne, defaults to 10
        :type nombre_essai: int, optional
        :return: le point le plus proche par rapport au lidar, en mètres
        :rtype: float
        """
        points = []
        for _ in range(nombre_essai):
            lidar.scan()
            scan = [val for val in lidar.scan.distances if val > 0.01]
            scan.sort()
            points.append(scan[0])

        points.sort()
        return points[len(points) // 2]

    def safe_face_get_nearest_point(self, nombre_essai: int = 10) -> float:
        """
        Renvoie le point le plus proche en face du lidar, en prennant la médianne de {nombre_essai} mesures pour éviter les erreurs

        :param nombre_essai: le nombre de detection du lidar sur lequels faire une médianne, defaults to 10
        :type nombre_essai: int, optional
        :return: le point le plus proche en face du lidar, en mètres
        :rtype: float
        """
        points = []
        for _ in range(nombre_essai):
            points.append(self.get_face_nearest_point())

        points.sort()
        return points[len(points) // 2]

    def get_cartesian_points(self) -> list:
        return self.__polar_to_cartesian()

    def get_polar_points(self) -> list:
        return self.__scan_values_to_polar()
