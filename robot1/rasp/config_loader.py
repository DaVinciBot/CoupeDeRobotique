import pathlib
import json
import sys
import os


def load_json_file(file_path):
    try:
        with open(file_path) as config:
            file_json = json.load(config)
    except FileNotFoundError:
        try:
            with open(os.path.join(BASE_DIR, file_path)) as config:
                file_json = json.load(config)
        except Exception:
            raise

    return file_json


# Get usefully directories
BASE_DIR = pathlib.Path(__file__).resolve().parent
ROOT_DIR = BASE_DIR.parent
COMMON_DIR = str(ROOT_DIR / "common")
sys.path.append(
    COMMON_DIR
)  # Add common directory to the path (to be able to import common modules)

# Load configuration file
CONFIG_FILE_PATH = os.path.join(ROOT_DIR, "configuration.json")
CONFIG_STORE = load_json_file(CONFIG_FILE_PATH)


class Config:
    BASE_DIR = BASE_DIR
    ROOT_DIR = ROOT_DIR
    COMMON_DIR = COMMON_DIR

    CURRENT_FOLDER_NAME = BASE_DIR.name

    # General config
    GENERAL_CONFIG = CONFIG_STORE["general"]
    GENERAL_WS_CONFIG = GENERAL_CONFIG["ws"]

    WS_PORT = int(GENERAL_WS_CONFIG["port"])
    WS_LIDAR_ROUTE = GENERAL_WS_CONFIG["lidar_route"]
    WS_LOG_ROUTE = GENERAL_WS_CONFIG["log_route"]
    WS_ODOMETER_ROUTE = GENERAL_WS_CONFIG["odometer_route"]

    # Specific config
    SPECIFIC_CONFIG = CONFIG_STORE[CURRENT_FOLDER_NAME]
    SPECIFIC_WS_CONFIG = SPECIFIC_CONFIG["ws"]

    WS_SENDER_NAME = SPECIFIC_WS_CONFIG["sender_name"]
    WS_SERVER_IP = SPECIFIC_WS_CONFIG["server_ip"]


class Configuration(dict):
    def from_object(self, obj):
        for attr in dir(obj):

            if not attr.isupper():
                continue

            self[attr] = getattr(obj, attr)

        self.__dict__ = self


APP_CONFIG = Configuration()
APP_CONFIG.from_object(Config)
