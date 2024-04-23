from datamodel import OrderDepth, TradingState, Order
from typing import List
import string

# factory Trader class i give the name of the trader and it returns the trader class
class TraderFactory:
    @staticmethod
    def getTrader(trader_name: str):
        if trader_name == "BaseTrader":
            return BaseTrader()
        elif trader_name == "MarketTakerTrader":
            return DumbTrader()
        elif trader_name == "VolumeBasedTrader":
            return VolumeBasedTrader()
        else:
          print("Trader not found")
          return None
      
class BaseTrader:
    def run(self, state: TradingState):
        """
        Only method required. It takes all buy and sell orders for all symbols as an input,
        and outputs a list of orders to be sent
        """
        
        print("traderDatZa: " + state.traderData)
        print("Observations: " + str(state.observations))

        # Orders to be placed on exchange matching engine
        result = {}
        for product in state.order_depths:
            order_depth: OrderDepth = state.order_depths[product]
            # Initialize the list of Orders to be sent as an empty list
            orders: List[Order] = []
            # Define a fair value for the PRODUCT. Might be different for each tradable item
            # Note that this value of 10 is just a dummy value, you should likely change it!
            acceptable_price = 10
                        # All print statements output will be delivered inside test results
            print("Acceptable price : " + str(acceptable_price))
            print("Buy Order depth : " + str(len(order_depth.buy_orders)) + ", Sell order depth : " + str(len(order_depth.sell_orders)))
            
            # Order depth list come already sorted.
            # We can simply pick first item to check first item to get best bid or offer
            if len(order_depth.sell_orders) != 0:
                best_ask, best_ask_amount = list(order_depth.sell_orders.items())[0]
                if int(best_ask) < acceptable_price:
                    # In case the lowest ask is lower than our fair value,
                    # This presents an opportunity for us to buy cheaply
                    # The code below therefore sends a BUY order at the price level of the ask,
                    # with the same quantity
                    # We expect this order to trade with the sell order
                    print("BUY", str(-best_ask_amount) + "x", best_ask)
                    orders.append(Order(product, best_ask, -best_ask_amount))
                    
            if len(order_depth.buy_orders) != 0:
                best_bid, best_bid_amount = list(order_depth.buy_orders.items())[0]
                if int(best_bid) > acceptable_price:
                    # Similar situation with sell orders
                    print("SELL", str(best_bid_amount) + "x", best_bid)
                    orders.append(Order(product, best_bid, -best_bid_amount))
                    
            result[product] = orders
            
        # String value holding Trader state data required.
        # It will be delivered as TradingState.traderData on next execution.
        traderData = "SAMPLE" 
        
        # Sample conversion request. Check more details below.
        conversion = 1
        return result, traderData, conversion


class DumbTrader:
    """ Buy Low Sell High Strategy"""
    def run(self, state: TradingState):
        result = {}
        for product in state.order_depths:
            order_depth: OrderDepth = state.order_depths[product]
            orders: List[Order] = []
            position = state.position[product]
            ask_prices, ask_amounts = list(order_depth.sell_orders.keys()), list(order_depth.sell_orders.values()) 
            bid_prices, bid_amounts = list(order_depth.buy_orders.keys()), list(order_depth.buy_orders.values())
            if len(ask_prices) != 0:     
                # Buy high           
                ask_price = ask_prices[-1]
                ask_amount = 20 - position
                orders.append(Order(product, ask_price, ask_amount))
            if len(bid_prices) != 0:
                # Sell low
                bid_price = bid_prices[-1]
                bid_amount =  -20 - position
                orders.append(Order(product, bid_price, bid_amount))               
            result[product] = orders
        traderData = "SAMPLE"
        conversion = 1
        return result, traderData, conversion


class VolumeBasedTrader:
    """ Skew the order book by adding a fixed amount to the bid and ask prices
    
    Heuristic : fill probability of a sell limit order is highest (lowest) when the book is buy-heavy (sell-heavy), and the fill probability of a buy limit is highest (lowest) when the book is sell-heavy (buy-heavy)"""
    
    # hyperparameters
    # deviation nbr tick from BB BA devTick
    # k measure of imbalance
    def set_hyperparameter(self, d:dict):
        self.dev_tick = 1
        self.kappa = 1/3
        pass
        
    def run(self, state: TradingState):
        result = {}
        for product in state.order_depths:
            order_depth: OrderDepth = state.order_depths[product]
            orders: List[Order] = []
            pos = state.position[product]
            buy_orders = order_depth.buy_orders
            sell_orders = order_depth.sell_orders
            
            volume_bid = sum(buy_orders.values())
            volume_ask = abs(sum(sell_orders.values()))
            print(volume_ask, volume_bid)
            if volume_ask == 0 and volume_bid == 0:
                break
            v_imbalance = (volume_bid - volume_ask) / (volume_bid + volume_ask)
            if v_imbalance > self.kappa:
                # buy heavy regime
                acceptable_price = list(sell_orders.keys())[0] + 1
                qty = - 20 - pos
                orders.append(Order(product, acceptable_price, qty))
            elif self.kappa > v_imbalance > - self.kappa:
                # neutral regime
                pass
            elif v_imbalance <= -self.kappa:
                # sell heavy regime
                acceptable_price = list(buy_orders.keys())[0] -1
                qty = 20 - pos
                orders.append(Order(product, acceptable_price, qty))             
            
            result[product] = orders
        traderData = "SAMPLE"
        conversion = 1
        return result, traderData, conversion



def RandomQuotingTrader():
    """Randomly quotes ask and bid orders in the 3 levels of the limit order book"""
    def run(self, state: TradingState):
        result = {}
        for product in state.order_depths:
            order_depth: OrderDepth = state.order_depths[product]
            orders: List[Order] = []
            # Logic ...
            result[product] = orders
        traderData = "SAMPLE"
        conversion = 1
        return result, traderData, conversion
    
def FixedQuotingTrader():
    """ Quotes ask and bid orders at the best bid and best ask"""
    def run(self, state: TradingState):
        result = {}
        for product in state.order_depths:
            order_depth: OrderDepth = state.order_depths[product]
            orders: List[Order] = []
            # Logic ...
            result[product] = orders
        traderData = "SAMPLE"
        conversion = 1
        return result, traderData, conversion    

def AvellanedStoikovTrader():
    
    def run(self, state: TradingState):
        pass