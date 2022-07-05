from Application.Services.ReadData.ReadOnline.MarketWatchDataHandler import marketWatchDataHandler
from math import atan, floor, log10, pi
from Domain.Enums.OnlineColumns import onlineColumns
from Application.Services.ReadData.ReadOnline.OnlineDataHandler import onlineDataHandler
from Application.Services.Middlewares.MiddlewareFramework.Middleware import cast_list_to_numba, get_numba_types, middleware
from Application.Services.ReadData.ReadOffline.ReadOfflineServices import read_offline_services
from numba.types import float64, unicode_type, ListType, DictType, int64
from numba.typed import Dict, List
from Domain.ImportEnums import *

S3 = [25]
S15 = [5]
S = S3

class marketLastIndexDailySellMiddleware(middleware):

    def __init__(self, dataHandler, marketWatchHandler, mainTickersList: list, kargs):
        super(marketLastIndexDailySellMiddleware, self).__init__(dataHandler, marketWatchHandler, mainTickersList, kargs)

    def create_history_data(self, idList: list, dataHandler: onlineDataHandler, marketWatchHandler: marketWatchDataHandler) -> dict:
        if len(idList)==0:
            return None
            
        # Getting  >> Float64 <<
        (floatInnerDict, FloatDataDict) = get_numba_types('Float', False)
        floatInnerDict.clear()
        FloatDataDict.clear()

        # currentTime = dataHandler.time(num= 1)

        for id in idList:
            floatInnerDict.update({'MaxIndex' : -100})
            # Assembling
            FloatDataDict.update({id: floatInnerDict.copy()})
        return FloatDataDict

    def get_online_data(self, tickersList: list, dataHandler: onlineDataHandler, marketWatchHandler:marketWatchDataHandler):
        # Getting  >> Float64 <<
        (floatInnerDict, FloatDataDict) = get_numba_types('Float', True)
        floatInnerDict.clear()
        FloatDataDict.clear()
        # Getting  >> List << 
        (core_list, listInnerDict, listDataDict) = get_numba_types('List' , True)
        core_list.clear()
        listInnerDict.clear()
        listDataDict.clear()

        marketLastIndex = marketWatchHandler.lastPricePRCAverge(decNum= S[0], num= 5)

        if len(marketLastIndex.keys()) == 0:
            return (None,None)

        # List
        core_list = cast_list_to_numba(core_list, marketLastIndex[marketGroupType.TotalMarket.value])
        listInnerDict.update({'MarketLastIndex': core_list.copy()})

        price = dataHandler.lastPrice(num= 1, IDList= tickersList)
        time = dataHandler.time(num= 1, IDList= tickersList)

        # Assembling
        for Id in price:
            listDataDict.update({Id: listInnerDict.copy()})
            floatInnerDict.update({'Time': int(time[Id][-1].strftime('%H%M'))})
            FloatDataDict.update({Id: floatInnerDict.copy()})

        return (FloatDataDict, listDataDict)
        

    @staticmethod
    def single_ticker_calculation(tickerFloatOnlineData: dict, tickerListOnlineData:dict, tickerOfflineData: dict, tickerHistoryData:dict, tickerId:int):
        # Check whether ticker history is None or not
        if tickerHistoryData is None:
            print('history is None!!')
            return (False, 69)
            
        limitIndex = -55

        marketLastIndexList = tickerListOnlineData['MarketLastIndex']
        tickerHistoryData['MaxIndex'] = max(tickerHistoryData['MaxIndex'], marketLastIndexList[-1])

        if tickerFloatOnlineData['Time'] < 910:
            return (False, 69)

        if marketLastIndexList[-1] < tickerHistoryData['MaxIndex'] - 20 or marketLastIndexList[-1] < limitIndex:
            return (False, 100)

        if marketLastIndexList[-1] <= max(marketLastIndexList) - 5:
            return (False, 80)
        else:
            return (False, 69)





