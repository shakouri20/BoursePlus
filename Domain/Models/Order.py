# from numba.core.types.abstract import _type_reconstructor
from datetime import datetime
from inspect import FullArgSpec
from Domain.ImportEnums import *

from numba import jit

# ==================================<< Decorators >>=============================================== #

def order_validation(func):
    def inner(*args, **kargs):
    # logger = logging.getLogger(__name__)
        def is_in_args():
            for arg in args:
                if isinstance(arg, Order):
                    return arg
            for key in kargs:
                if isinstance(kargs[key], Order):
                    return kargs[key]
            return None
        _order:Order = is_in_args()
        if _order is None:
            raise Exception('No order is provided!!')
        if not _order.is_valid_order():
            raise Exception('Provided order object is not valid!!!')
        else:
            return func(*args, **kargs)
    return inner

def benchmark(func):
    """
    A decorator that prints the time a function takes
    to execute.
    """
    import time
    def wrapper(*args, **kwargs):
        t = time.perf_counter()
        res = func(*args, **kwargs)
        print (func.__name__, time.perf_counter()-t)
        return res
    return wrapper

class Order():
    def __init__(self) -> None:
        self.tickerId = None
        self.orderType:orderType = None
        self.timeSpan:orderTimeSpan = None
        self.assetType:assetType = None
        self.price = None # This Price will be sent to broker for execution
        self.assetPrice = None # Price of asset on trading table
        self.time = None
        self.policy = 1

    def is_valid_order(self):
        attributes = [a for a in dir(self) if not a.startswith('__') and not callable(getattr(self, a))]
        for attribute in attributes:
            result = self.__getattribute__(attribute)
            if result is None:
                return False
        
        return True
        
    def set_tickerId(self, id):
        self.tickerId = id

    def get_tickerId(self):
        return self.tickerId

    def set_order_time(self, time: datetime):
        if not isinstance(time, datetime):
            raise Exception('Provided time is not valid! Pass a valid datetime object.')
        self.time = time

    def get_order_time(self):
        if self.time is None:
            raise Exception('Time has not been set yet!')
        return self.time

    def set_asset_type(self, type:assetType):
        if isinstance(type, assetType):
            self.assetType = type
        else:
            raise Exception('Asset type is not correct.')

    def get_asset_type(self):
        if isinstance(self.assetType, assetType):
            return self.assetType
        else:
            raise Exception('Asset type has not been set.')

    def set_order_type(self, _orderType):
        if isinstance(_orderType, orderType):
            self.orderType = _orderType
        else:
            raise Exception('Order type is not valid.')

    def get_order_type(self):
        if isinstance(self.orderType, orderType):
            return self.orderType
        else:
            raise Exception('OrderType has not been set.')

    def set_order_price(self, price):
        if price > 0:
            self.price = price
        else:
            raise Exception(str(self.tickerId), str(price), 'price is not valid.')

    def get_order_price(self):
        if self.price is not None:
            return self.price
        else:
            raise Exception('Price has not been set!')

    def set_order_asset_price(self, price):
        if price > 0:
            self.assetPrice = price
        else:
            raise Exception('price is not valid.')

    def get_order_asset_price(self):
        if self.assetPrice is not None:
            return self.assetPrice
        else:
            raise Exception('Asset price has not been set!')

    def set_time_span(self, _timeSpan):
        if isinstance(_timeSpan, orderTimeSpan):
            self.timeSpan = _timeSpan
        else:
            raise Exception('Time span is not correct.')

    def get_time_span(self):
        if isinstance(self.timeSpan, orderTimeSpan):
            return self.timeSpan
        else:
            raise Exception('Time span has not been set.')