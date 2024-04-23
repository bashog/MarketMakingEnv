from collections import defaultdict
from market_engine.order import LimitOrder
from util.types import Side

import pandas as pd

class DataOracle:
    def __init__(self, data:pd.DataFrame, symbol:str):
        self.data = data
        self.symbol = symbol
        self._orders = defaultdict(list)
        self._timestamps = None
    
    def read_data(self):
        self.data['internal_timestamp'] = pd.to_datetime(self.data['internal_timestamp'])
        self._timestamps = self.data['internal_timestamp'].unique()
        for timestamp in self._timestamps:
            orders_at = self.data[self.data['internal_timestamp'] == timestamp]
            for index, line in orders_at.iterrows():
                side = Side[line['side']]
                price = line['price']
                volume = line['volume']
                id = line['qid']
                order = LimitOrder("", timestamp, self.symbol, volume, side, price, id)
                self._orders[timestamp].append(order)
    
    def get_orders(self, timestamp):
        return self._orders[timestamp]
    
    def get_start_time(self):
        return self._timestamps[0]
    
    def get_end_time(self):
        return self._timestamps[-1]
    
    def get_timestamps(self):
        return self._timestamps
    
    def kernel_init(self, kernel):
        self.kernel = kernel