from typing import List
import queue

from market_engine.data_oracle import DataOracle
from util.message import Message
from util.logger import setup_logger, DummyLogger

class Kernel:
    def __init__(self, random_state = 7, log_name = None):
        self.random_state = random_state
        if log_name is not None:
            self.logger = setup_logger(log_name)
        else:
            self.logger = DummyLogger()
        self.logger.info("-"*50)
        self.logger.info("Kernel initialized")

    def run(self, oracle, exchangeAgent):
        # Init Loop Message
        self.messages = queue.PriorityQueue()
        
        # Initialize data oracle that feed market data
        self.oracle = oracle
        self.oracle.kernel_init(self)
        self.start_time = self.oracle.get_start_time()
        self.end_time = self.oracle.get_end_time()
        self.currentTime = self.start_time
        self.timestamps = self.oracle.get_timestamps()
        self.logger.info(f"Start time: {self.start_time}, End time: {self.end_time}")
        
        # Init ExchangeAgent
        self.exchangeAgent = exchangeAgent
        self.exchangeAgent.kernel_init(self, self.logger)
        
        # Init TradingAgent
        
        
        
        # Main loop
        for timestamp in self.timestamps:
            self.logger.info(f"-----------------------------------")
            self.logger.info(f"Processing timestamp {timestamp}")
            self.exchangeAgent.log_order_book()
            self.currentTime = timestamp
            # Process market order
            self.logger.info(f"Processing market orders")
            market_orders = self.oracle.get_orders(timestamp)
            self.exchangeAgent.receive_market_orders(timestamp, market_orders)
            self.exchangeAgent.update_market_analytics()
            self.exchangeAgent.log_order_book()
            # Process 

              
    # Communication methods
    def send_message(self, sender:str, recipient:str, message:Message, delay:int=0):
        sent_time = self.currentTime #+ cumpute delay of agent
        deliver_time = sent_time #+ latency
        if recipient != "":
            self.messages.put((deliver_time, (recipient, message.type, message)))
    
    def get_exchange_id(self):
        return self.exchangeAgent.id
        

