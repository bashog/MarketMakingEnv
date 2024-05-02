from agents.trading_agent import TradingAgent
from util.types import Side

class DummyTrader(TradingAgent):
    def __init__(self, id: str, starting_cash=100000):
        super().__init__(id, starting_cash)
        
    def handle_wake_up(self, current_time):
        super().handle_wake_up(current_time)
        market_data = self.get_market_data()
        if market_data is not None:
            best_bid_price, best_bid_quantity = self._market_data.best_bid()
            best_ask_price, best_ask_quantity = self._market_data.best_ask()
            self.place_limit_order(self._symbol, best_bid_quantity, Side.BUY, best_bid_price)
            self.place_limit_order(self._symbol, best_ask_quantity, Side.SELL, best_ask_price)
            self._logger.info(f"Dummy trader {self.id} placed limit orders at best bid and ask prices")