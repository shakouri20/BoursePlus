from Application.Services.ReadData.ReadOnline.MarketWatchDataHandler import marketWatchDataHandler
from math import atan, floor, log10, pi
from Domain.Enums.OnlineColumns import onlineColumns
from Application.Services.ReadData.ReadOnline.OnlineDataHandler import onlineDataHandler
from Application.Services.Middlewares.MiddlewareFramework.Middleware import cast_list_to_numba, get_numba_types, middleware
from Application.Services.ReadData.ReadOffline.ReadOfflineServices import read_offline_services
from numba.types import float64, unicode_type, ListType, DictType, int64
from numba.typed import Dict, List
from Domain.ImportEnums import *

S15 = [1]
S3 = [6]
S = S3

class marketMADifDailyBuyMiddleware100(middleware):

    def __init__(self, dataHandler, marketWatchHandler, mainTickersList: list, kargs):
        super(marketMADifDailyBuyMiddleware100, self).__init__(dataHandler, marketWatchHandler, mainTickersList, kargs)

    def get_online_data(self, tickersList: list, dataHandler: onlineDataHandler, marketWatchHandler:marketWatchDataHandler):
        # Getting  >> Float64 <<
        (floatInnerDict, FloatDataDict) = get_numba_types('Float', True)
        floatInnerDict.clear()
        FloatDataDict.clear()

        marketMADif = marketWatchHandler.lastPricePRCAverge_MA_dif(decNum=S[0], num= 1, maLength= 100)

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
        
        limitScore = 45

        marketMADif = tickerFloatOnlineData[marketGroupType.TotalMarket.value]

        score = int(max(min(60 + 2 * marketMADif, 100), 20))

        if score < limitScore:            
            return (True, 0)
        else:
            return (False, score)