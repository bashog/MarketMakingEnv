from typing import List
import queue
import random
import pandas as pd

from market_engine.data_oracle import DataOracle
from util.message import Message
from util.logger import setup_logger, DummyLogger
from util.message import MessageType

class Kernel:
    def __init__(self, log_name = None):
        self._logger = setup_logger(log_name) if log_name else DummyLogger()
        self._logger.info("-"*50)
        self._logger.info("Kernel initialized")
        
        # About time
        self._analytics_interval = pd.Timedelta(seconds=0.1) 
        self._data_request_interval = pd.Timedelta(seconds=0.1)
        self._agent_activation_interval = pd.Timedelta(seconds=0.5)
        
        # Agent registry
        self._agents = {}
    
    def register_agent(self, agent):
        self._agents[agent.id] = agent
        
    def pre_run(self, oracle, exchange_agent, trading_agent):
        # Init Loop Message
        self._messages = queue.PriorityQueue()
        
        # Initialize data oracle that feed market data
        self._oracle = oracle
        self._oracle.kernel_init(self)
        self._logger.info(f"Oracle initialized")
        self._start_time = self._oracle.get_start_time()
        self._end_time = self._oracle.get_end_time()
        self._current_time = self._start_time
        self._logger.info(f"Start time: {self._start_time}, End time: {self._end_time}")
        
        # Init Exchange Agent
        self._exchange_agent = exchange_agent
        self._exchange_agent.kernel_init(self, self._logger)
        self.register_agent(self._exchange_agent)
        self._next_analytics_time = self._start_time
        self._logger.info(f"Exchange agent {self._exchange_agent.id} initialized")
        
        # Pre-send orders
        self._oracle.kernel_start(self._start_time)
        self._logger.info(f"Oracle started and pre-sent orders")
        
        # Init Trading Agent
        self._trading_agent = trading_agent
        self._trading_agent.kernel_init(self, self._logger)
        self._trading_agent.kernel_start(self._start_time)
        self._next_data_request_time = self._start_time
        self._next_agent_activation_time = self._start_time
        self.register_agent(self._trading_agent)
        self._logger.info(f"Trading agent {self._trading_agent.id} initialized")
        
    def run(self, oracle, exchange_agent, trading_agent):
        self.pre_run(oracle, exchange_agent, trading_agent)
        
        # Main loop
        while self._current_time <= self._end_time:
            self.process_messages()
            # This part to be improved to have autonomous agents
            if self._current_time >= self._next_analytics_time:
                self._exchange_agent.update_market_analytics()
                self._next_analytics_time += self._analytics_interval
            if self._current_time >= self._next_data_request_time:
                self._trading_agent.request_market_data()
                self._next_data_request_time += self._data_request_interval
            if self._current_time >= self._next_agent_activation_time:
                self._trading_agent.request_wake_up()
                self._next_agent_activation_time += self._agent_activation_interval
            self.advance_time()
        
    def process_messages(self):
        while not self._messages.empty():
            message_time, (sender, recipient, message) = self._messages.get()
            if message_time <= self._current_time:
                self._agents[recipient].receive_message(self._current_time, message)
            else:
                self._messages.put((message_time, (sender, recipient, message)))
                break
    
    def advance_time(self):
        if not self._messages.empty():
            next_message_time = self._messages.queue[0][0]
            self._current_time = min(next_message_time, self._end_time)
              
    # Communication methods
    def send_message(self, sender:str, recipient:str, message:Message, delay=pd.Timedelta(seconds=0)):
        deliver_time = self._current_time + delay
        self._messages.put((deliver_time, (recipient, message.type, message)))
    
    def get_exchange_id(self):
        return self._exchange_agent.id
        

