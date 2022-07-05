from Domain.ImportEnums import *

# ==================================<< Decorators >>=============================================== #
def asset_validation(func):
    def inner(*args, **kargs):
        def is_in_args():
            for arg in args:
                if isinstance(arg, asset):
                    return arg

            for key in kargs:
                if isinstance(kargs[key], asset):
                    return kargs[key]
            return None

        _asset:asset = is_in_args()
        if _asset is None:
            raise Exception('No asset is provided!!')

        if not _asset.is_valid_asset():
            raise Exception('Provided asset object is not valid!!!')
        else:
            return func(*args, **kargs)
    return inner


class asset():
    '''Base class for an asset '''
    def __init__(self, _assetType:assetType, _tickerId, _Amount: int, _timeSpan: orderTimeSpan, _orderType: orderType) -> None:
        self.tickerId = _tickerId
        self.Amount = _Amount
        self.assetType: assetType = _assetType
        self.timeSpan: orderTimeSpan = _timeSpan
        self.orderType: orderType = _orderType

    def __eq__(self, other): 
        if not isinstance(other, asset):
            # don't attempt to compare against unrelated types
            return NotImplemented

        return self.tickerId == other.tickerId and self.Amount == other.Amount and self.assetType == other.assetType\
            and self.timeSpan == other.timeSpan and self.orderType == other.orderType 

    def is_valid_asset(self):
        attributes = [a for a in dir(self) if not a.startswith('__') and not callable(getattr(self, a))]
        for attribute in attributes:
            result = self.__getattribute__(attribute)
            if result is None:
                return False
        
        return True

    def get_tickerId(self):
        return self.tickerId

    def get_order_type(self):
        if isinstance(self.orderType, orderType):
            return self.orderType
        else:
            raise Exception('OrderType has not been set.')

    def get_time_span(self):
        if isinstance(self.timeSpan, orderTimeSpan):
            return self.timeSpan
        else:
            raise Exception('Time span has not been set.')

    def get_amount(self):
        return self.Amount

    def get_asset_type(self):
        return self.assetType