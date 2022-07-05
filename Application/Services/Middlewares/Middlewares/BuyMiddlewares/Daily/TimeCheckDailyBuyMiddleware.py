from Application.Services.Middlewares.MiddlewareFramework.Middleware import *
from Infrastructure.Repository.OnlineDataRepository import onlineData_repo
from Infrastructure.Repository.OfflineDataRepository import offlineData_repo
from Application.Services.ReadData.ReadOffline.ReadOfflineServices import read_offline_services as rfs
from numba import jit
from numba.types import float32, unicode_type, ListType, float64, DictType, int64
from numba.typed import Dict, List
from math import log10
from datetime import datetime, timedelta


class timeCheckDailyBuyMiddleware(middleware):

    def __init__(self, dataHandler, marketWatchHandler, mainTickersList: list, kargs):
        super(timeCheckDailyBuyMiddleware, self).__init__(dataHandler, marketWatchHandler, mainTickersList, kargs)


    def get_online_data(self, tickersList: list, dataHandler: onlineDataHandler, marketWatchHandler: marketWatchDataHandler):
        # Getting  >> Float64 <<
        (floatInnerDict, FloatDataDict) = get_numba_types('Float', True)
        floatInnerDict.clear()
        FloatDataDict.clear()

        time = dataHandler.time(num= 1, IDList= tickersList)

        for Id in time:
            floatInnerDict.update({'Time': int(time[Id][-1].strftime('%H%M'))})
            
            # Assembling
            FloatDataDict.update({Id: floatInnerDict.copy()})

        return (FloatDataDict, None)



    @staticmethod
    def single_ticker_calculation(tickerFloatOnlineData: dict, tickerListOnlineData:dict, tickerOfflineData: dict, tickerHistoryData:dict, tickerId:int):
        
        time = tickerFloatOnlineData['Time']

        return (True , 0) if time > 1030 else (False, 50)



