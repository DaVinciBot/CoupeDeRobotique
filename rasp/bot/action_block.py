import time
from typing import Union

class Lock:
    
    def __init__(self,action_id : int, delay : int = 0) -> None:
        self.delay = delay
        self.id = action_id
        
    def execute(self):
        time.sleep(self.delay/1000)
        
class Action:
    
    def __init__(self,id,msg) -> None:
        self.id = id
        self.msg = msg
        
class Instruction:
    def __init__(self,block_name, process : Union[Lock,Action]) -> None:
        self.block_name = block_name
        self.process = process