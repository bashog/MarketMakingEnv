import enum

class Side(enum.IntEnum):
    SELL = 0
    BUY = 1
    ASK = SELL
    BID = BUY
    S = SELL
    B = BUY
    
class MessageType(enum.Enum):
    # about order
    LIMIT_ORDER = "LIMIT_ORDER"
    MARKET_ORDER = "MARKET_ORDER"
    CANCEL_ORDER = "CANCEL_ORDER"
    MODIFY_ORDER = "MODIFY_ORDER"
    
    # about execution
    ORDER_ACCEPTED = "ORDER_ACCEPTED"
    ORDER_CANCELLED = "ORDER_CANCELLED"
    ORDER_EXECUTED = "ORDER_EXECUTED"
    
    # about trading agent
    REQUEST_MARKET_DATA = "REQUEST_MARKET_DATA"
    MARKET_DATA = "MARKET_DATA"
    WAKE_UP = "WAKE_UP"
    
    def __lt__(self, other):
        return self.value < other.value
    