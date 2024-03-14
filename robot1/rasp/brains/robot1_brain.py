# Import from common
from logger import Logger, LogLevels
from geometry import OrientedPoint, Point
from arena import MarsArena
from WS_comms import WSclientRouteManager, WSmsg
from brain import Brain
from utils import Utils

# Import from local path
from sensors import Lidar
from controllers import RollingBasis
from config_loader import CONFIG


class Robot1Brain(Brain):
    def __init__(
        self,
        logger: Lidar,
        ws_cmd: WSclientRouteManager,
        ws_log: WSclientRouteManager,
        ws_lidar: WSclientRouteManager,
        ws_odometer: WSclientRouteManager,
        ws_camera: WSclientRouteManager,
        rolling_basis: RollingBasis,
        lidar: Lidar,
        arena: MarsArena,
    ) -> None:
        super().__init__(logger, self)

        self.lidar_scan = []

    @Brain.routine(refresh_rate=0.5)
    async def lidar_scan(self):
        scan = self.lidar.scan_to_absolute_cartesian(
            robot_pos=self.rolling_basis.odometrie
        )
        self.lidar_scan = scan

    @Brain.routine(refresh_rate=1)
    async def send_lidar_to_server(self):
        await self.ws_lidar.sender.send(
            WSmsg(msg="lidar_scan", data=[[p.x, p.y] for p in self.lidar_scan])
        )

    @Brain.routine(refresh_rate=1)
    async def send_odometer_to_server(self):
        await self.ws_odometer.sender.send(
            WSmsg(
                msg="odometer",
                data=[
                    self.rolling_basis.odometrie.x,
                    self.rolling_basis.odometrie.y,
                    self.rolling_basis.odometrie.theta,
                ],
            )
        )

    @Brain.routine(refresh_rate=0.5)
    async def main(self):
        # Get the message from routes
        cmd = await self.ws_cmd.receiver.get()
        camera = await self.ws_camera.receiver.get()

        # Log states
        self.logger.log(f"CMD state: {cmd}", LogLevels.INFO)
        self.logger.log(f"New message from camera: {camera}", LogLevels.INFO)

        if cmd != WSmsg():
            # New command received
            self.logger.log(
                f"Command received: {cmd.msg}, {cmd.sender}, {len(cmd.data)}",
                LogLevels.INFO,
            )
            # Handle it (implemented only for Go_To and Keep_Current_Position)
            if cmd.msg == "Go_To":
                # Verify if the point is accessible
                if MarsArena.enable_go_to(
                    starting_point=Point(
                        self.rolling_basis.odometrie.x, self.rolling_basis.odometrie.y
                    ),
                    destination_point=Point(cmd.data[0], cmd.data[1]),
                ):
                    self.rolling_basis.Go_To(
                        OrientedPoint(cmd.data[0], cmd.data[1], cmd.data[2])
                    )
            elif cmd.msg == "Keep_Current_Position":
                self.rolling_basis.Keep_Current_Position()
            else:
                self.logger.log(
                    f"Command not implemented: {cmd.msg} / {cmd.data}",
                    LogLevels.WARNING,
                )

    # pas super logique que ce soit ici mais c'est le seul endroit où tout est acessible. Mélange de la la notion de robot de partie à mon sens
    Brain.stage(0, 70)

    def get_plant(self):
        running = True
        while running:
            sorted_zones = self.arena.sort_pickup_zone()
            if not go_to_zone(sorted_zones):
                print("kill la stage")
            # ramasser plante et delay
            # faire la même chose pour toute les zones de la phase avec les actuators correspondants
            else:
                print("log un message d'erreur et kill stage")

            # si le temps est sup à une variable définie dans config alors running = False
            def go_to_zone(zones):
                for zone in sorted_zones:
                    destination_point = self.arena.compute_go_to_destination(zone)
                    if self.arena.enable_go_to(
                        destination_point
                    ):  # ajouter le check de la position du robot adverse
                        if not self.rolling_basis.Go_To(
                            destination_point
                        ):  # à lancer surement dans une nouvelle fonction enrobée avec un timeout et await. Retourne true destinatinon reached and false otherwise
                            go_to_zone(zones)
                    return True
                return False
