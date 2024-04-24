from typing import Dict
import numpy as np

from market_engine.order_book import OrderBook


class OrderBookState:
    def __init__(self, 
                 symbol, 
                 timestamp, 
                 buy_side:Dict[int, int], 
                 sell_side:Dict[int, int], 
                 mid_price:int):
        self.timestamp = timestamp
        self.symbol = symbol
        self.buy_side = buy_side
        self.sell_side = sell_side
        self.mid_price = mid_price
    
    def volume_buy(self):
        return sum(self.buy_side.values())
    
    def volume_sell(self):
        return sum(self.sell_side.values())

class MarketAnalytics:
    def __init__(self, symbol:str, depth:int):
        self.symbol = symbol
        self.depth = depth
        #self.order_book_snapshots = {}
        self.order_book_state = {}
        self.timestamps = []
        self.prices = []

    def order_strength(self, length:int):
        buy_volumes = [self.order_book_state[t].volume_buy() for t in self.timestamps[-length:]]
        sell_volumes = [self.order_book_state[t].volume_sell() for t in self.timestamps[-length:]]
        total_buys = sum(buy_volumes)
        total_sells = sum(sell_volumes)
        total_volume = total_buys + total_sells
        if total_volume == 0:
            return 0 
        return (total_buys - total_sells) / total_volume
    
    def realized_volatility(self, length:int):
        pass 
    
    def relative_strength_index(self, length:int):
        if len(self.prices) < length + 1:
            return None  # Not enough data
        changes = np.diff(self.prices[-(length + 1):])
        gains = np.maximum(changes, 0)
        losses = -np.minimum(changes, 0)
        average_gain = np.mean(gains)
        average_loss = np.mean(losses)
        if average_loss == 0:
            return 100
        rs = average_gain / average_loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def update(self, timestamp, order_book:OrderBook):
        #self.order_book_snapshots[timestamp] = order_book
        buy_side = order_book.get_buy_side(self.depth)
        sell_side = order_book.get_sell_side(self.depth)
        mid_price = order_book.mid_price()
        order_book_state = OrderBookState(self.symbol, timestamp, buy_side, sell_side, mid_price)
        self.order_book_state[timestamp] = order_book_state
        self.timestamps.append(timestamp)
        if mid_price is not None:
            self.prices.append(mid_price)
    
    def __str__(self):
        return (f"MarketAnalytics for {self.symbol}: {len(self.timestamps)} timestamps processed, current mid price: {self.prices[-1] if self.prices else 'N/A'}")
        