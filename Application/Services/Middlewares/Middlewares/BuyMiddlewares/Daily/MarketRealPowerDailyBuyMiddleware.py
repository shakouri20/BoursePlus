from Application.Services.ReadData.ReadOnline.MarketWatchDataHandler import marketWatchDataHandler
from math import atan, floor, log10, pi
from Domain.Enums.OnlineColumns import onlineColumns
from Application.Services.ReadData.ReadOnline.OnlineDataHandler import onlineDataHandler
from Application.Services.Middlewares.MiddlewareFramework.Middleware import cast_list_to_numba, get_numba_types, middleware
from Application.Services.ReadData.ReadOffline.ReadOfflineServices import read_offline_services
from numba.types import float64, unicode_type, ListType, DictType, int64
from numba.typed import Dict, List
from Domain.ImportEnums import *

class marketRealPowerDailyBuyMiddleware(middleware):

    def __init__(self, dataHandler, marketWatchHandler, mainTickersList: list, kargs):
        super(marketRealPowerDailyBuyMiddleware, self).__init__(dataHandler, marketWatchHandler, mainTickersList, kargs)

    def get_online_data(self, tickersList: list, dataHandler: onlineDataHandler, marketWatchHandler:marketWatchDataHandler):
        # Getting  >> Float64 <<
        (floatInnerDict, FloatDataDict) = get_numba_types('Float', True)
        floatInnerDict.clear()
        FloatDataDict.clear()

        marketRealPower = marketWatchHandler.realPowerDif(num= 1, length= 30)

        if len(marketRealPower.keys()) == 0:
            return (None,None)

        for group in marketRealPower:
            value = marketRealPower[group][-1]
            floatInnerDict.update({group: value})

        for Id in tickersList:
            FloatDataDict.update({Id: floatInnerDict.copy()})

        return (FloatDataDict, None)
        

    @staticmethod
    def single_ticker_calculation(tickerFloatOnlineData: dict, tickerListOnlineData:dict, tickerOfflineData: dict, tickerHistoryData:dict, tickerId:int):
        
        marketRealPower = tickerFloatOnlineData[marketGroupType.TotalMarket.value]

        score = max(min(100, int(166*log10(marketRealPower)+50)), 0)

        return (False, score)
        # if marketLastIndex < -50 :
        #     return (False, 0)

        # if marketLastIndex > 60:
        #     return (False, 100)

        # if marketLastIndex >= 0:
        #     score = int(1.4 * (marketLastIndex ** (5/7)) + 60)
        # else:
        #     score = int(-1.4 * (abs(marketLastIndex) ** (5/7)) + 60)

        # return (False , min(100, score))