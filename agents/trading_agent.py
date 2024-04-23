from collections import defaultdict
from copy import deepcopy

from agent.agent import Agent
from market_engine.order import LimitOrder, MarketOrder, FilledOrder
from util.types import Side, MessageType
from util.message import Message

class TradingAgent(Agent):
    
    def __init__(self, id:str, random_state:str, starting_cash=100000, log_to_file:bool=False):
        super().__init__(id, random_state, log_to_file)
        
        # Agent internal 
        self._order = {}
        self._starting_cash = starting_cash
        self._cash_balance = starting_cash
        self._current_positions = defaultdict(int)
        self._pending_positions = defaultdict(int)
    
    def kernel_start(self, start_time):
        self.exchange_id = self.kernel.get_exchange_id()
        super().kernel_start(start_time)
    
    def kernel_stop(self):
        super().kernel_stop()
        # compute final result
    
    def send_message(self, recipient_id, message, delay=0):
        return super().send_message(recipient_id, message, delay)
    
    def receive_message(self, current_time, message):
        super().receive_message(current_time, message)
        msg_type = message.type
        if msg_type == MessageType.ORDER_EXECUTED:
            filled_order:FilledOrder = message.content
            self._cash_balance += filled_order.fee # positive for maker, negative for taker
            if filled_order.side == Side.BUY:
                self._current_positions[filled_order.symbol] += filled_order.filled_quantity
                self._cash_balance -= filled_order.filled_quantity * filled_order.filled_price
            elif filled_order.side == Side.SELL:
                self._current_positions[filled_order.symbol] -= filled_order.filled_quantity
                self._cash_balance += filled_order.filled_quantity * filled_order.filled_price
            self._pending_positions[filled_order.symbol] -= filled_order.filled_quantity
        elif msg_type == MessageType.ORDER_CANCELLED:
            order_id = message.content
            order = self._orders[order_id]
            self._pending_positions[order.symbol] -= order.quantity
            del self._orders[order_id]
        
    def place_limit_order(self, symbol:str, quantity:int, side:Side, limit_price:int):
        order = LimitOrder(self.id, self.current_time, symbol, quantity, side, limit_price)
        self._orders[order.order_id] = deepcopy(order)
        # update pending positions
        qty = order.quantity if order.side == Side.BUY else -order.quantity
        self._pending_positions[symbol] += qty
        # send order to exchange
        message = Message(MessageType.LIMIT_ORDER, order)
        self.send_message(self.exchange_id, message)
    
    def place_market_order(self, symbol:str, quantity:int, side:Side): 
        order = MarketOrder(self.id, self.current_time, symbol, quantity, side) 
        self._orders[order.order_id] = deepcopy(order)
        # update pending positions
        qty = order.quantity if order.side == Side.BUY else -order.quantity
        self._pending_positions[symbol] += qty
        # send order to exchange
        message = Message(MessageType.MARKET_ORDER, order)
        self.send_message(self.exchange_id, message)
        