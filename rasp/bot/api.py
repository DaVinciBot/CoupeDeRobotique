from flask import Flask, send_from_directory, jsonify
from flask_classful import FlaskView
from datetime import datetime


app = Flask(__name__)

"""
class API:
    \"""
    API REST pour récupérer les logs + l'état du robot, et servir le site web
    \"""
    

    def __init__(self, state):
        self.state = state

    @app.route("/api/log/full/latest")
    def api_log():
        log_file = f"logs/{datetime.now().strftime('%Y-%m-%d')}.log"
        with open(log_file, "r") as f:
            log = f.read()
        return jsonify(log)
        
    
    @app.route("/api/state")
    def api_state():
        return jsonify("")
    
    @app.route("/")
    def index():
        return 

    @app.route("/api/lidar")
    def get_lidar():
        with open("lidar.json", "r") as f:
            log = f.read()
        return jsonify(log)
"""


class MainView(FlaskView):
    def __init__(self) -> None:
        pass

    def index(self):
        return send_from_directory("../", "index.html")

    @app.route("/api/log/full/latest")
    def log(self):
        log_file = f"logs/{datetime.now().strftime('%Y-%m-%d')}.log"
        with open(log_file, "r") as f:
            log = f.read()
        return jsonify(log)


if __name__ == "__main__":
    MainView.register(app, route_base="/")
    app.run(host="0.0.0.0")
