from io import StringIO
import cv2, time
from http.server import HTTPServer, BaseHTTPRequestHandler

img_path = "test.jpg"


class MJPEGHandler(BaseHTTPRequestHandler):
    current_img = None

    def send_index(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(
            b"""
            <html>
            <head></head>
            <body>
            <img src="http://localhost:8001/cam.mjpg" />
            </body>
            </html>
            """
        )

    def do_GET(self):
        if self.path.endswith(".mjpg"):
            self.send_response(200)
            self.send_header(
                "Content-type", "multipart/x-mixed-replace; boundary=--jpgboundary"
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
                    self.send_header("Content-length", str(dat.__len__()))
                    self.end_headers()
                    self.wfile.write(dat)
                    time.sleep(0.1)
                except KeyboardInterrupt:
                    break
                except Exception as e:
                    print(e)
                    break
            return
        if self.path.endswith(".html"):
            self.send_index()
            return


# I want to pass an object to the handler, but I can't figure out how to do it


def start_video_server():
    print("Starting video server")
    MJPEGHandler.current_img = None
    httpd = HTTPServer(("0.0.0.0", 8001), MJPEGHandler)

    # make the server ctrl+c-able
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        httpd.server_close()
        print("Server stopped")


def spawn_video_server():
    import threading

    t = threading.Thread(target=start_video_server)
    try:
        t.start()
    except Exception as e:
        print(e)
        t.join(timeout=1)


if __name__ == "__main__":
    start_video_server()
