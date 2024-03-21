from config_loader import CONFIG

# Import from common
from teensy_comms import Teensy
from geometry import OrientedPoint, Point, distance
from logger import Logger

import struct
import math
import time
import asyncio


class RollingBasis(Teensy):
    ######################
    # Rolling basis init #
    ######################
    def __init__(
        self,
        ser=12678590,
        vid: int = 5824,
        pid: int = 1155,
        baudrate: int = 115200,
        crc: bool = True,
        dummy: bool = False,
    ):
        super().__init__(ser, vid, pid, baudrate, crc, dummy)
        # All position are in the form tuple(X, Y, THETA)
        self.odometrie = OrientedPoint(0.0, 0.0, 0.0)
        self.position_offset = OrientedPoint(0.0, 0.0, 0.0)
        self.current_action = None
        self.isGo_To = False
        """
        This is used to match a handling function to a message type.
        add_callback can also be used.
        """
        self.messagetype = {
            128: self.rcv_odometrie,  # \x80
            129: self.rcv_action_finish,  # \x81
            130: self.rcv_print,  # \x82
            255: self.unknowed_msg,
        }

        self.queue = []

    #####################
    # Position handling #
    #####################
    def true_pos(self, position: OrientedPoint) -> OrientedPoint:
        """
        _summary_

        :param position: _description_
        :type position: OrientedPoint
        :return: _description_
        :rtype: OrientedPoint
        """
        return OrientedPoint(position.x+self.position_offset.x,position.y+self.position_offset.y,position.theta+self.position_offset.theta)

    #############################
    # Received message handling #
    #############################
    def rcv_print(self, msg: bytes):
        self.l.log("Teensy says : " + msg.decode("ascii", errors="ignore"))

    def rcv_odometrie(self, msg: bytes):
        self.odometrie = OrientedPoint(
            struct.unpack("<f", msg[0:4])[0],
            struct.unpack("<f", msg[4:8])[0],
            struct.unpack("<f", msg[8:12])[0],
        )

    def rcv_action_finish(self, msg: bytes):
        self.l.log("Action finished : " + msg.hex())
        if msg == self.Command.GoToPoint:
            self.isGo_To = False
        if not self.queue or len(self.queue) == 0:
            self.l.log("Received action_finished but no action in queue", 1)
            return
        # remove the action that just finished
        for i in range(len(self.queue)):
            if list(self.queue[i].keys())[0] == msg:
                self.l.log(f"Removing action {i} from queue : " + str(self.queue[i]))
                self.queue.pop(i)
                break
        # TODO: jamais execute car on le teste deja dans le if not self.queue or len(self.queue) == 0:
        if len(self.queue) == 0:
            self.l.log("Queue is empty")
            self.current_action = None
            return
        self.send_bytes(list(self.queue[0].values())[0])
        self.current_action = list(self.queue[0].keys())[0]
        self.l.log("Sending next action in queue")

    def unknowed_msg(self, msg: bytes):
        self.l.log(f"Teensy does not know the command {msg.hex()}", 1)

    #########################
    # User facing functions #
    #########################
    # TODO: class command a definir ailleurs ?
    class Command:
        GoToPoint = b"\x00"
        CurveGoTo = b"\x01"
        KeepCurrentPosition = b"\02"
        DisablePid = b"\03"
        EnablePid = b"\04"
        ResetPosition = b"\05"
        SetPID = b"\06"
        SetHome = b"\07"
        Stop = b"\x7E"  # 7E = 126
        Invalid = b"\xFF"

    # TODO: nommage avec majuscule a revoir -> il faut en full minisucule
    @Logger
    def Go_To(
        self,
        position: Point,
        *,  # force keyword arguments
        skip_queue=False,
        is_forward: bool = True,
        max_speed: int = 150,
        next_position_delay: int = 100,
        action_error_auth: int = 50,
        traj_precision: int = 50,
        correction_trajectory_speed: int = 80,
        acceleration_start_speed: int = 80,
        acceleration_distance: float = 10,
        deceleration_end_speed: int = 80,
        deceleration_distance: float = 10,
    ) -> None:
        """
        Va à la position donnée en paramètre

        :param position: la position en X et Y (et theta)
        :type position: Point
        :param is_forward: en avant (false) ou en arrière (true), defaults to False
        :type direction: bool, optional
        :param speed: Vitesse du déplacement, defaults to b'\x64'
        :type speed: bytes, optional
        :param next_position_delay: delay avant la prochaine position, defaults to 100
        :type next_position_delay: int, optional
        :param action_error_auth: l'erreur autorisé dans le déplacement, defaults to 20
        :type action_error_auth: int, optional
        :param traj_precision: la précision du déplacement, defaults to 50
        :type traj_precision: int, optional
        """
        pos = Point(
            position.x + self.position_offset.x, position.y + self.position_offset.y
        )
        msg = (
            self.Command.GoToPoint
            + struct.pack("<f", pos.x)
            + struct.pack("<f", pos.y)
            + struct.pack("<?", is_forward)
            + struct.pack("<B", max_speed)
            + struct.pack("<H", next_position_delay)
            + struct.pack("<H", action_error_auth)
            + struct.pack("<H", traj_precision)
            + struct.pack("<B", correction_trajectory_speed)
            + struct.pack("<B", acceleration_start_speed)
            + struct.pack("<f", acceleration_distance)
            + struct.pack("<B", deceleration_end_speed)
            + struct.pack("<f", deceleration_distance)
        )
        # https://docs.python.org/3/library/struct.html#format-characters
        if skip_queue or len(self.queue) == 0:
            self.queue.insert(0, {self.Command.GoToPoint: msg})
            self.send_bytes(msg)
        else:
            self.queue.append({self.Command.GoToPoint: msg})
            
        self.isGo_To = True

    @Logger
    async def Go_To_And_Wait(
        self,
        position: Point,
        *,  # force keyword arguments
        tolerance: float = 5,
        timeout: float = -1,  # in seconds
        skip_queue: bool = False,
        is_forward: bool = True,
        max_speed: int = 150,
        next_position_delay: int = 100,
        action_error_auth: int = 50,
        traj_precision: int = 50,
        correction_trajectory_speed: int = 80,
        acceleration_start_speed: int = 80,
        acceleration_distance: float = 10,
        deceleration_end_speed: int = 80,
        deceleration_distance: float = 10,
    ) -> int:
        """Waits to go over timeout or finish the queue (by finishing movement or being interrupted)

        Args:
            position (Point): Target.
            tolerance (float): Distance to be within to return a success if not timed out.
            timeout (float): Max time to wait in s, -1 for no limit. Defaults to -1.
            is_forward (bool, optional): _description_. Defaults to True.
            max_speed (int, optional): _description_. Defaults to 150.
            next_position_delay (int, optional): _description_. Defaults to 100.
            action_error_auth (int, optional): _description_. Defaults to 50.
            traj_precision (int, optional): _description_. Defaults to 50.
            correction_trajectory_speed (int, optional): _description_. Defaults to 80.
            acceleration_start_speed (int, optional): _description_. Defaults to 80.
            acceleration_distance (float, optional): _description_. Defaults to 10.
            deceleration_end_speed (int, optional): _description_. Defaults to 80.
            deceleration_distance (float, optional): _description_. Defaults to 10.

        Returns:
            int: 0 if finished normally, 1 if timed out, 2 if finished without timeout but not at targret position
        """

        start_time = time.time()
        self.Go_To(
            position,
            skip_queue=skip_queue,
            is_forward=is_forward,
            max_speed=max_speed,
            next_position_delay=next_position_delay,
            action_error_auth=action_error_auth,
            traj_precision=traj_precision,
            correction_trajectory_speed=correction_trajectory_speed,
            acceleration_start_speed=acceleration_start_speed,
            acceleration_distance=acceleration_distance,
            deceleration_end_speed=deceleration_end_speed,
            deceleration_distance=deceleration_distance,
        )

        # len(self.queue)>0 is very generic, might not trigger enough if other commands try to execute before this is other
        while time.time() - start_time < timeout and (len(self.queue) > 0 or not self.isGo_To):
            await asyncio.sleep(0.2)

        if time.time() - start_time > timeout:
            self.Stop_and_clear_queue()
            return 1
        elif distance(self.odometrie.__point, position) > tolerance:
            return 2
        else:
            return 0

    @Logger
    def curve_go_to(
        self,
        destination: OrientedPoint,
        corde: float,
        interval: int,
        *,  # force keyword arguments
        skip_queue=False,
        direction: bool = False,
        speed: int = 150,
        next_position_delay: int = 100,
        action_error_auth: int = 20,
        traj_precision: int = 50,
        test: bool = False,
    ) -> None:
        """Go to a point with a curve"""

        middle_point = OrientedPoint(
            (self.odometrie.x + destination.x) / 2,
            (self.odometrie.y + destination.y) / 2,
        )
        # alpha est l'angle entre la droite (position, destination) et l'axe des ordonnées (y)
        alpha = math.atan2(
            destination.y - self.odometrie.y, destination.x - self.odometrie.x
        )
        # theta est l'angle entre la droite (position, destination) et l'axe des abscisses (x)
        theta = math.pi / 2 - alpha

        third_point = OrientedPoint(
            middle_point.x + math.cos(theta) * corde,
            middle_point.y + math.sin(theta) * corde,
        )

        center = calc_center(self.odometrie, third_point, destination)
        destination = self.true_pos(destination)
        center = self.true_pos(center)
        if test:
            return center
        curve_msg = (
            self.Command.CurveGoTo  # command
            + struct.pack("<ff", destination.x, destination.y)  # target_point
            + struct.pack("<ff", center.x, center.y)  # center_point
            + struct.pack("<H", interval)  # interval (distance between two points)
            + struct.pack("<?", direction)  # direction
            + struct.pack("<H", speed)  # speed
            + struct.pack("<H", next_position_delay)  # delay
            + struct.pack("<H", action_error_auth)  # error_auth
            + struct.pack("<H", traj_precision)  # precision
        )
        if skip_queue or len(self.queue) == 0:
            self.l.log("Skipping Queue ...")
            self.queue.insert(0, {self.Command.CurveGoTo: curve_msg})
            self.l.log(self.queue)
            self.send_bytes(curve_msg)
        else:
            self.queue.append({self.Command.CurveGoTo: curve_msg})

    # TODO: grosse redondance sur le skip queue, utile de mettre en place un decorateur pour faire ça automatiquement ?
    @Logger
    def Keep_Current_Position(self, skip_queue=False):
        msg = self.Command.KeepCurrentPosition
        if skip_queue:
            self.queue.insert(0, {self.Command.KeepCurrentPosition: msg})
            self.send_bytes(msg)
        else:
            self.queue.append({self.Command.KeepCurrentPosition: msg})

    @Logger
    def Clear_Queue(self):
        self.queue.clear()

    @Logger
    def Stop_and_clear_queue(self):
        self.Clear_Queue()
        self.Keep_Current_Position(True)

    @Logger
    def Disable_Pid(self, skip_queue=False):
        msg = self.Command.DisablePid
        if skip_queue or len(self.queue) == 0:
            self.queue.insert(0, {self.Command.DisablePid: msg})
            self.send_bytes(msg)
        else:
            self.queue.append({self.Command.DisablePid: msg})

    @Logger
    def Enable_Pid(self, skip_queue=False):
        msg = self.Command.EnablePid
        if skip_queue or len(self.queue) == 0:
            self.queue.insert(0, {self.Command.EnablePid: msg})
            self.send_bytes(msg)
        else:
            self.queue.append({self.Command.EnablePid: msg})

    @Logger
    def Reset_Odo(self, skip_queue=False):
        msg = self.Command.ResetPosition
        if skip_queue or len(self.queue) == 0:
            self.queue.insert(0, {self.Command.ResetPosition: msg})
            self.send_bytes(msg)
        else:
            self.queue.append({self.Command.ResetPosition: msg})

    def Set_Home(self, x, y, theta, *, skip_queue=False):
        msg = self.Command.SetHome + struct.pack("<fff", x, y, theta)
        if skip_queue or len(self.queue) == 0:
            self.queue.insert(0, {self.Command.SetHome: msg})
            self.send_bytes(msg)
        else:
            self.queue.append({self.Command.SetHome: msg})

    def Set_PID(self, Kp: float, Ki: float, Kd: float, skip_queue=False):
        msg = self.Command.SetPID + struct.pack("<fff", Kp, Ki, Kp)
        if skip_queue or len(self.queue) == 0:
            self.queue.insert(0, {self.Command.SetPID: msg})
            self.send_bytes(msg)
        else:
            self.queue.append({self.Command.SetPID: msg})
