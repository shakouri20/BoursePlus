from Application.Services.ReadData.ReadOnline.MarketWatchDataHandler import marketWatchDataHandler
from math import atan, floor, log10, pi
from Domain.Enums.OnlineColumns import onlineColumns
from Application.Services.ReadData.ReadOnline.OnlineDataHandler import onlineDataHandler
from Application.Services.Middlewares.MiddlewareFramework.Middleware import cast_list_to_numba, get_numba_types, middleware
from Application.Services.ReadData.ReadOffline.ReadOfflineServices import read_offline_services
from numba.types import float64, unicode_type, ListType, DictType, int64
from numba.typed import Dict, List
from Domain.ImportEnums import *

class marketMADifDailyBuyMiddleware21(middleware):

    def __init__(self, dataHandler, marketWatchHandler, mainTickersList: list, kargs):
        super(marketMADifDailyBuyMiddleware21, self).__init__(dataHandler, marketWatchHandler, mainTickersList, kargs)

    def get_online_data(self, tickersList: list, dataHandler: onlineDataHandler, marketWatchHandler:marketWatchDataHandler):
        # Getting  >> Float64 <<
        (floatInnerDict, FloatDataDict) = get_numba_types('Float', True)
        floatInnerDict.clear()
        FloatDataDict.clear()

        marketMADif = marketWatchHandler.lastPricePRCAverge_MA_dif(num= 1, maLength= 21)

        if len(marketMADif.keys()) != 1:
            return (None,None)

        for group in marketMADif:
            value = marketMADif[group][-1]
            floatInnerDict.update({group: value})

        for Id in tickersList:
            FloatDataDict.update({Id: floatInnerDict.copy()})

        return (FloatDataDict, None)
        

    @staticmethod
    def single_ticker_calculation(tickerFloatOnlineData: dict, tickerListOnlineData:dict, tickerOfflineData: dict, tickerHistoryData:dict, tickerId:int):
        
        marketMADif = tickerFloatOnlineData[marketGroupType.TotalMarket.value]

        if marketMADif < -2.5 :
            return (True, 0)

        # if marketMADif > 2.5:
        #     return (False, 100)

        if marketMADif >= 0:
            score = int(10 * (marketMADif ** (5/3)) + 60)
        else:
            score = int(-10 * (abs(marketMADif) ** (5/3)) + 60)

        # score = (marketMADif + 10) * 5

        return (False , max(min(100, int(score)), 0))