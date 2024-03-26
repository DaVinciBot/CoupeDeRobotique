# Import from common
from logger import Logger, LogLevels
from geometry import OrientedPoint, Point
from arena import MarsArena,Plants_zone
from WS_comms import WSclientRouteManager, WSmsg
from brain import Brain
from utils import Utils


# Import from local path
from sensors import Lidar
from controllers import RollingBasis,Actuators
import asyncio
from geometry import Polygon
from config_loader import CONFIG


class Robot1Brain(Brain):
    def __init__(
        self,
        logger: Logger,
        ws_cmd: WSclientRouteManager,
        ws_log: WSclientRouteManager,
        ws_lidar: WSclientRouteManager,
        ws_odometer: WSclientRouteManager,
        ws_camera: WSclientRouteManager,
        actuators : Actuators,
        rolling_basis: RollingBasis,
        lidar: Lidar,
        arena: MarsArena,
    ) -> None:
        super().__init__(logger, self)

        # self.lidar_scan = []
        self.lidar_values_in_distances = []
        self.lidar_angles = (90, 180)
        self.odometer = None
        self.camera = {}
        
        # to delete, only use for completion 
        # self.rolling_basis:  RollingBasis 
        # self.actuators : Actuators
        # self.arena: MarsArena

    """
        Routines
    """

    """
        Get controllers / sensors feedback (odometer / lidar + extern (camera))
    """

    def ACS_by_distances(self):
        if self.arena.check_collision_by_distances(
            self.lidar_values_in_distances, self.odometer
        ):
            self.rolling_basis.stop_and_clear_queue()
            # It is the currently running action's responsibility to detect the stop if it needs to

    @Brain.task(refresh_rate=0.5)
    async def lidar_scan_distances(self):
        # Warning, currently hard-coded for 3 values/degree
        self.lidar_values_in_distances = self.lidar.scan_distances(
            start_angle=self.lidar_angles[0],
            end_angle=self.lidar_angles[1],
        )

        self.ACS_by_distances()

    # @Brain.task(refresh_rate=0.5)
    # async def lidar_scan(self):
    #     scan = self.lidar.scan_to_absolute_cartesian(
    #         robot_pos=self.rolling_basis.odometrie
    #     )

    #     self.lidar_scan = [[p.x, p.y] for p in scan]

    @Brain.task(refresh_rate=0.5)
    async def odometer_update(self):
        self.odometer = OrientedPoint(
            self.rolling_basis.odometrie.x,
            self.rolling_basis.odometrie.y,
            self.rolling_basis.odometrie.theta,
        )

    @Brain.task(refresh_rate=0.5)
    async def get_camera(self):
        msg = await self.ws_camera.receiver.get()
        if msg != WSmsg():
            self.camera = msg.data

    """
        Send controllers / sensors feedback (odometer / lidar)
    """

    # @Brain.task(refresh_rate=1)
    # async def send_lidar_scan_to_server(self):
    #     if self.lidar_scan:
    #         await self.ws_lidar.sender.send(
    #             WSmsg(msg="lidar_scan", data=self.lidar_scan)
    #         )

    @Brain.task(refresh_rate=1)
    async def send_odometer_to_server(self):
        if self.odometer is not None:
            await self.ws_odometer.sender.send(
                WSmsg(msg="odometer", data=self.odometer)  # To check
            )

    @Brain.task(refresh_rate=0.1)
    async def main(self):
        # Check cmd
        cmd = await self.ws_cmd.receiver.get()

        if cmd != WSmsg():
            self.logger.log(f"New cmd received: {cmd}", LogLevels.INFO)

            # Handle it (implemented only for Go_To and Keep_Current_Position)
            if cmd.msg == "Go_To":
                self.rolling_basis.stop_and_clear_queue()
                self.rolling_basis.go_to(
                    OrientedPoint(cmd.data[0], cmd.data[1], cmd.data[2]),
                    skip_queue=True,
                )
            elif cmd.msg == "Keep_Current_Position":
                self.rolling_basis.stop_and_clear_queue()
            else:
                self.logger.log(
                    f"Command not implemented: {cmd.msg} / {cmd.data}",
                    LogLevels.ERROR,
                )

    @Brain.task()
    async def go_to_and_wait_test(self):
        await asyncio.sleep(1)
        result = await self.rolling_basis.go_to_and_wait(
            Point(50, 50), tolerance=5, timeout=20
        )

        if result == 0:
            self.logger.log("Success of movement test")
        elif result == 1:
            self.logger.log("Timed out of movement test")
        elif result == 2:
            self.logger.log("Error moving: didn't reach destination")
             
    @Brain.task(process=False, run_on_start=False, timeout=70)        
    async def plant_stage(self):
    
        async def go_best_zone(plant_zones : list[Plants_zone]):
            destination_point = None
            destination_plant_zone = None
            for plant_zone in plant_zones:
                point = self.arena.compute_go_to_destination(start_point=self.odometer,zone=plant_zone)
                if self.arena.enable_go_to(point):
                    destination_point = point
                    destination_plant_zone = plant_zone
                    break
            if destination_point != None and await self.rolling_basis.go_to_and_wait(position = destination_point,timeout=10) == 0:      
                return True,destination_plant_zone
            return False,destination_plant_zone
        
        
        is_arrived : bool = False
        for pin in CONFIG.GODS_HAND_SERVO_PINS:
                self.actuators.update_servo(pin,CONFIG.GOD_HAND_SERVO_OPEN_ANGLE)
        while not is_arrived:
            plant_zones = self.arena.sort_pickup_zone(self.odometer)
            is_arrived, destination_plant_zone = await go_best_zone(plant_zones)
            if is_arrived:
                for pin in CONFIG.GODS_HAND_SERVO_PINS:
                    self.actuators.update_servo(pin,CONFIG.GOD_HAND_SERVO_CLOSE_ANGLE)
                destination_plant_zone.take_plant(5)
                
        is_arrived : bool = False
        while not is_arrived:
            plant_zones = self.arena.sort_drop_zone(self.odometer)
            is_arrived, destination_plant_zone = await go_best_zone(plant_zones)
            if is_arrived:
                for pin in CONFIG.GODS_HAND_SERVO_PINS:
                    self.actuators.update_servo(pin,CONFIG.GOD_HAND_SERVO_OPEN_ANGLE)

    @Brain.task(process=False, run_on_start=True, refresh_rate=0.1)
    async def main(self):
        # Check cmd
        cmd = await self.ws_cmd.receiver.get()

        if cmd != WSmsg():
            self.logger.log(f"New cmd received: {cmd}", LogLevels.INFO)

            # Handle it (implemented only for Go_To and Keep_Current_Position)
            if cmd.msg == "Go_To":
                self.rolling_basis.queue = []
                self.rolling_basis.Go_To(
                    position=Point(cmd.data[0], cmd.data[1]),
                    max_speed=cmd.data[2],
                    next_position_delay=cmd.data[3],
                    action_error_auth=cmd.data[4],
                    traj_precision=cmd.data[5],
                    correction_trajectory_speed=cmd.data[6],
                    acceleration_start_speed=cmd.data[7],
                    acceleration_distance=cmd.data[8],
                    deceleration_end_speed=cmd.data[9],
                    deceleration_distance=cmd.data[10],
                    skip_queue=True,
                )
            elif cmd.msg == "Keep_Current_Position":
                self.rolling_basis.queue = []
                self.rolling_basis.Keep_Current_Position()

            elif cmd.msg == "Set_PID":
                self.rolling_basis.queue = []
                self.rolling_basis.Set_PID(Kp=cmd.data[0], Ki=cmd.data[1], Kd=cmd.data[2])

            else:
                self.logger.log(
                    f"Command not implemented: {cmd.msg} / {cmd.data}",
                    LogLevels.WARNING,
                )
                
                
        
        
            
            
        
