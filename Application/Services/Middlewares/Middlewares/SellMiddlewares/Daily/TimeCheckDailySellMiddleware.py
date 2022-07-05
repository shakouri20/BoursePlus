from Application.Services.ReadData.ReadOnline.MarketWatchDataHandler import marketWatchDataHandler
from time import strftime
from Application.Services.ReadData.ReadOnline.OnlineDataHandler import onlineDataHandler
from Application.Services.Middlewares.MiddlewareFramework.Middleware import get_numba_types, middleware
from Application.Services.ReadData.ReadOffline.ReadOfflineServices import read_offline_services
from Domain.Enums.OnlineColumns import onlineColumns
from numba.types import float32, unicode_type, ListType, float64, DictType, int64
from numba.typed import Dict, List


class timeCheckDailySellMiddleware(middleware):

    def __init__(self, dataHandler, marketWatchHandler, mainTickersList: list, kargs):
        super(timeCheckDailySellMiddleware, self).__init__(dataHandler, marketWatchHandler, mainTickersList, kargs)

    def get_online_data(self, tickersList: list, dataHandler: onlineDataHandler, marketWatchHandler: marketWatchDataHandler):
        # Getting  >> Float64 <<
        (floatInnerDict, FloatDataDict) = get_numba_types('Float', True)
        floatInnerDict.clear()
        FloatDataDict.clear()

        currentTime = dataHandler.time(num= 1, IDList= tickersList)

        for Id in currentTime:
            # Float
            floatInnerDict.update({'Time' : int(currentTime[Id][-1].strftime('%H%M'))})
            
                # Assembling
            FloatDataDict.update({Id: floatInnerDict.copy()})

        return (FloatDataDict, None)


    @staticmethod
    def single_ticker_calculation(tickerFloatOnlineData: dict, tickerListOnlineData:dict, tickerOfflineData: dict, tickerHistoryData:dict, tickerId:int):
        time = tickerFloatOnlineData['Time']
        return (False, 69) if time < 1045 else (False, 100)

