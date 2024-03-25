from config_loader import CONFIG

# Import from common
from teensy_comms import Teensy, calc_center
from geometry import OrientedPoint, Point, distance
from logger import Logger, LogLevels
from utils import Utils

import struct
import math
import asyncio
from enum import Enum
from dataclasses import dataclass


class Command(Enum):
    GO_TO_POINT = b"\x00"
    CURVE_GO_TO = b"\x01"
    KEEP_CURRENT_POSITION = b"\02"
    DISABLE_PID = b"\03"
    ENABLE_PID = b"\04"
    RESET_POSITION = b"\05"
    SET_PID = b"\06"
    SET_HOME = b"\07"
    STOP = b"\x7E"  # 7E = 126
    INVALID = b"\xFF"


@dataclass
class Instruction:
    cmd: Command
    msg: bytes  # msg is often the same as cmd, but can contain extra info


class RB_Queue:

    tracked_commands = (Command.GO_TO_POINT, Command.CURVE_GO_TO)

    def __init__(self, l: Logger) -> None:
        self.id_counter = 0
        self.last_deleted_id = -1
        self.__queue: list[Instruction] = []

    @staticmethod
    def __is_tracked_command(command: Command) -> bool:
        return command in RB_Queue.tracked_commands

    def __is_tracked_command_at_index(self, __index: int) -> bool:
        return RB_Queue.__is_tracked_command(self.__queue[__index].cmd)

    def _append(self, __object: Instruction) -> int:
        self.__queue.append(__object)
        if RB_Queue.__is_tracked_command(__object.cmd):
            self.id_counter += 1
            return self.id_counter - 1
        else:
            return -1

    def pop(self, __index: int = -1) -> Instruction:
        if self.__is_tracked_command_at_index(__index):
            self.last_deleted_id += 1
        return self.__queue.pop(__index)

    def clear(self) -> None:
        # Count the number of tracked commands in the queue to add to last_deleted_id
        self.last_deleted_id += len(
            [i for i in self.__queue if RB_Queue.__is_tracked_command(i.cmd)]
        )
        self.__queue.clear()

    def delete_up_to(self, __index: int) -> None:
        if self.__is_tracked_command_at_index(__index):
            self.last_deleted_id += 1
        del self.__queue[__index]

    def _insert(self, __index: int, __object: Instruction) -> None:
        """Cannot insert tracked elements to keep things simple"""
        assert not RB_Queue.__is_tracked_command(
            __object.cmd
        ), "Tried to insert tracked command (should only be appended)"
        self.__queue.insert(__index, __object)

    def __getitem__(self, __index) -> Instruction:
        return self.__queue[__index]

    def __len__(self) -> int:
        return len(self.__queue)

    def __str__(self) -> str:
        return str(self.__queue)


