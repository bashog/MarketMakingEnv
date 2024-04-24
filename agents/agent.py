from kernel import Kernel
import pandas as pd
from util.logger import DummyLogger

class Agent:
    def __init__(self, id:str):
        self._id = id
        self._kernel = None
        self._current_time = None
    
    @property
    def id(self):
        return self._id
    
    # Kernel lifecycle methods
    def kernel_init(self, kernel, logger=DummyLogger()):
        self._kernel = kernel
        self._logger = logger
    
    def kernel_start(self, start_time):
        self._current_time = start_time
    
    def kernel_stop(self):
        pass
    
    # Communication methods
    def receive_message(self, current_time, message):
        self._current_time = current_time
    
    def send_message(self, recipient_id, message, delay = pd.Timedelta(seconds=0)):
        self._kernel.send_message(self.id, recipient_id, message, delay = delay)
        