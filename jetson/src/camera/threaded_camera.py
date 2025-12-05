"""Threaded camera module for high-performance video capture."""

import threading
import time
from typing import Optional

import cv2
import numpy as np

from src.camera import Camera


class ThreadedCamera(Camera):
    """Camera class with threaded frame reading for better performance.
    
    This class continuously reads frames in a background thread, allowing
    the main thread to retrieve the latest frame without waiting for I/O.
    """

    def __init__(
        self,
        camera_id: int,
        width: Optional[int] = None,
        height: Optional[int] = None,
        backends: Optional[list] = None,
        buffer_size: int = 1,
    ) -> None:
        """Initialize the threaded camera.

        Args:
            camera_id (int): The ID of the camera to use.
            width (int, optional): The desired width of the camera feed.
            height (int, optional): The desired height of the camera feed.
            backends (list[int], optional): List of backend preferences.
            buffer_size (int): Number of frames to buffer (1 = latest only).
        """
        super().__init__(camera_id, width, height, backends)
        
        self.buffer_size = buffer_size
        self.frame = None
        self.frame_lock = threading.Lock()
        self.stopped = False
        self.thread = None
        
        # Statistiques de performance
        self.frames_read = 0
        self.frames_dropped = 0
        self.last_fps_time = time.time()
        self.fps = 0.0
        
        if self.is_opened():
            self.start()

    def start(self) -> None:
        """Start the background thread for reading frames."""
        if self.thread is None or not self.thread.is_alive():
            self.stopped = False
            self.thread = threading.Thread(target=self._update_frame, daemon=True)
            self.thread.start()
            # Attendre que la première frame soit disponible
            time.sleep(0.1)

    def _update_frame(self) -> None:
        """Background thread function that continuously reads frames."""
        while not self.stopped:
            if self.cam is None or not self.cam.isOpened():
                break
                
            ret, frame = self.cam.read()
            
            if ret:
                with self.frame_lock:
                    # Si on a déjà une frame non lue, on compte ça comme drop
                    if self.frame is not None:
                        self.frames_dropped += 1
                    self.frame = frame
                    self.frames_read += 1
                    
                # Calculer le FPS de lecture
                current_time = time.time()
                if current_time - self.last_fps_time >= 1.0:
                    self.fps = self.frames_read / (current_time - self.last_fps_time)
                    self.frames_read = 0
                    self.last_fps_time = current_time
            else:
                # Petite pause si la lecture échoue
                time.sleep(0.001)

    def read_frame(self) -> Optional[np.ndarray]:
        """Read the latest frame from the buffer.

        Returns:
            np.ndarray | None: The latest captured frame or None if unavailable.
        """
        with self.frame_lock:
            return self.frame.copy() if self.frame is not None else None

    def get_stats(self) -> dict:
        """Get camera performance statistics.
        
        Returns:
            dict: Statistics including FPS and dropped frames.
        """
        return {
            "read_fps": self.fps,
            "frames_dropped": self.frames_dropped,
            "buffer_size": self.buffer_size,
        }

    def release(self) -> None:
        """Stop the background thread and release the camera."""
        self.stopped = True
        if self.thread is not None:
            self.thread.join(timeout=1.0)
        super().release()

    def __del__(self):
        """Ensure resources are released on deletion."""
        self.release()
