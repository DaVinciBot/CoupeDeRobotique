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
import time


class Command(Enum):
    GO_TO_POINT = b"\x00"
    CURVE_GO_TO = b"\x01"
    KEEP_CURRENT_POSITION = b"\02"
    DISABLE_PIDS = b"\03"
    ENABLE_PIDS = b"\04"
    RESET_POSITION = b"\05"
    SET_PIDS = b"\06"
    SET_HOME = b"\07"
    GET_ORIENTATION = b"\08"
    STOP = b"\x7E"  # 7E = 126
    INVALID = b"\xFF"


@dataclass
class Instruction:
    cmd: Command
    msg: bytes  # msg is often the same as cmd, but can contain extra info

    def __str__(self):
        return f"cmd:{self.cmd}, msg:{self.msg}"


class RB_Queue:

    tracked_commands = (Command.GO_TO_POINT, Command.CURVE_GO_TO)
    
    """
    Represents a queue of instructions for a rolling basis controller.

    Attributes:
        tracked_commands (tuple): A tuple of tracked commands.
        id_counter (int): Counter for generating unique IDs for tracked commands.
        last_deleted_id (int): ID of the last deleted tracked command.
        __queue (list[Instruction]): The underlying list to store the instructions.

    Methods:
        __init__(self, logger: Logger) -> None: Initializes a new instance of the RB_Queue class.
        append(self, __object: Instruction) -> int: Appends an instruction to the queue.
        pop(self, __index: int = -1) -> Instruction: Removes and returns an instruction from the queue.
        clear(self) -> None: Clears the queue.
        delete_up_to(self, __index: int) -> None: Deletes instructions up to the specified index.
        insert(self, __index: int, __object: Instruction) -> None: Inserts an instruction at the specified index.
        __getitem__(self, __index) -> Instruction: Returns the instruction at the specified index.
        __len__(self) -> int: Returns the number of instructions in the queue.
        __str__(self) -> str: Returns a string representation of the queue.
    """

    def __init__(self, logger: Logger) -> None:
        self.id_counter = 0
        self.last_deleted_id = -1
        self.__queue: list[Instruction] = []

    @staticmethod
    def __is_tracked_command(command: Command) -> bool:
        return command in RB_Queue.tracked_commands

    def __is_tracked_command_at_index(self, __index: int) -> bool:
        return RB_Queue.__is_tracked_command(self.__queue[__index].cmd)

    def append(self, __object: Instruction) -> int:
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
        for i in range(__index + 1):
            if self.__is_tracked_command_at_index(0):
                self.last_deleted_id += 1
            del self.__queue[0]

    def insert(self, __index: int, __object: Instruction) -> None:
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
        ser: int = CONFIG.ROLLING_BASIS_TEENSY_SER,
        crc: bool = CONFIG.TEENSY_CRC,
        vid: int = CONFIG.TEENSY_VID,
        pid: int = CONFIG.TEENSY_PID,
        baudrate: int = CONFIG.TEENSY_BAUDRATE,
        dummy: bool = CONFIG.TEENSY_DUMMY,
    ):
        super().__init__(
            logger, ser=ser, vid=vid, pid=pid, baudrate=baudrate, crc=crc, dummy=dummy
        )
        self.odometrie: OrientedPoint = OrientedPoint((0.0, 0.0), 0.0)
        self.position_offset = OrientedPoint((0.0, 0.0), 0.0)
        """
        This is used to match a handling function to a message type.
        add_callback can also be used.
        """
        self.messagetype = {
            128: self.rcv_odometrie,  # \x80
            129: self.rcv_action_finish,  # \x81
            130: self.rcv_print,  # \x82
            255: self.rcv_unknown_msg,
        }

        self.queue = RB_Queue(self.logger)

    #####################
    # Position handling #
    #####################
    def true_pos(self, position: OrientedPoint) -> OrientedPoint:
        """
        enables to correct the position using a fixed offset if required

        :param position: _description_
        :type position: OrientedPoint
        :return: _description_
        :rtype: OrientedPoint
        """
        return OrientedPoint(
            (position.x + self.position_offset.x, position.y + self.position_offset.y),
            position.theta + self.position_offset.theta,
        )

    #############################
    # Received message handling #
    #############################
    def rcv_print(self, msg: bytes):
        self.logger.log(
            "Teensy says : " + msg.decode("ascii", errors="ignore"), LogLevels.INFO
        )

    def rcv_odometrie(self, msg: bytes):
        self.odometrie = OrientedPoint(
            (struct.unpack("<f", msg[0:4])[0], struct.unpack("<f", msg[4:8])[0]),
            struct.unpack("<f", msg[8:12])[0],
        )

    def rcv_action_finish(self, cmd_finished: bytes):
        self.logger.log("Action finished : " + cmd_finished.hex(), LogLevels.INFO)
        if not self.queue or len(self.queue) == 0:
            self.logger.log(
                "Received action_finish but no action in queue", LogLevels.WARNING
            )
            return
        # remove actions up to the one that just finished
        for i in range(len(self.queue)):
            if self.queue[i].cmd.value == cmd_finished:
                self.logger.log(
                    f"Removing actions up to {i} from queue : "
                    + str(self.queue[: i + 1]),
                    LogLevels.INFO,
                )
                self.queue.delete_up_to(i)
                break

        if len(self.queue) == 0:
            self.logger.log("Queue is empty, not sending anything", LogLevels.INFO)
        else:
            self.logger.log("Sending next action in queue")
            self.send_bytes(self.queue[0].msg)

    def rcv_unknown_msg(self, msg: bytes):
        self.logger.log(
            f"Teensy does not know the command {msg.hex()}", LogLevels.WARNING
        )

    def append_to_queue(
        self, instruction: Instruction, skip_and_clear_queue=False
    ) -> int:

        if skip_and_clear_queue:
            self.queue.clear()

        new_id = self.queue.append(instruction)

        if len(self.queue) == 1:
            self.send_bytes(self.queue[0].msg)

        return new_id

    def insert_in_queue(
        self, index: int, instruction: Instruction, force_send: bool = False
    ) -> None:
        """Should only take non tracked instructions. To use carefully, adding an action in front of an unfinished one may trigger the unfinished one again afterwards."""
        self.queue.insert(index, instruction)

        if len(self.queue) == 1 or force_send:
            self.send_bytes(self.queue[0].msg)

    @Logger
    def go_to(
        self,
        position: Point,
        *,  # force keyword arguments
        skip_and_clear_queue: bool = False,
        forward: bool = True,
        relative: bool = False,
        max_speed: int = 160,
        next_position_delay: int = 100,
        action_error_auth: int = 30,
        traj_precision: int = 30,
        correction_trajectory_speed: int = 160,
        acceleration_start_speed: int = 160,
        acceleration_distance: float = 0,
        deceleration_end_speed: int = 160,
        deceleration_distance: float = 0,
    ) -> int:
        """
        Va à la position donnée en paramètre, return l'id dans la queue de l'action

        :param position: la position en X et Y (et theta)
        :type position: Point
        :param forward: en avant (True) ou en arrière (False), defaults to True
        :type direction: bool, optional
        :param relative: en absolu (False) ou en relatif (True), defaults to False
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
        self.logger.log(
            f"go_to {'relative' if relative else 'absolute'}: {position}",
            LogLevels.DEBUG,
        )
        pos = (
            Point(
                position.x + self.position_offset.x, position.y + self.position_offset.y
            )
            if not relative
            else Point(
                math.cos(self.odometrie.theta) * position.x
                - math.sin(self.odometrie.theta) * position.y
                + self.position_offset.x
                + self.odometrie.x,
                math.sin(self.odometrie.theta) * position.x
                + math.cos(self.odometrie.theta) * position.y
                + self.position_offset.y
                + self.odometrie.y,
            )
        )
        msg = (
            Command.GO_TO_POINT.value
            + struct.pack("<f", pos.x)
            + struct.pack("<f", pos.y)
            + struct.pack("<?", forward)
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

        return self.append_to_queue(
            Instruction(Command.GO_TO_POINT, msg),
            skip_and_clear_queue=skip_and_clear_queue,
        )

    @Logger
    async def go_to_and_wait(
        self,
        position: Point,
        *,  # force keyword arguments
        skip_and_clear_queue: bool = False,
        tolerance: float = 5,
        timeout: float = -1,  # in seconds
        forward: bool = True,
        relative: bool = False,
        max_speed: int = 160,
        next_position_delay: int = 100,
        action_error_auth: int = 30,
        traj_precision: int = 30,
        correction_trajectory_speed: int = 160,
        acceleration_start_speed: int = 160,
        acceleration_distance: float = 0,
        deceleration_end_speed: int = 160,
        deceleration_distance: float = 0,
    ) -> int:
        """Waits to go over timeout or finish the queue (by finishing movement or being interrupted)

        Args:
            position (Point): Target.
            tolerance (float): Distance to be within to return a success if not timed out.
            timeout (float): Max time to wait in s, -1 for no limit. Defaults to -1.
            forward (bool, optional): _description_. Defaults to True.
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
            int: 0 if finished normally, 1 if timed out, 2 if finished without timeout but not at target position
        """

        target_to_compare = (
            Point(
                position.x + self.position_offset.x, position.y + self.position_offset.y
            )
            if not relative
            else Point(
                math.cos(self.odometrie.theta) * position.x
                - math.sin(self.odometrie.theta) * position.y
                + self.position_offset.x
                + self.odometrie.x,
                math.sin(self.odometrie.theta) * position.x
                + math.cos(self.odometrie.theta) * position.y
                + self.position_offset.y
                + self.odometrie.y,
            )
        )

        start_time = Utils.get_ts()
        queue_id = self.go_to(
            position,
            skip_and_clear_queue=skip_and_clear_queue,
            forward=forward,
            relative=relative,
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
            timeout < 0 or Utils.time_since(start_time) < timeout
        ) and self.queue.last_deleted_id < queue_id:
            await asyncio.sleep(0.1)

        if Utils.time_since(start_time) >= timeout and timeout >= 0:
            self.logger.log(
                f"Reached timeout in Go_To_And_Wait, clearing queue, at: {self.odometrie}, {distance(self.odometrie, target_to_compare)} away",
                LogLevels.WARNING,
            )
            self.stop_and_clear_queue()
            return 1
        elif distance(self.odometrie, target_to_compare) <= tolerance:
            self.logger.log(
                f"Reached target in go_to_and_wait, at: {self.odometrie}",
                LogLevels.INFO,
            )
            return 0
        else:  # Should only mean ACS triggered or unplanned behaviour
            self.logger.log(
                f"Didn't timeout in Go_To_And_Wait but did not arrive, at: {self.odometrie}, targeting : {target_to_compare}, {distance(self.odometrie, target_to_compare)} away",
                LogLevels.WARNING,
            )
            # self.stop_and_clear_queue()
            return 2

    @Logger
    def get_orientation(
        self,
        position: Point,
        *,  # force keyword arguments
        forward: bool = True,
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

        pos = Point(
            position.x + self.position_offset.x, position.y + self.position_offset.y
        )
        msg = (
            Command.GET_ORIENTATION.value
            + struct.pack("<ff", pos.x, pos.y)
            + struct.pack("<?", forward)
            + struct.pack("<B", max_speed)
            + struct.pack(
                "<HHH", next_position_delay, action_error_auth, traj_precision
            )
            + struct.pack("<BB", correction_trajectory_speed, acceleration_start_speed)
            + struct.pack("<f", acceleration_distance)
            + struct.pack("<B", deceleration_end_speed)
            + struct.pack("<f", deceleration_distance)
        )
        # https://docs.python.org/3/library/struct.html#format-characters

        self.append_to_queue(Instruction(Command.GET_ORIENTATION, msg))

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
            (
                (self.odometrie.x + destination.x) / 2,
                (self.odometrie.y + destination.y) / 2,
            )
        )
        # alpha est l'angle entre la droite (position, destination) et l'axe des ordonnées (y)
        alpha = math.atan2(
            destination.y - self.odometrie.y, destination.x - self.odometrie.x
        )
        # theta est l'angle entre la droite (position, destination) et l'axe des abscisses (x)
        theta = math.pi / 2 - alpha

        third_point = OrientedPoint(
            (
                middle_point.x + math.cos(theta) * corde,
                middle_point.y + math.sin(theta) * corde,
            )
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
            self.logger.log("Skipping Queue ...")
            self.queue.insert(0, Instruction(Command.CURVE_GO_TO, curve_msg))
            self.logger.log(str(self.queue))
            self.send_bytes(curve_msg)
        else:
            self.queue.append(Instruction(Command.CURVE_GO_TO, curve_msg))

    # TODO: grosse redondance sur le skip queue, utile de mettre en place un decorateur pour faire ça automatiquement ?
    @Logger
    def keep_current_pos(self, skip_queue=False):
        msg = Command.KEEP_CURRENT_POSITION.value
        if skip_queue:
            self.insert_in_queue(
                0, Instruction(Command.KEEP_CURRENT_POSITION, msg), True
            )
        else:
            self.append_to_queue(Instruction(Command.KEEP_CURRENT_POSITION, msg))

    @Logger
    def clear_queue(self):
        self.queue.clear()

    @Logger
    def stop_and_clear_queue(self):
        self.clear_queue()
        self.keep_current_pos(True)

    @Logger
    def disable_pid(self, skip_queue=False):
        msg = Command.DISABLE_PIDS.value
        if skip_queue:
            self.insert_in_queue(0, Instruction(Command.DISABLE_PIDS, msg), True)
        else:
            self.queue.append(Instruction(Command.DISABLE_PIDS, msg))

    @Logger
    def enable_pid(self, skip_queue=False):
        msg = Command.ENABLE_PIDS.value
        if skip_queue:
            self.insert_in_queue(0, Instruction(Command.ENABLE_PIDS, msg), True)
        else:
            self.append_to_queue(Instruction(Command.ENABLE_PIDS, msg))

    @Logger
    def reset_odo(self, skip_queue=False):
        """reset teensy's odo to (0,0,0)

        Args:
            skip_queue (bool, optional): wether to skip the queue or not. Defaults to False.
        """
        msg = Command.RESET_POSITION.value
        if skip_queue:
            self.insert_in_queue(0, Instruction(Command.RESET_POSITION, msg), True)
        else:
            self.append_to_queue(Instruction(Command.RESET_POSITION, msg))

    def set_odo(self, new_odo: Point, *, skip_queue=False):
        msg = Command.SET_HOME.value + struct.pack(
            "<fff",
            new_odo.x,
            new_odo.y,
            new_odo.theta if isinstance(new_odo, OrientedPoint) else 0.0,
        )
        if skip_queue:
            self.insert_in_queue(0, Instruction(Command.SET_HOME, msg), True)
        else:
            self.append_to_queue(Instruction(Command.SET_HOME, msg))

    def set_pids(
        self,
        l_Kp: float,
        l_Ki: float,
        l_Kd: float,
        r_Kp: float,
        r_Ki: float,
        r_Kd: float,
        skip_queue=False,
    ):
        msg = Command.SET_PIDS.value + struct.pack(
            "<ffffff", l_Kp, l_Ki, l_Kd, r_Kp, r_Ki, r_Kd
        )
        if skip_queue:
            self.queue.insert(0, Instruction(Command.SET_PIDS, msg))
        else:
            self.append_to_queue(Instruction(Command.SET_PIDS, msg))
