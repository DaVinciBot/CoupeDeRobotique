import numpy as np
import cv2


class Frame:
    def __init__(self, img: np.ndarray, ids: list[int], corners: list[np.array]):
        self.img = img
        self.ids = ids
        self.corners = corners
        self.len = 0 if ids is None else len(ids)

    def draw_markers(self) -> np.ndarray:
        if self.len:
            return cv2.aruco.drawDetectedMarkers(self.img, self.corners, self.ids)

    def draw_circle_with_label(self, x: int, y: int, label: str, radius: int, thickness: int,
                               color: tuple[int, int, int]):
        cv2.circle(
            self.img,
            (x, y),
            radius,
            color,
            thickness
        )

        cv2.putText(
            self.img,
            label,
            (x + 10, y + 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            color,
            2
        )

    def draw_corners(self, radius=5, thickness=2):
        # Corners deco
        corners_deco = [
            {"label": "A", "color": (255, 255, 0)},
            {"label": "B", "color": (0, 255, 255)},
            {"label": "C", "color": (255, 0, 255)},
            {"label": "D", "color": (255, 255, 255)},
        ]
        for index in range(self.len):
            for deco_index in range(len(corners_deco)):
                self.draw_circle_with_label(
                    int(self.corners[index][0][deco_index][0]),
                    int(self.corners[index][0][deco_index][1]),
                    corners_deco[deco_index]["label"],
                    radius,
                    thickness,
                    corners_deco[deco_index]["color"]
                )

    def draw_barycenter(self, radius=5, thickness=2, color=(255, 0, 0)):
        for index in range(self.len):
            cv2.line(
                self.img,
                (int(self.corners[index][0][0][0]), int(self.corners[index][0][0][1])),
                (int(self.corners[index][0][2][0]), int(self.corners[index][0][2][1])),
                color,
                thickness
            )
            cv2.line(
                self.img,
                (int(self.corners[index][0][1][0]), int(self.corners[index][0][1][1])),
                (int(self.corners[index][0][3][0]), int(self.corners[index][0][3][1])),
                color,
                thickness
            )

            # Calcul Xcenter
            x = (int(self.corners[index][0][0][0]) + int(self.corners[index][0][2][0])) // 2
            y = (int(self.corners[index][0][0][1]) + int(self.corners[index][0][2][1])) // 2

            self.draw_circle_with_label(
                x,
                y,
                f"             X: {x}  Y:{y}",
                radius,
                thickness,
                color,

            )

    def compute_ellipses(self):
        ellipses = []
        if self.len:
            for index in range(self.len):
                points = np.array([
                    [self.corners[index][0][0][0], self.corners[index][0][0][1]],
                    [self.corners[index][0][1][0], self.corners[index][0][1][1]],
                    [self.corners[index][0][2][0], self.corners[index][0][2][1]],
                    [self.corners[index][0][3][0], self.corners[index][0][3][1]]
                ])
                center = points.mean(axis=0)
                points_centered = points - center
                covariance = np.cov(points_centered.T)

                # Résoudre le problème de valeur propre généralisé
                eigenvalues, eigenvectors = np.linalg.eig(covariance)

                # Calculer les longueurs des axes principaux
                axis_length = 2 * np.sqrt(eigenvalues)  # Multiplié par 2 pour obtenir le diamètre

                # Trouver l'angle d'orientation de l'ellipse
                angle = np.arctan2(eigenvectors[0, 1], eigenvectors[0, 0])
                angle_degrees = np.degrees(angle)

                # Le rayon maximum est la racine carrée de la valeur propre maximale
                max_radius = np.sqrt(max(eigenvalues))

                ellipses.append(
                    {
                        "center": center,
                        "axis_length": axis_length,
                        "angle_degrees": angle_degrees,
                        "max_radius": max_radius
                    }
                )
        return ellipses

    def draw_ellipses(self, ellipses):
        for ellipse in ellipses:
            cv2.ellipse(self.img,
                        (int(ellipse.get("center")[0]), int(ellipse.get("center")[1])),
                        (int(ellipse.get("axis_length")[0] / 2), int(ellipse.get("axis_length")[1] / 2)),
                        ellipse.get("angle_degrees"),
                        0, 360,
                        (255, 0, 0), 2)

            text_position = (
                int(ellipse.get("center")[0] + ellipse.get("axis_length")[0] / 2), int(ellipse.get("center")[1]) + 40
            )
            cv2.putText(
                self.img, f"Radius: {ellipse.get('max_radius'):.2f}", text_position, cv2.FONT_HERSHEY_SIMPLEX,
                0.5, (255, 255, 255), 1
            )
