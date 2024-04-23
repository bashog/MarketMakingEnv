from typing import Any, Callable, Deque, Dict, List, Optional
from collections import defaultdict, deque
import bisect
import math
from copy import deepcopy

from market_engine.order import Order, MarketOrder, LimitOrder, FilledOrder
from util.types import Side, MessageType
from util.message import Message
from util.logger import DummyLogger


class OrderBook:

    def __init__(self, symbol:str, owner=None, logger=DummyLogger()):
        """Initialise a new instance of the OrderBook class."""
        self.symbol = symbol
        self.owner = owner # the exchange agent that owns the order book
        self.maker_fee: float = 0.0
        self.taker_fee: float = 0.0
        
        self.logger = logger
        
        # Dict that stores the order for each price level 
        self._levels: Dict[int, Deque[Order]] = defaultdict(deque)         
        # Price levels for each side 
        self._bid_prices: List[int] = []
        self._ask_prices: List[int] = []
        # Total volume for each price level
        self._total_volumes: Dict[int, int] = defaultdict(int)
        self._last_traded_price: Optional[int] = None
    
    def set_owner(self, owner):
        self.owner = owner
        
    def send_order(self, order: Order):
        """Send an order to the order book."""
        if order.__class__.__name__ == 'MarketOrder':
            self._trade_order(order)
        elif order.__class__.__name__ == 'LimitOrder':
            self._insert_order(order)
        else:
            raise ValueError(f"Unknown order type: {order}")
    
    def _insert_order(self, order: LimitOrder):
        price = order.limit_price
        side = order.side
        #self.logger.info(f"Inserting order: {order}, Price: {price}, Side: {side}")
        while (order.remaining_quantity > 0 and
               ((side == Side.BUY and self._ask_prices and self._best_ask() is not None and price >= self._best_ask()) or
                (side == Side.SELL and self._bid_prices and self._best_bid() and price <= self._best_bid()))):
            best_price = self._best_ask() if side == Side.BUY else self._best_bid()
            order.remaining_quantity = self._trade_level(order, best_price, side)
            

        if order.remaining_quantity > 0:
            self._levels[price].append(order)
            self._total_volumes[price] += order.remaining_quantity
            if side == Side.BUY:
                if price not in self._bid_prices:
                    bisect.insort(self._bid_prices, price)
            elif side == Side.SELL:
                if price not in self._ask_prices:
                    bisect.insort(self._ask_prices, price)
    
    def _trade_order(self, order: MarketOrder):
        """Send a market order to the order book."""
        side = order.side
        prices = self._ask_prices if side == Side.BUY else self._bid_prices
        while order.remaining_quantity > 0 and prices:
            best_price = prices[0] if side == Side.BUY else prices[-1]
            order.remaining_quantity = self._trade_level(order, best_price, side)
                
    def _trade_level(self, incoming_order: Order, price: int, side: Side):
        """Trade an order with existing orders at a given price level."""
        queue = self._levels[price]
        while queue and incoming_order.remaining_quantity > 0:
            current_order = queue[0]
            traded_quantity = min(current_order.remaining_quantity, incoming_order.remaining_quantity)
            
            # update remaining quantities
            current_order.remaining_quantity -= traded_quantity
            incoming_order.remaining_quantity -= traded_quantity
            
            # notify the owner 
            if traded_quantity > 0:
                # send a message to the agent that placed the order initially
                maker_filled_order = FilledOrder(current_order.agent_id, current_order.symbol, traded_quantity, current_order.side, price, self.maker_fee)
                message = Message(MessageType.ORDER_EXECUTED, maker_filled_order)
                self.owner.send_message(self.owner.id, message)
                # send a message to the agent that placed the incoming order
                taker_filled_order = FilledOrder(incoming_order.agent_id, incoming_order.symbol, traded_quantity, incoming_order.side, price, self.taker_fee)
                message = Message(MessageType.ORDER_EXECUTED, taker_filled_order)
                self.owner.send_message(self.owner.id, message)
            
            self._total_volumes[price] -= traded_quantity
            self._last_traded_price = price
            if current_order.remaining_quantity == 0:
                queue.popleft()
            if self._total_volumes[price] == 0:
                self._remove_level(price, side)

        return incoming_order.remaining_quantity
    
    def _remove_level(self, price: int, side):
        """Remove a price level from the order book."""
        #print(f"Removing level {price} on side {side}")
        if side == Side.BUY:
            if price in self._bid_prices:
                self._bid_prices.remove(price)
                #print(f"Removed {price} from bid prices.")
        elif side == Side.SELL:
            if price in self._ask_prices:
                self._ask_prices.remove(price)
                #print(f"Removed {price} from ask prices.")
        if price in self._levels:
            del self._levels[price]
            #print(f"Removed {price} from levels.")
        if price in self._total_volumes:
            del self._total_volumes[price]
            #print(f"Removed {price} from total volumes.")
       
    def _best_bid(self):
        """Return the current best bid price"""
        while self._bid_prices:
            if self._levels[self._bid_prices[-1]]:
                return self._bid_prices[-1]
            else:
                self._remove_level(self._bid_prices[-1], Side.BUY)
        return None
    
    def _best_ask(self):
        """Return the current best ask price"""
        while self._ask_prices:
            if self._levels[self._ask_prices[0]]:
                return self._ask_prices[0]
            else:
                self._remove_level(self._ask_prices[0], Side.SELL)
        return None

    def mid_price(self):
        """Return the mid price of the order book"""
        if self._best_bid() is None or self._best_ask() is None:
            return None
        return (self._best_bid() + self._best_ask()) / 2.0
    
    def get_buy_side(self, depth=10):
        buy_side:Dict[int, int] = {}
        depth = min(depth, len(self._bid_prices)) if depth is not None else len(self._bid_prices)
        for price in self._bid_prices[:depth]:
            buy_side[price] = self._total_volumes[price]
        return buy_side
    
    def get_sell_side(self, depth=10):
        sell_side:Dict[int, int] = {}
        depth = min(depth, len(self._ask_prices)) if depth is not None else len(self._ask_prices)
        for price in self._ask_prices[:depth]:
            sell_side[price] = self._total_volumes[price]
        return sell_side
            
    
    def __str__(self, depth=None):
        bid_details = []
        bid_depth = min(depth, len(self._bid_prices)) if depth is not None else len(self._bid_prices)
        sorted_bid_prices = sorted(self._bid_prices, reverse=True)
        for price in sorted_bid_prices[:bid_depth]:
            orders = self._levels[price]
            quantity_at_price = self._total_volumes[price]
            order_count = len(orders)
            bid_details.append(f"{price}$ x {quantity_at_price} (Orders: {order_count})")

        ask_details = []
        ask_depth = min(depth, len(self._ask_prices)) if depth is not None else len(self._ask_prices)
        sorted_ask_prices = sorted(self._ask_prices)
        for price in sorted_ask_prices[:ask_depth]:
            orders = self._levels[price]
            quantity_at_price = self._total_volumes[price]
            order_count = len(orders)
            ask_details.append(f"{price}$ x {quantity_at_price} (Orders: {order_count})")

        bids_str = ' | '.join(bid_details) if bid_details else "No bids"
        asks_str = ' | '.join(ask_details) if ask_details else "No asks"
        last_price_str = f"Last traded price: {self._last_traded_price}$" if self._last_traded_price else "No trades yet"

        return f"OrderBook(Symbol={self.symbol})\nBids: {bids_str}\nAsks: {asks_str}\n{last_price_str}"

        bid_details = []
        for price in sorted(self._bid_prices, reverse=True):
            orders = self._levels[price]
            quantity_at_price = self._total_volumes[price]
            order_count = len(orders)
            bid_details.append(f"{price}¢ x {quantity_at_price} (Orders: {order_count})")

        ask_details = []
        for price in sorted(self._ask_prices):
            orders = self._levels[price]
            quantity_at_price = self._total_volumes[price]
            order_count = len(orders)
            ask_details.append(f"{price}¢ x {quantity_at_price} (Orders: {order_count})")

        bids_str = ' | '.join(bid_details) if bid_details else "No bids"
        asks_str = ' | '.join(ask_details) if ask_details else "No asks"
        last_price_str = f"Last traded price: {self._last_traded_price}¢" if self._last_traded_price else "No trades yet"

        return f"OrderBook(Symbol={self.symbol})\nBids: {bids_str}\nAsks: {asks_str}\n{last_price_str}"