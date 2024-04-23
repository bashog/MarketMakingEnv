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
    
    # about data of the order book
    LAST_TRADE = "LAST_TRADE"
    MARKET_DATA = "MARKET_DATA"
    