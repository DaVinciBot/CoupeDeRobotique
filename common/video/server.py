"""Minimal MJPEG streaming server used for debugging video feeds."""

from __future__ import annotations

import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any

from loggerplusplus import Logger

try:
    import cv2
except ModuleNotFoundError:
    cv2: Any = None  # pylint: disable=invalid-name


_logger = Logger(identifier="MJPEGHandler", follow_logger_manager_rules=True)


class MJPEGHandler(BaseHTTPRequestHandler):
    """Serve MJPEG frames over HTTP.

    Attributes:
        current_img: The current image frame to be served.
    """

    current_img = None
    """The current image frame to be served."""

    def send_index(self) -> None:
        """Send a basic HTML page embedding the MJPEG stream."""
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(
            b"""
            <html>
            <head></head>
            <body>
            <img src=\"http://localhost:8001/cam.mjpg\" />
            </body>
            </html>
            """,
        )

    def do_GET(self) -> None:  # pylint: disable=invalid-name
        """Serve the MJPEG stream or index page depending on the path.

        Raises:
            RuntimeError: If OpenCV is unavailable for an MJPEG request.
        """
        if self.path.endswith(".mjpg"):
            if cv2 is None:
                raise RuntimeError(
                    "OpenCV is required to serve MJPEG streams. "
                    "Install the optional 'opencv-python' dependency.",
                )
            self.send_response(200)
            self.send_header(
                "Content-type",
                "multipart/x-mixed-replace; boundary=--jpgboundary",
            )
            self.end_headers()
            while True:
                try:
                    if self.current_img is None:
                        _logger.warning("[VIDEO] No image to send")
                        continue
                    dat = cv2.imencode(".jpg", self.current_img)[1].tobytes()
                    self.wfile.write(b"--jpgboundary")
                    self.send_header("Content-type", "image/jpeg")
                    self.send_header("Content-length", str(len(dat)))
                    self.end_headers()
                    self.wfile.write(dat)
                    time.sleep(0.1)
                except KeyboardInterrupt:
                    break
                except Exception as e:  # noqa: BLE001
                    _logger.error(f"[VIDEO] Streaming error: {e}")
                    break
            return
        if self.path.endswith(".html"):
            self.send_index()
            return


# I want to pass an object to the handler, but I can't figure out how to do it


def start_video_server() -> None:
    """Start the MJPEG HTTP server in the foreground."""
    _logger.info("[VIDEO] Starting server on port 8001")
    MJPEGHandler.current_img = None
    httpd = HTTPServer(("0.0.0.0", 8001), MJPEGHandler)

    # make the server ctrl+c-able
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        httpd.server_close()
        _logger.info("[VIDEO] Server stopped")


def spawn_video_server() -> None:
    """Launch the video server in a background thread."""
    import threading  # noqa: PLC0415

    t = threading.Thread(target=start_video_server)
    try:
        t.start()
    except RuntimeError as e:
        _logger.error(f"[VIDEO] Failed to spawn server: {e}")
        t.join(timeout=1)


if __name__ == "__main__":
    start_video_server()
