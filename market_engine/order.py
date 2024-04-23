from util.types import Side

class Order:
    order_id: int = 0
    
    def __init__(self, agent_id:str, time_placed:int, symbol:str, quantity:int, side:Side, order_id:int=None):
        """ Order object """
        self.agent_id = agent_id
        self.time_placed = time_placed
        self.symbol = symbol
        self.quantity = quantity
        self.side = side
        self.order_id = order_id if order_id is not None else self.generate_order_id()
        self.remaining_quantity = quantity
        
    def generate_order_id(self):
        Order.order_id += 1
        return Order.order_id


class MarketOrder(Order):
    def __init__(self, agent_id:str, time_placed:int, symbol:str, quantity:int, side:Side, order_id:int=None):
        """ Market Order object"""
        super().__init__(agent_id, time_placed, symbol, quantity, side, order_id)
    
    def __str__(self):
        return f"{self.side} {self.quantity} {self.symbol}"
        

class LimitOrder(Order):
    def __init__(self, agent_id:str, time_placed:int, symbol:str, quantity:int, side:Side, limit_price:int, order_id:int=None):
        """ Limit Order object """
        super().__init__(agent_id, time_placed, symbol, quantity, side, order_id)
        self.limit_price = limit_price
    
    def __str__(self):
        return f"{self.side} {self.quantity} {self.symbol} @ {self.limit_price}"
    
class FilledOrder:
    def __init__(self, agent_id:str, symbol:str, filled_quantity:int, side:Side, filled_price:int, fee:int=0):
        self.agent_id = agent_id
        self.symbol = symbol
        self.filled_quantity = filled_quantity
        self.side = side
        self.filled_price = filled_price
        self.fee = fee # positive fee if maker, negative fee if taker

    def __str__(self):
        return f"{self.side} {self.filled_quantity} {self.symbol} @ {self.filled_price}"


