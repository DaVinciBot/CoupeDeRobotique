"""Camera module for video capture and calibration."""

import time
from typing import Any, Dict, List, Optional, Tuple, Union

import cv2
import numpy as np
from src.utils.timing import timer

sharpness_minimum_threshold: int = 50
coverage_map_maximum_threshold: int = 2
minimum_images_for_calibration: int = 10
mean_for_excellent_calibration: float = 0.5
mean_for_bad_calibration: float = 1.0


class Camera:
    """Camera class for handling video capture and processing."""

    def __init__(
        self,
        camera_id: int,
        width: Optional[int] = None,
        height: Optional[int] = None,
        backends: Optional[List[int]] = None,
        fps: Optional[float] = None,
        use_mjpg: bool = True,
        use_csi: bool = False,
    ) -> None:
        """Initialize the camera.

        Args:
            camera_id (int): The ID of the camera to use.
            width (int, optional): The desired width of the camera feed.
            height (int, optional): The desired height of the camera feed.
            backends (list[int], optional): List of backend preferences for the camera.
            fps (float, optional): The desired frames per second.
            use_mjpg (bool): Use MJPG codec for performance.
            use_csi (bool): Use CSI camera (IMX219) with GStreamer pipeline.
        """
        self.camera_id = camera_id
        self.cam: cv2.VideoCapture | None = None
        self.use_csi = use_csi

        # Si caméra CSI, utiliser GStreamer pipeline
        if use_csi:
            # Forcer 1080p @ 15fps pour éviter la 4K
            # Ne pas utiliser les paramètres width/height/fps fournis si présents
            width = 1920
            height = 1080
            fps = 15

            print(
                f"🎥 Configuration CSI forcée: {width}x{height} @ {fps} fps (pas de 4K)"
            )

            # Pipeline GStreamer optimisé pour IMX219 sur Jetson
            gst_pipeline = (
                f"nvarguscamerasrc sensor-id={camera_id} ! "
                f"video/x-raw(memory:NVMM), width={width}, height={height}, "
                f"format=NV12, framerate={int(fps)}/1 ! "
                f"nvvidconv flip-method=0 ! "
                f"video/x-raw, width={width}, height={height}, format=BGRx ! "
                f"videoconvert ! "
                f"video/x-raw, format=BGR ! "
                f"appsink"
            )
            print(f"🎥 CSI Camera pipeline: {gst_pipeline}")

            self.cam = cv2.VideoCapture(gst_pipeline, cv2.CAP_GSTREAMER)
            if self.cam is None or not self.cam.isOpened():
                print("⚠️  Échec ouverture caméra CSI, tentative avec V4L2...")
                self.use_csi = False
                self.cam = None

        # Si pas CSI ou échec CSI, utiliser les backends classiques
        if not self.use_csi:
            if backends is None:
                # Backends par défaut selon la plateforme
                # Linux/Jetson: CAP_V4L2
                # Windows: CAP_DSHOW, CAP_MSMF
                # macOS: CAP_ANY
                if hasattr(cv2, "CAP_V4L2"):
                    # Linux/Jetson
                    backends = [cv2.CAP_V4L2, cv2.CAP_ANY]
                else:
                    # Windows/Mac
                    backends = [
                        getattr(cv2, attr, cv2.CAP_ANY)
                        for attr in ("CAP_DSHOW", "CAP_MSMF")
                    ] + [cv2.CAP_ANY]

            selected_backend = None
            for backend in backends:
                self.cam = cv2.VideoCapture(camera_id, backend)
                if self.cam and self.cam.isOpened():
                    selected_backend = backend
                    break
                if self.cam:
                    self.cam.release()

            if self.cam is None or not self.is_opened():
                return

            # Afficher le backend sélectionné pour diagnostic
            backend_names = {
                cv2.CAP_V4L2: "V4L2 (Linux)",
                cv2.CAP_DSHOW: "DSHOW (Windows)",
                cv2.CAP_MSMF: "MSMF (Windows)",
                cv2.CAP_ANY: "ANY (Auto)",
            }
            backend_name = backend_names.get(
                selected_backend, f"Backend {selected_backend}"
            )
            print(f"🎥 Camera backend: {backend_name}")

            # Configuration de la résolution et FPS (UNE SEULE FOIS, après ouverture)
            if width and height:
                # MJPG pour performance (sauf calibration où on laisse le codec par défaut)
                if use_mjpg:
                    fourcc = cv2.VideoWriter_fourcc(*"MJPG")
                    self.cam.set(cv2.CAP_PROP_FOURCC, fourcc)
                # Sinon ne pas définir de codec (laisser le défaut d'OpenCV)

                self.cam.set(cv2.CAP_PROP_FRAME_WIDTH, width)
                self.cam.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

            if fps:
                # Essayer de définir le FPS (peut ne pas fonctionner sur toutes les caméras)
                self.cam.set(cv2.CAP_PROP_FPS, fps)
                actual_fps = self.cam.get(cv2.CAP_PROP_FPS)
                if abs(actual_fps - fps) > 1:
                    print(f"⚠️  FPS demandé: {fps}, FPS obtenu: {actual_fps:.1f}")

                # IMPORTANT: Laisser la caméra se stabiliser après changement de FPS
                # Certaines caméras ont besoin de temps pour ajuster leur buffer interne
                time.sleep(0.2)  # 200ms de stabilisation
            else:
                time.sleep(0.05)

        # Lire quelques frames pour vider le buffer initial
        if self.cam and self.cam.isOpened():
            for _ in range(5):
                self.cam.read()
                time.sleep(0.01)  # Petite pause entre chaque frame

    def is_opened(self) -> bool:
        """Check if the camera is opened.

        Returns:
            bool: True if the camera is opened, False otherwise.
        """
        return self.cam is not None and self.cam.isOpened()

    def set_fps(self, fps: int) -> bool:
        """Change le FPS de la caméra dynamiquement.

        Args:
            fps: Le nouveau FPS à définir

        Returns:
            bool: True si le changement a réussi
        """
        if self.cam is None or not self.is_opened():
            return False

        # Définir le nouveau FPS
        self.cam.set(cv2.CAP_PROP_FPS, fps)
        time.sleep(0.1)  # Temps de stabilisation réduit

        # Vider le buffer (réduit à 3 frames pour optimisation)
        for _ in range(3):
            self.cam.read()

        return True

    def get_resolution(self) -> Tuple[int, int]:
        """Get the current resolution of the camera.

        Returns:
            tuple[int, int]: The width and height of the camera feed.
        """
        if self.cam is None or not self.is_opened():
            return (0, 0)
        return (
            int(self.cam.get(cv2.CAP_PROP_FRAME_WIDTH)),
            int(self.cam.get(cv2.CAP_PROP_FRAME_HEIGHT)),
        )

    def get_camera_info(self) -> Dict[str, Union[int, float]]:
        """Get camera information.

        Returns:
            dict: Dictionary with camera information such as width, height, and fps.
        """
        if self.cam is None or not self.is_opened():
            return {}
        w, h = self.get_resolution()
        return {"width": w, "height": h, "fps": self.cam.get(cv2.CAP_PROP_FPS)}

    @timer
    def read_frame(self) -> Optional[np.ndarray]:
        """Read a frame from the camera.

        Returns:
            np.ndarray[Any, Any] | None: The captured frame or None if unsuccessful.
        """
        if self.cam is None or not self.is_opened():
            return None

        try:
            ret, frame = self.cam.read()
            if not ret:
                # Vérifier si la caméra est toujours connectée
                if not self.cam.isOpened():
                    print("⚠️  Caméra déconnectée détectée dans read_frame()")
                return None
            return frame
        except cv2.error as e:
            print(f"❌ Erreur OpenCV lors de la lecture: {e}")
            return None

    def calibrate(
        self,
        chessboard_size: Tuple[int, int] = (9, 6),
        square_size: float = 1.0,
        num_images: int = 20,
    ) -> Tuple[
        Optional[Any],
        Optional[Any],
        Optional[Any],
        Optional[Any],
    ]:
        """Calibrate the camera using chessboard images.

        Args:
            chessboard_size (tuple[int, int], optional): Nb of inner corners chessboard.
            square_size (float, optional): Size of a square in your defined unit.
            num_images (int, optional): Number of images to capture for calibration.

        Returns:
            tuple: Camera matrix, dist. coeffs, rotation vectors, translation vectors.
        """
        if not self.is_opened():
            return None, None, None, None

        objp = np.zeros((chessboard_size[0] * chessboard_size[1], 3), np.float32)
        objp[:, :2] = np.mgrid[
            0 : chessboard_size[0],
            0 : chessboard_size[1],
        ].T.reshape(-1, 2)
        objp *= square_size

        objpoints, imgpoints = [], []
        captured = 0
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

        coverage_map = np.zeros((
            self.get_resolution()[1] // 20,
            self.get_resolution()[0] // 20,
        ))

        print(f"Capture de {num_images} images.")
        print("CONSEILS : Variez angles, distances et positions")
        print("Appuyez sur 'c' pour capturer, 'q' pour terminer.")

        # Diagnostic: vérifier les propriétés de la caméra (UNE FOIS)
        fourcc = self.cam.get(cv2.CAP_PROP_FOURCC)
        fourcc_str = "".join([chr((int(fourcc) >> 8 * i) & 0xFF) for i in range(4)])
        print(f"🔍 Codec actuel: {fourcc_str}")
        print(f"🔍 Résolution: {self.get_resolution()}")
        print()  # Ligne vide pour séparer

        while captured < num_images:
            frame = self.read_frame()
            if frame is None:
                continue

            # Réduire résolution pour accélérer findChessboardCorners (4x plus rapide)
            scale = 0.5
            small = cv2.resize(frame, None, fx=scale, fy=scale)
            gray_small = cv2.cvtColor(small, cv2.COLOR_BGR2GRAY)

            ret, corners = cv2.findChessboardCorners(
                gray_small,
                chessboard_size,
                cv2.CALIB_CB_ADAPTIVE_THRESH + cv2.CALIB_CB_NORMALIZE_IMAGE,
            )

            # Remettre les coins à l'échelle originale si détectés
            if ret and corners is not None:
                corners = corners / scale
                # Affiner sur l'image PLEINE résolution pour la précision
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                corners = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)

            display = frame.copy()

            coverage_display = cv2.resize(coverage_map, (200, 150))
            coverage_display = (
                coverage_display * 255 / max(1, coverage_map.max())
            ).astype(np.uint8)
            coverage_display = cv2.applyColorMap(coverage_display, cv2.COLORMAP_JET)
            display[10:160, 10:210] = coverage_display

            if ret:
                cv2.drawChessboardCorners(display, chessboard_size, corners, ret)

                sharpness = cv2.Laplacian(gray, cv2.CV_64F).var()

                color = (
                    (0, 255, 0)
                    if sharpness > sharpness_minimum_threshold
                    else (0, 165, 255)
                )
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
                # Les coins sont déjà affinés par cornerSubPix dans la boucle ci-dessus
                center = np.mean(corners, axis=0)[0]
                grid_x = int(center[0] / 20)
                grid_y = int(center[1] / 20)

                if coverage_map[grid_y, grid_x] > coverage_map_maximum_threshold:
                    print("⚠ Zone déjà capturée, variez la position")
                    continue

                objpoints.append(objp)
                imgpoints.append(corners)
                coverage_map[grid_y, grid_x] += 1
                captured += 1
                print(
                    f"✓ Img {captured}/{num_images} capturée (netteté:{sharpness:.0f})",
                )

            elif key == ord("q"):
                break

        cv2.destroyAllWindows()

        if captured < minimum_images_for_calibration:
            print(
                f"Erreur: minimum {minimum_images_for_calibration} images nécessaires",
            )
            return None, None, None, None

        print("Calibration en cours...")

        flags = cv2.CALIB_FIX_PRINCIPAL_POINT + cv2.CALIB_FIX_ASPECT_RATIO

        ret, camera_matrix, dist_coeffs, rvecs, tvecs = cv2.calibrateCamera(
            objpoints,
            imgpoints,
            gray.shape[::-1],
            None,
            None,
            flags=flags,
        )

        if ret:
            total_error = 0
            for i in range(len(objpoints)):
                imgpoints2, _ = cv2.projectPoints(
                    objpoints[i],
                    rvecs[i],
                    tvecs[i],
                    camera_matrix,
                    dist_coeffs,
                )
                error = cv2.norm(imgpoints[i], imgpoints2, cv2.NORM_L2) / len(
                    imgpoints2,
                )
                total_error += error

            mean_error = total_error / len(objpoints)
            print(f"Erreur de reprojection moyenne: {mean_error:.3f} pixels")

            if mean_error > mean_for_bad_calibration:
                print("⚠ ATTENTION : Erreur élevée, recommencez la calibration")
            elif mean_error < mean_for_excellent_calibration:
                print("✓ Excellente calibration!")

        return (
            (camera_matrix, dist_coeffs, rvecs, tvecs)
            if ret
            else (None, None, None, None)
        )

    def release(self) -> None:
        """Release the camera resource."""
        if self.cam:
            self.cam.release()
            self.cam = None
