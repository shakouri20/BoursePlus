from math import ceil
from Domain.ImportEnums import *
import uuid
from datetime import datetime
from Infrastructure.Repository.TickerRepository import ticker_repo

# ==================================<< Decorators >>=============================================== #
def position_validation(func):
    def inner(*args, **kargs):
        def is_in_args():
            for arg in args:
                if isinstance(arg, position):
                    return arg
            for key in kargs:
                if isinstance(kargs[key], position):
                    return kargs[key]
            return None
        _position:position = is_in_args()
        if _position is None:
            raise Exception('No position is provided!!')
        if not _position.is_valid_position():
            raise Exception('Provided position object is not valid!!!')
        else:
            return func(*args, **kargs)
    return inner

class position():
    '''Position class represents every trade positioned and provides functions to create, terminate 
        and get resutls of a position. ''' 
    def __init__(self) -> None:
        self.status: positionStatus = None
        self.positionId = uuid.uuid1()
        self.tickerId = None
        self.tickerName = None
        self.creatorStrategy = None
        self.terminatorStrategy = None
        self.orderType:orderType = None
        self.timeSpan:orderTimeSpan = None
        self.assetType:assetType = None
        self.volume = None
        self.brokerFee = None
        self.startPrice = None
        self.endPrice = None
        self.startTime = None
        self.endTime = None

    def is_valid_position(self):
        if self.status is None or self.tickerId is None or self.creatorStrategy is None or self.orderType is None\
                    or self.timeSpan is None or self.assetType is None or self.volume is None or self.brokerFee is None\
                        or self.startPrice is None or self.startTime is None:
            return False
        else:
            return True
            
    def __set_time(self, _datetime:datetime):
        if isinstance(_datetime, datetime):
            self.startTime = _datetime
        else:
            raise Exception('Provided datetime is not valid.')
            
    def create_position(self, tickerId, creatorStrategy, _orderType:orderType, _timeSpan:orderTimeSpan,\
                                _assetType:assetType, startPrice:int, volume:int, brokerFee, startTime = datetime.now()):
        if not isinstance(_assetType, assetType):
            raise Exception('Asset type is not correct.')
        if not isinstance(_orderType, orderType):
            raise Exception('Order type is not valid.')
        if startPrice < 0:
            raise Exception('price is not valid.')
        if volume < 0:
            raise Exception('volume is not valid.')
        if not isinstance(_timeSpan, orderTimeSpan):
            raise Exception('Time span is not correct.')
        self.tickerId = tickerId
        self.creatorStrategy = creatorStrategy
        self.orderType = _orderType
        self.timeSpan = _timeSpan
        self.assetType = _assetType
        self.startPrice = startPrice
        self.volume = volume
        self.brokerFee = brokerFee
        self.startTime = startTime
        self.status = positionStatus.Open

    def terminate_position(self, terminatorStrategy, endPrice:int, _volume:int, endTime = datetime.now()):
        if endPrice < 0:
            raise Exception('price is not valid.')
        if _volume < 0:
            raise Exception('volume is not valid.')
        if self.status != positionStatus.Open:
            raise Exception('position has not been created yet! Can not terminate an unopenned position.')
        if _volume > self.volume :
            raise Exception('Termination volume is bigger than creation volume!')

        if _volume == self.volume:
            # Terminate position completely
            self.terminatorStrategy = terminatorStrategy
            self.endPrice = endPrice
            self.endTime = endTime
            self.status = positionStatus.Closed
            return None
        else:
            # Create a secondary position and initialize it.
            volumeDiff = self.volume - _volume
            secondary_position = position()
            secondary_position.create_position(self.tickerId, self.creatorStrategy, self.orderType, self.timeSpan,\
                                                    self.assetType, self.startPrice, volumeDiff)
            secondary_position.__set_time(self.startTime)
            self.volume = _volume
            self.endPrice = endPrice
            self.endTime = endTime
            self.status = positionStatus.Closed
            return secondary_position

    def get_profit(self):
        '''Returns the profit from a closed position.'''
        if self.status == positionStatus.Open:
            raise Exception('Order still is open!')
        return ceil(self.volume * (self.endPrice - self.startPrice * (1 + self.brokerFee)))

    def get_final_money(self):
        if self.status == positionStatus.Open:
            raise Exception('Order still is open!')
        return self.endPrice * self.volume

    def get_initial_money(self):
        return self.startPrice * self.volume

    def get_start_time(self):
        if self.startTime is None:
            raise Exception('Start time has not been set!')
        
        return self.startTime

    def get_end_time(self):
        if self.endTime is None:
            raise Exception('End time has not been set!')
        
        return self.endTime

    def is_closed(self):
        if self.status == positionStatus.Open:
            return False
        elif self.status == positionStatus.Closed:
            return True
        else:
            raise Exception('Position has not been configured yet!!')
    
    def get_position_id(self):
        '''Returns position id which is unique identifier of position object initialized. '''
        return self.positionId

    def get_tickerName(self):
        return ticker_repo().read_by_ID(self.tickerId)['FarsiTicker']
    
    def get_tickerId(self):
        return self.tickerId

    def get_asset_type(self):
        if isinstance(self.assetType, assetType):
            return self.assetType
        else:
            raise Exception('Asset type has not been set.')

    def get_order_type(self):
        if isinstance(self.orderType, orderType):
            return self.orderType
        else:
            raise Exception('OrderType has not been set.')

    def get_start_price(self):
        if self.startPrice is not None:
            return self.startPrice
        else:
            raise Exception('Start price has not been set!')

    def get_end_price(self):
        if self.endPrice is not None:
            return self.endPrice
        else:
            raise Exception('End price has not been set!')

    def get_time_span(self):
        if isinstance(self.timeSpan, orderTimeSpan):
            return self.timeSpan
        else:
            raise Exception('Time span has not been set.')

    def is_position_fit_to_order(self, tickerId: int, timeSpan: orderTimeSpan) -> bool:
        '''Checks whether position fits to order with its ticker id and time span.
         The position must be open.'''
        if self.status == positionStatus.Closed:
            return False
        if self.tickerId != tickerId:
            return False
        if self.timeSpan != timeSpan:
            return False
        return True

    def get_position_report(self):
        positionDict = {}
        positionDict['Creator'] = self.creatorStrategy
        positionDict['Status'] = self.status.value
        positionDict['Name'] = self.get_tickerName()
        positionDict['T0'] = self.get_start_time().strftime('%Y-%m-%d %H:%M:%S')
        positionDict['P0'] = self.startPrice
        positionDict['V'] = self.volume
        if self.is_closed() == True:
            positionDict['P1'] = self.endPrice
            positionDict['T1'] = self.get_end_time().strftime('%Y-%m-%d %H:%M:%S')
            positionDict['Profit'] = self.get_profit()
            positionDict['Profit%'] = round(self.get_profit()/self.startPrice/self.volume*100, 2)
            positionDict['Terminator'] = self.terminatorStrategy
        return positionDict


