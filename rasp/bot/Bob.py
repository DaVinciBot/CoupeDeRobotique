from bot.Com import RollingBasis, Actuators
from bot.Lidar import Lidar
from bot.Logger import Logger
from bot.action_block import Lock,Action,Instruction
from bot.State import instructions

class Bob:
    
    def __init__(self) -> None:
        
        """
        Initialize the Bob object.

        Attributes:
        - l: Logger object for logging.
        - rolling_basis: RollingBasis object for controlling the rolling basis.
        - actuators: Actuators object for controlling actuators.
        - Lidar: Lidar object for Lidar functionality.
        - instructions: List of Instruction objects representing the instructions to execute.
        - is_on: Flag indicating whether the robot is turned on.
        - is_obstacle: Flag indicating whether an obstacle is detected.
        - SERVOS_PIN: List of servo pins.
        - ULTRASONICS_PINS: List of ultrasonic sensor pins.
        - is_moving: Flag indicating whether the robot is currently moving.
        - run_auth: Flag indicating authorization for the robot to move.
        - go_to_verif: Flag indicating trajectory verification requirement.
        - enable_lidar_collision_check: Flag indicating whether Lidar collision check is enabled.
        """
        
        self.l = Logger()
        # separated units
        self.rolling_basis = RollingBasis()
        self.actuators = Actuators()
        self.Lidar = Lidar()
        self.is_on = False # must be activated by the game
        self.is_obstacle = False
        # actuator's config
        self.SERVOS_PIN = [5] # the maxmimun number of servos is 12
        self.ULTRASONICS_PINS = [(12,14)]
        
        # state
        self.is_moving = False
        self.is_obstacle = True # does the lidar detects an obstacle
        self.run_auth = False # when true the robot is authorized to move
        self.go_to_verif = False # when true trajectory is checked to avoid forbidden moves
        self.enable_lidar_collision_check = False  # when true stops when an obstacle is detected
              
    def handle_call_back(self,block_name,msg:bytes)->None:
        """
        Handle callback messages from different blocks.

        Args:
        - block_name: Name of the block sending the message.
        - msg: Bytes message received.

        Returns:
        - None
        """
        self.l.log(f"Action finished on {block_name} : {msg.hex()}")
        try : length = len(instructions)
        except : length = 0
        found = False
        if length == 0 :
            self.l.log(f"received action finished {msg} from {block_name} but instruction is empty")
            return
        for i in range(length):
            if instructions[i].block_name == block_name and self.isAction() and instructions[i].process.id == msg:
                self.found = True
                instructions.pop(i) # delete the finished instruction
                self.l.log(f"removed instruction {i} from instructions : {instructions[i]}")
                self.delete_lock(block_name=block_name,action_id=msg,first_i=i) # if exists delete the lock corresponding to the finished action
                self.send_action(block_name=block_name)
        if not found:
            self.l.log(f"Received the action finished {msg.hex()} but couldn't find an action with the same id in instructions",1)
        if len(instructions)==0:
            self.l.log("instructions is empty")
                
                
    def delete_lock(self,block_name, action_id, first_i)->bool:
        """if exists delete the lock with the given block_name and action_id and return True. Stops if an action with the same block_name is detected 

        Args:
            block_name (_type_): the name of the block
            action_id (_type_): the id of the action
            first_i (_type_): the index to start from

        Returns:
            bool: wether a lock have been deleted or not
        """
        for i in range(first_i,len(instructions)):
            if instructions[i].block_name == block_name:
                if self.isLock() and instructions[i].process.id == action_id:
                    instructions.pop(i)
                    return True
                elif not self.isLock():
                    return False
        return False
    
    def send_action(self,block_name)->bool:
        """
        Send an action to the specified block.

        Args:
        - block_name: Name of the block to send the action to.

        Returns:
        - bool: True if the action was sent successfully, False otherwise.
        """
        for i in range(len(instructions)):
            if instructions[i].block_name != block_name and self.isLock():
                return False
            if instructions[i].block_name == block_name and self.isAction():
                if block_name == self.rolling_basis.name:
                    self.rolling_basis.send_bytes(instructions[i].process.msg)
                if block_name == self.actuators.name:
                    self.actuators.send_bytes(instructions[i].process.msg)
                else:
                    self.l.log(f"tried to send an instruction to {block_name} whereas the bord isn't known",1)
                    return False
                return True
        return False          
                         
    def ACS(self):
        """
        ACS stands for Anti Collision System. Stop the bot and continue navigation when possible. Sould evolve toward an avoidance system
        Returns:
        - None  
        """
        self.rolling_basis.Keep_Current_Position()
        while True:
            if not self.is_obstacle():
                for i in range(len(instructions)):
                    if instructions[i].block_name != self.rolling_basis.name and self.isLock():
                        break
                    elif instructions[i].block_name == self.rolling_basis.name and self.isAction():
                        self.rolling_basis.send_bytes(instructions[i].process.msg)
                break
                        
    def isAction(self,i):
        """
        Check if the process at index 'i' in instructions is an Action.

        Args:
        - i: Index in the instruction list.

        Returns:
        - bool: True if the process is an Action, False otherwise.
        """
        return isinstance(instructions[i].process,Action)
    
    def isLock(self,i):
        """
        Check if the process at index 'i' in instruction is a Lock.

        Args:
        - i: Index in the instruction list.

        Returns:
        - bool: True if the process is a Lock, False otherwise.
        """
        return isinstance(instructions[i].process,Lock)
    
    
    
    def main(self):
        while self.is_on:
            if self.is_obstacle:
                self.ACS()