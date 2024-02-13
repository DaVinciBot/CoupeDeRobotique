import time

class DummySerial:
    def __init__(self, baudrate):
        self.output_buffer = b''
        self.input_buffer = b''
        self.baudrate = baudrate
        self.out_waiting = False
        

    def write(self, data):
        self.out_waiting = True
        self.output_buffer += data
        #time.sleep(len(data)/self.baudrate)
        self.out_waiting = False
        
    def reset_output_buffer(self):
        self.output_buffer = b''
        

    def read_until(self, signature):
        return self.input_buffer.split(signature)[0]
    
    def dummy_add_input(self, data):
        self.input_buffer += data
        
    def reset_input_buffer(self):
        self.input_buffer = b''