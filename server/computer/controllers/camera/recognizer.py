from controllers.camera.frame import Frame
from controllers.camera.detected_object import DetectedObject, Aruco, ColorObject

from sklearn.cluster import DBSCAN
import numpy as np
import cv2


class ArucoRecognizer:
    def __init__(self, aruco_type: str):
        # Load pre-trained IA from OpenCV based on the aruco type
        self.dictionary = cv2.aruco.Dictionary_get(getattr(cv2.aruco, aruco_type))
        self.params = cv2.aruco.DetectorParameters_create()

    def detect(self, img: np.ndarray, **extra_params) -> list[Aruco]:
        founds = cv2.aruco.detectMarkers(img, self.dictionary, parameters=self.params, **extra_params)

        if founds[1] is None:
            return []

        nb_founds = len(founds[1])
        return [Aruco(founds[1][i][0], founds[0][i][0]) for i in range(nb_founds)]


class ColorRecognizer:
    def __init__(self, detection_range: tuple[np.array, np.array], clustering_eps: int = 10,
                 clustering_min_samples: int = 10, name: str = "unknow") -> None:
        self.range_low = detection_range[0]
        self.range_high = detection_range[1]
        self.clustering_eps = clustering_eps
        self.clustering_min_samples = clustering_min_samples
        self.name = name

    def __color_mask(self, img: np.ndarray, reduce_noise=True):
        """
        Converting an image from BGR to HSV format is crucial for color detection tasks in computer vision
        because it separates color from light intensity. This separation enhances the system's robustness
        to lighting changes, makes color specification more intuitive, and improves color segmentation
        accuracy, especially under varying lighting conditions.
        """
        img_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

        # Apply the color mask to the image, to keep only the color we want (color in detection range)
        color_mask = cv2.inRange(img_hsv, self.range_low, self.range_high)
        # Dilate the mask to increase the size of the detected color
        color_mask = cv2.dilate(color_mask, None, iterations=3)

        if reduce_noise:
            color_mask = cv2.GaussianBlur(color_mask, (3, 3), 0)

        return color_mask

    @staticmethod
    def __extract_positive_points(mask: np.ndarray) -> np.ndarray:
        return np.column_stack(np.nonzero(mask))

    @staticmethod
    def __find_clusters(points: np.ndarray) -> np.ndarray:
        if points.size > 0:
            dbscan = DBSCAN(eps=self.clustering_eps, min_samples=self.clustering_min_samples)
            return dbscan.fit_predict(points)

        return np.array([])

    @staticmethod
    def __compute_clusters_info(points: np.ndarray, clusters):
        clusters_info = []

        unique_clusters = set(clusters)
        # Remove noise (cluster label -1)
        if -1 in unique_clusters:
            unique_clusters.remove(-1)

        for cluster in unique_clusters:
            cluster_points = points[clusters == cluster]
            if cluster_points.size > 0:
                centroid = np.mean(cluster_points, axis=0)
                min_x, max_x = np.min(cluster_points[:, 1]), np.max(cluster_points[:, 1])
                min_y, max_y = np.min(cluster_points[:, 0]), np.max(cluster_points[:, 0])
                bounding_box = ((min_x, min_y), (max_x, max_y))

                clusters_info.append({"centroid": (centroid[1], centroid[0]), "bounding_box": bounding_box})

        return clusters_info

    def detect(self, img: np.ndarray, reduce_noise=True) -> list[ColorObject]:
        color_mask = self.__color_mask(img, reduce_noise)
        points = self.__extract_positive_points(color_mask)
        clusters = self.__find_clusters(points)

        clusters_info = self.__compute_clusters_info(points, clusters)

        return [
            ColorObject(cluster.get("centroid"), cluster.get("bounding_box"), self.name)
            for cluster in clusters_info
        ]
