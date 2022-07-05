from Domain.Enums.OrderTimeSpan import orderTimeSpan
from Domain.Enums.OrderType import orderType
from Domain.Models.Order import Order
from Domain.Enums.OrderStatus import orderStatus


class orderResultMessageToStrategy():
    def __init__(self) -> None:
        self.orderType:orderType = None
        self.orderStatus = None # Success / Fail
        self.tickerId = None
        self.timeSpan:orderTimeSpan = None
        self.assetPrice:int = None

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

    def set_tickerId(self, id):
        self.tickerId = id

    def get_tickerId(self):
        return self.tickerId
    
    def set_asset_price(self, id):
        self.assetPrice = id

    def get_asset_price(self):
        return self.assetPrice

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


    def set_order_status(self, _orderStatus):
        if isinstance(_orderStatus, orderStatus):
            self.orderStatus = _orderStatus
        else:
            raise Exception('Order Status is not correct.')

    def get_order_status(self):
        if isinstance(self.orderStatus, orderStatus):
            return self.orderStatus
        else:
            raise Exception('Order status has not been set.')


    