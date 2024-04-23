from typing import List
import copy 
import pandas as pd

from agents.agent import Agent
from market_engine.order_book import OrderBook
from market_engine.order import LimitOrder
from market_engine.market_analytics import MarketAnalytics
from util.types import MessageType
from util.logger import DummyLogger


class ExchangeAgent(Agent):
    def __init__(self, id:str, symbol:str, random_state:7):
        super().__init__(id, random_state)
        self.symbol = symbol
        self.market_analytics = MarketAnalytics(self.symbol, depth = 5)
    
    def kernel_init(self, kernel, logger=DummyLogger()):
        super().kernel_init(kernel)
        self.oracle = self.kernel.oracle
        self.logger = logger
        self.order_book = OrderBook(self.symbol, self, self.logger)
        self.logger.info(f"Exchange agent {self.id} initialized")
    
    def receive_market_orders(self, current_time, market_orders:List[LimitOrder]):
        self.current_time = current_time
        for market_order in market_orders:
            self.order_book.send_order(market_order)        
    
    def receive_message(self, current_time, message):
        super().receive_message(current_time, message)
        #self.logger.info(f"Exchange agent {self.id} received message {message}")
        
        message_type = message.type
        if message_type in [MessageType.LIMIT_ORDER, MessageType.MARKET_ORDER]:
            self.order_book.send_order(message.content)
        #elif message_type == MessageType.CANCEL_ORDER:
        #    self.order_book.cancel_order(message.content["order_id"])
        #elif message_type == MessageType.MODIFY_ORDER:
        #    self.order_book.modify_order(message.content["order"])
        elif message_type == MessageType.MARKET_DATA:
            return copy.deepcopy(self.market_analytics)
        
    def send_message(self, recipient_id, message, delay=0):
        #self.logger.info(f"Exchange agent {self.id} sent message {message} to {recipient_id}")
        message_type = message.type
        if message_type in [MessageType.ORDER_ACCEPTED, MessageType.ORDER_CANCELLED, MessageType.ORDER_EXECUTED]:
            super().send_message(recipient_id, message, delay)
    
    def update_market_analytics(self):
        self.market_analytics.update(self.current_time, self.order_book)

    def log_order_book(self, analytics=True):
        self.logger.info(f"Order book at time {self.current_time}")
        self.logger.info(self.order_book.__str__(depth=5))
        if analytics:
            self.logger.info(self.market_analytics.__str__())


