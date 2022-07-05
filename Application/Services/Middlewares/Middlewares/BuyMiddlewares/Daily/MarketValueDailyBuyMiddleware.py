from Application.Services.ReadData.ReadOnline.MarketWatchDataHandler import marketWatchDataHandler
from math import atan, floor, log10, pi
from Domain.Enums.OnlineColumns import onlineColumns
from Application.Services.ReadData.ReadOnline.OnlineDataHandler import onlineDataHandler
from Application.Services.Middlewares.MiddlewareFramework.Middleware import cast_list_to_numba, get_numba_types, middleware
from Application.Services.ReadData.ReadOffline.ReadOfflineServices import read_offline_services
from numba.types import float64, unicode_type, ListType, DictType, int64
from numba.typed import Dict, List
from Domain.ImportEnums import *
from numba import jit

class marketValueDailyBuyMiddleware(middleware):

    def __init__(self, dataHandler, marketWatchHandler, mainTickersList: list, kargs):
        super(marketValueDailyBuyMiddleware, self).__init__(dataHandler, marketWatchHandler, mainTickersList, kargs)

    def create_history_data(self, idList: list, dataHandler: onlineDataHandler, marketWatchHandler: marketWatchDataHandler) -> dict:
            if len(idList)==0:
                return None
                
            # Getting  >> Float64 <<
            (floatInnerDict, FloatDataDict) = get_numba_types('Float', False)
            floatInnerDict.clear()
            FloatDataDict.clear()

            for id in idList:
                floatInnerDict.update({'StartValue' : 0})
                floatInnerDict.update({'StartTime' : 0})
                # Assembling
                FloatDataDict.update({id: floatInnerDict.copy()})
            return FloatDataDict

    def get_online_data(self, tickersList: list, dataHandler: onlineDataHandler, marketWatchHandler:marketWatchDataHandler):
        # Getting  >> Float64 <<
        (floatInnerDict, FloatDataDict) = get_numba_types('Float', True)
        floatInnerDict.clear()
        FloatDataDict.clear()

        marketValue = marketWatchHandler.totalValue(num= 1)
        currentTime = marketWatchHandler.time(num= 1)

        if len(marketValue.keys()) != 1:
            return (None,None)

        for Id in tickersList:

            floatInnerDict.update({'Value' : marketValue[marketGroupType.TotalMarket.value][-1]})
            floatInnerDict.update({'Time' : int(currentTime[marketGroupType.TotalMarket.value][-1].strftime('%H%M'))})

            FloatDataDict.update({Id: floatInnerDict.copy()})

        return (FloatDataDict, None)
        

    @staticmethod
    def single_ticker_calculation(tickerFloatOnlineData: dict, tickerListOnlineData:dict, tickerOfflineData: dict, tickerHistoryData:dict, tickerId:int):
        
        limitScore = 0

        currentTime = tickerFloatOnlineData['Time']
        value = tickerFloatOnlineData['Value']

        
        if tickerHistoryData['StartValue'] == 0:
            tickerHistoryData['StartValue'] = value
            tickerHistoryData['StartTime'] = currentTime
            return (False, 0) ##################

        thisTimeDif = get_time_dif(tickerHistoryData['StartTime'], currentTime)

        if thisTimeDif == 0:
            return (False, 0) ##################

        totalTimeDif = get_time_dif(tickerHistoryData['StartTime'], 1230)

        scaledValue = tickerHistoryData['StartValue'] + (value-tickerHistoryData['StartValue']) * (totalTimeDif / thisTimeDif)

        score = int(max(min(scaledValue/200, 100), 0))

        if score < limitScore:
            return (True, 0)
        else:
            return (False, score)


@jit
def get_time_dif(t1,t2):
    t1m = t1 % 100
    t1H = (t1 - t1m)/100

    t2m = t2 % 100
    t2H = (t2 - t2m)/100

    difm = t2m - t1m
    difH = (t2H - t1H)*60
    return difH + difm