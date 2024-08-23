from enum import Enum
#from logger import Logger, LogLevels

class TeensyGpioManager:
    
    class TypeActuator(Enum):
        UNKNOWN = 0
        SERVO = 1
        STEPPER = 2
        LCD = 3
    
    def __init__(self, nb_pin : int, logger):  
        self.logger = logger
        self.nb_pin = nb_pin
        self.gpios = {}
        
    def __str__(self):
        return f"TeensyGpioManager : {self.gpios}"
        
        
    def is_available_gpio(self, pin: int):
        return not pin in self.gpios
    
    def is_valid_gpio(self, pin: int, type_actuator: TypeActuator = TypeActuator.UNKNOWN):
        if not pin in self.gpios or self.gpios[pin] != type_actuator:
            return False
        return True
    
    def add_gpio(self, pin: int, type_actuator: TypeActuator = TypeActuator.UNKNOWN):
        if not self.is_available_gpio(pin):
            #self.logger.log(f"Pin {pin} is already used", LogLevels.ERROR)
            return False
        elif pin <0 or pin > self.nb_pin:
            #self.logger.log(f"Pin {pin} is not valid. Must be in range [0,{self.nb_pin}]", LogLevels.ERROR)
            return False
        self.gpios[pin] = type_actuator
        return True
        
    def get_type_gpio(self, pin : int):
        if pin in self.gpios:
            return self.gpios[pin]
        else:
            #self.logger.log(f"Pin {pin} is not used", LogLevels.ERROR)
            return None