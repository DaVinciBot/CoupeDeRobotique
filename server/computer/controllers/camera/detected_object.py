from abc import abstractmethod


class DetectedObject:
    @abstractmethod
    def get_info(self, extra_info=False):
        """
        Return a dictionary with the object information.
        Every object must return :
        * type: the type of the object
        * bounding_box: the bounding box of the object
        * centroid: the centroid of the object
        * corners: the corners of the object
        --> extra_info: if True, return extra information about the object
        """
        pass

    @abstractmethod
    def __str__(self):
        pass


class Aruco(DetectedObject):
    def __init__(self, encoded_number, corners):
        self.encoded_number = encoded_number
        self.corners = corners

        self._centroid = None
        self._bounding_box = None
        self._ellipse = None

    """
        Private methods
    """

    def __compute_ellipses(self):
        points = np.array([
            [self.corners[0][0][0], self.corners[0][0][1]],
            [self.corners[0][1][0], self.corners[0][1][1]],
            [self.corners[0][2][0], self.corners[0][2][1]],
            [self.corners[0][3][0], self.corners[0][3][1]]
        ])

        center = points.mean(axis=0)

        points_centered = points - center
        covariance = np.cov(points_centered.T)

        eigenvalues, eigenvectors = np.linalg.eig(covariance)

        axis_length = 2 * np.sqrt(eigenvalues)

        angle = np.arctan2(eigenvectors[0, 1], eigenvectors[0, 0])
        angle_degrees = np.degrees(angle)

        max_radius = np.sqrt(max(eigenvalues))

        return {
            "center": center,
            "axis_length": axis_length,
            "angle_degrees": angle_degrees,
            "max_radius": max_radius
        }

    """
        Properties
    """

    @property
    def centroid(self):
        if self._centroid is None:
            self._centroid = (
                (self.corners[0][0] + self.corners[2][0]) / 2,
                (self.corners[0][1] + self.corners[2][1]) / 2,
            )
        return self._centroid

    @property
    def bounding_box(self):
        if self._bounding_box is None:
            self._bounding_box = (
                (self.corners[0][0], self.corners[0][1]),
                (self.corners[2][0], self.corners[2][1]),
            )
        return self._bounding_box

    @property
    def ellipse(self):
        if self._ellipse is None:
            self._ellipse = self.__compute_ellipse()
        return self._ellipse

    @property
    def axis_length(self):
        return self.ellipse["axis_length"]

    @property
    def angle_degrees(self):
        return self.ellipse["angle_degrees"]

    @property
    def max_radius(self):
        return self.ellipse["max_radius"]

    """
        Public methods
    """

    def get_info(self, extra_info=False):
        info = {
            "type": "aruco",
            "bounding_box": self.bounding_box,
            "centroid": self.centroid,
            "corners": self.corners
        }
        if extra_info:
            info["encoded_number"] = self.encoded_number
            info["ellipse"] = self.ellipse

        return info

    def __str__(self):
        return f"[{self.__class__.__name__}]: id({self.encoded_number})  centroid({self.centroid[0]:.2f}, {self.centroid[1]:.2f})"


class ColorObject(DetectedObject):
    def __init__(self, centroid, bounding_box, name: str = "unknown"):
        self.centroid = centroid
        self.bounding_box = bounding_box
        self.name = name

        self._corners = None

    @property
    def corners(self):
        if self._corners is None:
            self._corners = [
                (self.bounding_box[0][0], self.bounding_box[0][1]),
                (self.bounding_box[1][0], self.bounding_box[0][1]),
                (self.bounding_box[1][0], self.bounding_box[1][1]),
                (self.bounding_box[0][0], self.bounding_box[1][1])
            ]
        return self._corners

    def get_info(self, extra_info=False):
        info = {
            "type": "color_object",
            "bounding_box": self.bounding_box,
            "centroid": self.centroid,
            "corners": self.corners
        }
        if extra_info:
            info["color"] = self.name

        return info

    def __str__(self):
        return f"[{self.__class__.__name__}]: color({self.name}) centroid({self.centroid[0]:.2f}, {self.centroid[1]:.2f})"
