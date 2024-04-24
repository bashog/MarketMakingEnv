from typing import List
import copy 
import pandas as pd

from agents.agent import Agent
from market_engine.order_book import OrderBook
from market_engine.order import LimitOrder
from market_engine.market_analytics import MarketAnalytics
from util.message import Message
from util.types import MessageType
from util.logger import DummyLogger


class ExchangeAgent(Agent):
    def __init__(self, id:str, symbol:str):
        super().__init__(id)
        self.symbol = symbol
        self._market_analytics = MarketAnalytics(self.symbol, depth = 5)
    
    def kernel_init(self, kernel, logger=DummyLogger()):
        super().kernel_init(kernel, logger)
        self._oracle = self._kernel._oracle
        self._order_book = OrderBook(self.symbol, self, self._logger)
    
    def receive_market_orders(self, current_time, market_orders:List[LimitOrder]):
        self._current_time = current_time
        for market_order in market_orders:
            self._order_book.send_order(market_order)        
    
    def receive_message(self, current_time, message):
        super().receive_message(current_time, message)
        #self.logger.info(f"Exchange agent {self.id} received message {message}")
        
        message_type = message.type
        if message_type in [MessageType.LIMIT_ORDER, MessageType.MARKET_ORDER]:
            self._order_book.send_order(message.content)
        #elif message_type == MessageType.CANCEL_ORDER:
        #    self.order_book.cancel_order(message.content["order_id"])
        #elif message_type == MessageType.MODIFY_ORDER:
        #    self.order_book.modify_order(message.content["order"])
        elif message_type == MessageType.REQUEST_MARKET_DATA:
            market_data = copy.deepcopy(self._market_analytics)
            response_message = Message(MessageType.MARKET_DATA, market_data)
            self.send_message(message.content, response_message)
            
    def send_message(self, recipient_id, message, delay=pd.Timedelta(seconds=0)):
        if recipient_id != "Market":
            self._logger.info(f"Exchange agent {self.id} sent message {message} to {recipient_id}")
            message_type = message.type
            if message_type in [MessageType.ORDER_ACCEPTED, MessageType.ORDER_CANCELLED, MessageType.ORDER_EXECUTED, MessageType.MARKET_DATA]:
                super().send_message(recipient_id, message, delay)
    
    def update_market_analytics(self):
        self._market_analytics.update(self._current_time, self._order_book)
        #self.log_order_book()

    def log_order_book(self, analytics=True):
        self._logger.info(f"Order book at time {self._current_time}")
        self._logger.info(self._order_book.__str__(depth=5))
        if analytics:
            self._logger.info(self._market_analytics.__str__())


