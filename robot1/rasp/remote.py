from config_loader import CONFIG
from brains import RemoteBrain
from loggerplusplus import Logger
from controllers import RollingBasis
from sensors import Lidar
from remote import PS5Remote
from WS_comms import WServerRouteManager, WSender, WSreceiver, WServer

brain = RemoteBrain(
    logger=Logger(identifier="Remote Brain"),
    rolling_basis=RollingBasis(),
    lidar=Lidar(
        logger=Logger(identifier="Lidar"),
        min_angle=CONFIG.LIDAR_MIN_ANGLE,
        max_angle=CONFIG.LIDAR_MAX_ANGLE,
        unit_angle=CONFIG.LIDAR_ANGLES_UNIT,
        unit_distance=CONFIG.LIDAR_DISTANCES_UNIT,
        min_distance=CONFIG.LIDAR_MIN_DISTANCE_DETECTION,
    ),
    remote=PS5Remote(),
    ws_cmd=WServerRouteManager(
        WSreceiver(use_queue=True), WSender(CONFIG.WS_SENDER_NAME)
    ),
)

ws_server = WServer(
    logger=Logger(identifier="WS Server"),
    host=CONFIG.WS_HOSTNAME,
    port=CONFIG.WS_PORT,
    ping_pong_clients_interval=CONFIG.WS_PING_PONG_INTERVAL,  # TODO: je crois que ça marche pas cette feature
)

for routine in brain.get_tasks():
    ws_server.add_background_task(routine)

ws_server.run()
