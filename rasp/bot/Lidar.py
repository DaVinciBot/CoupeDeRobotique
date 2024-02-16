import math
from .Shapes import OrientedPoint, Point


class Direction:
    STRAIGHT = 0
    LEFT = 1
    RIGHT = 2
    BOTH = 3
    ERROR = 4


def get_possible_directions(
    scan1: list,
    scan2: list,
    start_angle=90,
    end_angle=180,
    step_angle=1 / 3,
    threshold=0.2,
    delay_mili=10,
) -> int:
    """a basic function that enables the analysis of the moving direction of an obstacle and returns possible directions for us.

    Args:
        start_angle (int, optional): the first angle taken into account in the process. Defaults to 0.
        end_angle (type, optional): the last angle taken into account in the process. Defaults to len(lidar.scan.distances).
        step_angle (type, optional): enables the computation of indices of the given angles in the tab. Defaults to 1/3.
        threshold (float, optional): if the distance between the robot and an element is under the threshold, then consider it as an obstacle. Defaults to 0.2.
        delay_mili (int, optional): the delay between the two measurements of the lidar. Defaults to 10.

    Returns:
        int: description
    """
    i: int = int(start_angle / step_angle)
    i_max: int = int(end_angle / step_angle)
    first_start: int = -1  # must be set to -1
    second_start: int = -1
    # get the index of the first distance under threshold of each scan
    while i < i_max and (first_start == -1 or second_start == -1):
        if scan1[i] <= threshold and first_start == -1:
            first_start = i
        if scan2[i] <= threshold and second_start == -1:
            second_start = i
        i += 1
    if second_start == -1:  # no distance under threshold
        return Direction.STRAIGHT
    i = i_max
    first_stop: int = -1
    second_stop: int = -1
    # get the index of the last distance under threshold of each scan
    while i > -1 and (first_stop == -1 or second_stop == -1):
        if scan1[i] <= threshold and first_stop == -1:
            first_stop = i
        if scan2[i] <= threshold and second_stop == -1:
            second_stop = i
        i -= 1
    if (
        second_start < first_start and second_stop < first_stop
    ):  # is the other robot going left ?
        return Direction.LEFT
    if (
        second_start > first_start and second_stop > first_stop
    ):  # is the other robot going right ?
        return Direction.RIGHT
    if second_start == first_start and second_stop == first_stop:
        return Direction.BOTH
    return Direction.ERROR


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


def polar_to_cartesian(polar_coordinates: list[Point]) -> list[Point]:
    cartesian_coordinates = []

    for coordinate in polar_coordinates:
        cartesian_coordinates.append(
            Point(
                round(coordinate.y * math.cos(coordinate.x), 14),
                round(coordinate.y * math.sin(coordinate.x), 14),
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
    cartesian_coordinates: list[Point],
    robot_pos: OrientedPoint,
) -> list[Point]:
    """
    Convertit des coordonnées cartésiennes relatives à un robot en coordonnées absolues de la table

    :param cartesian_coordinates: les coordonnées cartésiennes relatives au robot
    :type cartesian_coordinates: list[Point]
    :param robot_pos: la position du robot sur la table (x, y, theta), theta est l'angle de rotation du robot
    :type robot_pos: OrientedPoint
    :return: les coordonnées cartésiennes absolues
    :rtype: list[Point]
    """
    res = []
    for coordinate in cartesian_coordinates:
        res.append(
            Point(
                robot_pos.x + coordinate.x,
                robot_pos.y + coordinate.y,
            )
        )
    return res


def is_under_threshold(
    polar_coordinates: list[OrientedPoint], threshold: float
) -> bool:
    return min([x.y for x in polar_coordinates]) < threshold


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
        import pysicktim as lidar

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
        self.lidar_obj.scan()
        points = [val for val in self.lidar_obj.scan.distances if val > 0.01]
        points.sort()
        return points[0]

    def safe_get_nearest_point(self, nb_mesure: int = 30) -> float:
        points = []
        for _ in range(nb_mesure):
            self.lidar_obj.scan()
            scan = [val for val in self.lidar_obj.scan.distances if val > 0.01]
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
            self.lidar_obj.scan()
            scan = [
                val
                for val in self.lidar_obj.scan.distances[
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
        self.lidar_obj.scan()
        return self.lidar_obj.scan.distances


# class Lidar:
#     """
#     Classe permettant de récupérer les données du lidar, et de les traiter, la résultion angulaire est de 1/3 de degré
#     """

#     def __init__(self, min_angle: float = -math.pi, max_angle: float = math.pi):
#         """
#         Initialise la connection au lidar

#         :param min_angle: l'angle de lecture minimal, defaults to -math.pi
#         :type min_angle: float, optional
#         :param max_angle: l'angle de lecture maximal, defaults to math.pi
#         :type max_angle: float, optional
#         """
#         import pysicktim as lidar

#         self.min_angle = min_angle
#         self.max_angle = max_angle
#         self.lidar_obj = lidar

#     def __scan(self):
#         self.lidar_obj.scan()

#     def __get_scan_distances(self) -> list[float]:
#         return self.lidar_obj.scan.distances

#     def __get_polar(self) -> list[list[float, float]]:
#         angle_step = (self.max_angle - self.min_angle) / len(self.__get_scan_distances())
#         polar_coordinates = []
#         for i in range(len(self.__get_scan_distances())):
#             polar_coordinates.append((self.min_angle + (i * angle_step), self.__get_scan_distances()[i]))
#         return polar_coordinates

#     def __get_cartesian(self) -> list[list[float, float]]:
#         cartesian_coordinates = []
#         for coordinate in self.__get_polar():
#             cartesian_coordinates.append(
#                 (
#                     coordinate[1] * math.cos(coordinate[0]),
#                     coordinate[1] * math.sin(coordinate[0]),
#                 )
#             )
#         return cartesian_coordinates

#     def __get_absolute_cartesian(self, robot_pos: OrientedPoint) -> list[Point]:
#         """
#         Convertit des coordonnées cartésiennes relatives à un robot en coordonnées absolues de la table

#         :param cartesian_coordinates: les coordonnées cartésiennes relatives au robot
#         :type cartesian_coordinates: list[float]
#         :param robot_pos: la position du robot sur la table (x, y, theta), theta est l'angle de rotation du robot
#         :type robot_pos: tuple[float, float, float]
#         :return: les coordonnées cartésiennes absolues
#         :rtype: list[float]
#         """
#         res = []
#         for coordinate in self.__get_cartesian():
#             res.append(
#                 Point(
#                     robot_pos.x + coordinate.x * math.cos(robot_pos.theta),
#                     robot_pos.y + coordinate.y * math.sin(robot_pos.theta),
#                 )
#             )
#         return res


#     def scan_to_polar(self) -> list[list[float, float]]:
#         self.__scan()
#         return self.__get_polar()

#     def scan_to_cartesian(self) -> list[list[float, float]]:
#         self.__scan()
#         return self.__get_cartesian()

#     def scan_to_absolute_cartesian(self, robot_pos: OrientedPoint) -> list[Point]:
#         self.__scan()
#         return self.__get_absolute_cartesian(robot_pos)