class RollingBasis(Teensy):
    ######################
    # Rolling basis init #
    ######################
    def __init__(
        self,
        logger: Logger,
        ser=12678590,
        vid: int = 5824,
        pid: int = 1155,
        baudrate: int = 115200,
        crc: bool = True,
        dummy: bool = False,
    ):
        super().__init__(logger, ser, vid, pid, baudrate, crc, dummy)
        # All position are in the form tuple(X, Y, THETA)
        self.odometrie = OrientedPoint(0.0, 0.0, 0.0)
        self.position_offset = OrientedPoint(0.0, 0.0, 0.0)
        """
        This is used to match a handling function to a message type.
        add_callback can also be used.
        """
        self.messagetype = {
            128: self.rcv_odometrie,  # \x80
            129: self.rcv_action_finish,  # \x81
            130: self.rcv_print,  # \x82
            255: self.unknown_msg,
        }

        self.queue = RB_Queue(self.l)

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
        return OrientedPoint(
            position.x + self.position_offset.x,
            position.y + self.position_offset.y,
            position.theta + self.position_offset.theta,
        )

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

    def rcv_action_finish(self, cmd_finished: bytes):
        self.l.log("Action finished : " + cmd_finished.hex())
        if not self.queue or len(self.queue) == 0:
            self.l.log(
                "Received action_finished but no action in queue", LogLevels.WARNING
            )
            return
        # remove the action that just finished
        for i in range(len(self.queue)):
            if self.queue[i].cmd == cmd_finished:
                self.l.log(
                    f"Removing actions up to {i} from queue : " + str(self.queue[:i])
                )
                self.queue.delete_up_to(i)
                break

        if len(self.queue) == 0:
            self.l.log("Queue is empty, not sending anything")
        else:
            self.l.log("Sending next action in queue")
            self.send_bytes(self.queue[0].msg)

    def unknown_msg(self, msg: bytes):
        self.l.log(f"Teensy does not know the command {msg.hex()}", LogLevels.WARNING)

    def append_to_queue(self, instruction: Instruction) -> int:
        new_id = self.queue._append(instruction)

        if len(self.queue) == 1:
            self.send_bytes(self.queue[0].msg)

        return new_id

    def insert_in_queue(
        self, index: int, instruction: Instruction, force_send: bool = False
    ) -> None:
        """Should only take non tracked instructions"""
        self.queue._insert(index, instruction)

        if len(self.queue) == 1 or force_send:
            self.send_bytes(self.queue[0].msg)

    # TODO: nommage avec majuscule a revoir -> il faut en full minisucule
    @Logger
    def Go_To(
        self,
        position: Point,
        *,  # force keyword arguments
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
        """
        Va à la position donnée en paramètre, return l'id dans la queue de l'action

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
            Command.GO_TO_POINT.value
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

        return self.append_to_queue(Instruction(Command.GO_TO_POINT, msg))

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

        start_time = Utils.get_ts()
        queue_id = self.Go_To(
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

        while (
            Utils.get_ts() - start_time < timeout
            and self.queue.last_deleted_id < queue_id
        ):
            await asyncio.sleep(0.2)

        self.l.log(
            f"Exited Go_To_And_Wait while loop at point: {self.odometrie.__point}",
            LogLevels.INFO,
        )
        if Utils.get_ts() - start_time >= timeout:
            self.l.log(
                "Reached timeout in Go_To_And_Wait, clearing queue", LogLevels.WARNING
            )
            self.Stop_and_clear_queue()
            return 1
        elif (
            distance(
                Point(self.odometrie.__point.x, self.odometrie.__point.y), position
            )
            <= tolerance
        ):
            return 0
        else:
            self.l.log(
                "Unexpected: didn't timeout in Go_To_And_Wait but did not arrive, clearing queue",
                LogLevels.ERROR,
            )
            self.Stop_and_clear_queue()
            return 2

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

        curve_msg = (
            Command.CURVE_GO_TO.value  # command
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
            self.queue._insert(0, Instruction(Command.CURVE_GO_TO, curve_msg))
            self.l.log(str(self.queue))
            self.send_bytes(curve_msg)
        else:
            self.queue._append(Instruction(Command.CURVE_GO_TO, curve_msg))

    # TODO: grosse redondance sur le skip queue, utile de mettre en place un decorateur pour faire ça automatiquement ?
    @Logger
    def Keep_Current_Position(self, skip_queue=False):
        msg = Command.KEEP_CURRENT_POSITION.value
        if skip_queue:
            self.insert_in_queue(
                0, Instruction(Command.KEEP_CURRENT_POSITION, msg), True
            )
        else:
            self.append_to_queue(Instruction(Command.KEEP_CURRENT_POSITION, msg))

    @Logger
    def Clear_Queue(self):
        self.queue.clear()

    @Logger
    def Stop_and_clear_queue(self):
        self.Clear_Queue()
        self.Keep_Current_Position(True)

    @Logger
    def Disable_Pid(self, skip_queue=False):
        msg = Command.DISABLE_PID.value
        if skip_queue:
            self.insert_in_queue(0, Instruction(Command.DISABLE_PID, msg), True)
        else:
            self.queue._append(Instruction(Command.DISABLE_PID, msg))

    @Logger
    def Enable_Pid(self, skip_queue=False):
        msg = Command.ENABLE_PID.value
        if skip_queue:
            self.insert_in_queue(0, Instruction(Command.ENABLE_PID, msg), True)
        else:
            self.append_to_queue(Instruction(Command.ENABLE_PID, msg))

    @Logger
    def Reset_Odo(self, skip_queue=False):
        msg = Command.RESET_POSITION.value
        if skip_queue:
            self.insert_in_queue(0, Instruction(Command.RESET_POSITION, msg), True)
        else:
            self.append_to_queue(Instruction(Command.RESET_POSITION, msg))

    def Set_Home(self, x, y, theta, *, skip_queue=False):
        msg = Command.SET_HOME.value + struct.pack("<fff", x, y, theta)
        if skip_queue:
            self.insert_in_queue(0, Instruction(Command.SET_HOME, msg), True)
        else:
            self.append_to_queue(Instruction(Command.SET_HOME, msg))

    def Set_PID(self, Kp: float, Ki: float, Kd: float, skip_queue=False):
        msg = Command.SET_PID.value + struct.pack("<fff", Kp, Ki, Kd)
        if skip_queue:
            self.insert_in_queue(0, Instruction(Command.SET_PID, msg), True)
        else:
            self.append_to_queue(Instruction(Command.SET_PID, msg))
