from kernel import Kernel
import pandas as pd

class Agent:
    def __init__(self, id:str, random_state:str):

        self.id = id
        self.random_state = random_state
        
        # Kernel to be attached to the agent
        self.kernel = None
        
        # Current time of the agent
        self.current_time = None
    
    # Kernel lifecycle methods
    def kernel_init(self, kernel):
        self.kernel = kernel
    
    def kernel_start(self, start_time):
        self.current_time = start_time
    
    def kernel_stop(self):
        pass
    
    # Communication methods
    def receive_message(self, current_time, message):
        self.current_time = current_time
    
    def send_message (self, recipient_id, message, delay = 0):
        self.kernel.send_message(self.id, recipient_id, message, delay = delay)
        