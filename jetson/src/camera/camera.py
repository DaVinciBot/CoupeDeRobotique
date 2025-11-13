import time
from typing import Tuple

import cv2
import numpy as np


class Camera:
    """Camera class for handling video capture and processing."""

    def __init__(
        self,
        camera_id: int,
        width: int | None = None,
        height: int | None = None,
        backends: list[int] | None = None,
    ) -> None:
        """Initialize the camera.

        Args:
            camera_id (int): The ID of the camera to use.
            width (Optional[int], optional): The desired width of the camera feed. Defaults to None.
            height (Optional[int], optional): The desired height of the camera feed. Defaults to None.
            backends (Optional[List[int]], optional): A list of backend preferences for the camera. Defaults to None.
        """
        self.camera_id = camera_id
        self.cam: cv2.VideoCapture | None = None

        if backends is None:
            backends = [
                getattr(cv2, attr, cv2.CAP_ANY) for attr in ("CAP_DSHOW", "CAP_MSMF")
            ] + [cv2.CAP_ANY]

        for backend in backends:
            self.cam = cv2.VideoCapture(camera_id, backend)
            if self.cam and self.cam.isOpened():
                break
            if self.cam:
                self.cam.release()

        if self.cam is None or not self.is_opened():
            return

        if width and height:
            self.cam.set(cv2.CAP_PROP_FRAME_WIDTH, width)
            self.cam.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
            time.sleep(0.05)
            for _ in range(3):
                self.cam.read()

    def is_opened(self) -> bool:
        return self.cam is not None and self.cam.isOpened()

    def get_resolution(self) -> Tuple[int, int]:
        if self.cam is None or not self.is_opened():
            return (0, 0)
        return (
            int(self.cam.get(cv2.CAP_PROP_FRAME_WIDTH)),
            int(self.cam.get(cv2.CAP_PROP_FRAME_HEIGHT)),
        )

    def get_camera_info(self) -> dict:
        if self.cam is None or not self.is_opened():
            return {}
        w, h = self.get_resolution()
        return {"width": w, "height": h, "fps": self.cam.get(cv2.CAP_PROP_FPS)}

    def read_frame(self):
        if self.cam is None or not self.is_opened():
            return None
        ret, frame = self.cam.read()
        return frame if ret else None

    def calibrate(
        self,
        chessboard_size: Tuple[int, int] = (9, 6),
        square_size: float = 1.0,
        num_images: int = 20,
    ):
        if not self.is_opened():
            return None, None, None, None

        objp = np.zeros((chessboard_size[0] * chessboard_size[1], 3), np.float32)
        objp[:, :2] = np.mgrid[
            0 : chessboard_size[0], 0 : chessboard_size[1]
        ].T.reshape(-1, 2)
        objp *= square_size

        objpoints, imgpoints = [], []
        captured = 0
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

        # Statistiques pour validation
        coverage_map = np.zeros((
            self.get_resolution()[1] // 20,
            self.get_resolution()[0] // 20,
        ))

        print(f"Capture de {num_images} images.")
        print("CONSEILS : Variez angles, distances et positions")
        print("Appuyez sur 'c' pour capturer, 'q' pour terminer.")

        while captured < num_images:
            frame = self.read_frame()
            if frame is None:
                continue

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            ret, corners = cv2.findChessboardCorners(
                gray,
                chessboard_size,
                cv2.CALIB_CB_ADAPTIVE_THRESH + cv2.CALIB_CB_NORMALIZE_IMAGE,
            )

            display = frame.copy()

            # Affichage de la carte de couverture
            coverage_display = cv2.resize(coverage_map, (200, 150))
            coverage_display = (
                coverage_display * 255 / max(1, coverage_map.max())
            ).astype(np.uint8)
            coverage_display = cv2.applyColorMap(coverage_display, cv2.COLORMAP_JET)
            display[10:160, 10:210] = coverage_display

            if ret:
                cv2.drawChessboardCorners(display, chessboard_size, corners, ret)

                # Calcul de la qualité de détection
                sharpness = cv2.Laplacian(gray, cv2.CV_64F).var()

                color = (0, 255, 0) if sharpness > 50 else (0, 165, 255)
                cv2.putText(
                    display,
                    f"Detecte! Nettete: {sharpness:.0f}",
                    (10, 180),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    color,
                    2,
                )
                cv2.putText(
                    display,
                    f"'c' pour capturer ({captured}/{num_images})",
                    (10, 210),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (0, 255, 0),
                    2,
                )
            else:
                cv2.putText(
                    display,
                    "Pas de motif detecte",
                    (10, 180),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (0, 0, 255),
                    2,
                )

            cv2.imshow("Calibration", display)
            key = cv2.waitKey(1) & 0xFF

            if key == ord("c") and ret:
                corners2 = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)

                # Vérification anti-doublon (position similaire)
                center = np.mean(corners2, axis=0)[0]
                grid_x = int(center[0] / 20)
                grid_y = int(center[1] / 20)

                if coverage_map[grid_y, grid_x] > 2:
                    print("⚠ Zone déjà capturée, variez la position")
                    continue

                objpoints.append(objp)
                imgpoints.append(corners2)
                coverage_map[grid_y, grid_x] += 1
                captured += 1
                print(
                    f"✓ Image {captured}/{num_images} capturée (netteté: {sharpness:.0f})"
                )

            elif key == ord("q"):
                break

        cv2.destroyAllWindows()

        if captured < 10:
            print("Erreur: minimum 10 images nécessaires")
            return None, None, None, None

        print("Calibration en cours...")

        # Calibration avec flags optimaux
        flags = (
            cv2.CALIB_FIX_PRINCIPAL_POINT  # Centre optique fixe
            + cv2.CALIB_FIX_ASPECT_RATIO
        )  # Ratio fx/fy constant

        ret, camera_matrix, dist_coeffs, rvecs, tvecs = cv2.calibrateCamera(
            objpoints, imgpoints, gray.shape[::-1], None, None, flags=flags
        )

        if ret:
            # Calcul de l'erreur de reprojection
            total_error = 0
            for i in range(len(objpoints)):
                imgpoints2, _ = cv2.projectPoints(
                    objpoints[i], rvecs[i], tvecs[i], camera_matrix, dist_coeffs
                )
                error = cv2.norm(imgpoints[i], imgpoints2, cv2.NORM_L2) / len(
                    imgpoints2
                )
                total_error += error

            mean_error = total_error / len(objpoints)
            print(f"Erreur de reprojection moyenne: {mean_error:.3f} pixels")

            if mean_error > 1.0:
                print("⚠ ATTENTION : Erreur élevée, recommencez la calibration")
            elif mean_error < 0.5:
                print("✓ Excellente calibration!")

        return (
            (camera_matrix, dist_coeffs, rvecs, tvecs)
            if ret
            else (None, None, None, None)
        )

    def release(self):
        if self.cam:
            self.cam.release()
            self.cam = None
