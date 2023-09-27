from flask import Flask, send_from_directory, jsonify
from datetime import datetime


class API:
    """
    API REST pour récupérer les logs + l'état du robot, et servir le site web
    """
    app = Flask(__name__)

    def __init__(self):
        pass

    def run(self):
        self.app.run(host="0.0.0.0")

    @app.route("/api/log/full/latest")
    def api_log():
        log_file = f"logs/{datetime.now().strftime('%Y-%m-%d')}.log"
        with open(log_file, "r") as f:
            log = f.read()
        return jsonify(log)
        

    
    @app.route('api/state/:')
    
    @app.route("/")
    def index():
        return send_from_directory("../", "index.html")

