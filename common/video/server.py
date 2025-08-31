"""Minimal MJPEG streaming server used for debugging video feeds."""

from __future__ import annotations

import time
from http.server import BaseHTTPRequestHandler, HTTPServer

import cv2


class MJPEGHandler(BaseHTTPRequestHandler):
    """Serve MJPEG frames over HTTP."""

    current_img = None

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

    def do_GET(self) -> None:
        """Serve the MJPEG stream or index page depending on the path."""
        if self.path.endswith(".mjpg"):
            self.send_response(200)
            self.send_header(
                "Content-type",
                "multipart/x-mixed-replace; boundary=--jpgboundary",
            )
            self.end_headers()
            while True:
                try:
                    if self.current_img is None:
                        print("No image to send")
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
                    print(e)
                    break
            return
        if self.path.endswith(".html"):
            self.send_index()
            return


# I want to pass an object to the handler, but I can't figure out how to do it


def start_video_server() -> None:
    """Start the MJPEG HTTP server in the foreground."""
    print("Starting video server")
    MJPEGHandler.current_img = None
    httpd = HTTPServer(("0.0.0.0", 8001), MJPEGHandler)

    # make the server ctrl+c-able
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        httpd.server_close()
        print("Server stopped")


def spawn_video_server() -> None:
    """Launch the video server in a background thread."""
    import threading

    t = threading.Thread(target=start_video_server)
    try:
        t.start()
    except Exception as e:  # noqa: BLE001
        print(e)
        t.join(timeout=1)


if __name__ == "__main__":
    start_video_server()
