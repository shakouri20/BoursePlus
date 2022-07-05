from Application.Services.Middlewares.MiddlewareFramework.Middleware import *
from Infrastructure.Repository.OnlineDataRepository import onlineData_repo
from Infrastructure.Repository.OfflineDataRepository import offlineData_repo
from Application.Services.ReadData.ReadOffline.ReadOfflineServices import read_offline_services as rfs
from numba import jit
from numba.types import float32, unicode_type, ListType, float64, DictType, int64
from numba.typed import Dict, List
from math import log10
from datetime import datetime, timedelta

S15 = [4]
S3 = [20]
S = S15

class valueDifDailyBuyMiddleware(middleware):

    def __init__(self, dataHandler, marketWatchHandler, mainTickersList: list, kargs):
        super(valueDifDailyBuyMiddleware, self).__init__(dataHandler, marketWatchHandler, mainTickersList, kargs)

    def get_online_data(self, tickersList: list, dataHandler: onlineDataHandler, marketWatchHandler: marketWatchDataHandler):
        # Getting  >> Float64 <<
        (floatInnerDict, FloatDataDict) = get_numba_types('Float', True)
        floatInnerDict.clear()
        FloatDataDict.clear()


        volumes = dataHandler.volumeDif(decNum= S[0], num= 1)
        lastPrice = dataHandler.lastPrice(num= 1)

        for Id in tickersList:
            if Id in volumes:
                # Float
                valueDif = volumes[Id][-1] * lastPrice[Id][0]
                floatInnerDict.update({'ValueDif' : valueDif})

                # Assembling
                FloatDataDict.update({Id: floatInnerDict.copy()})

        return (FloatDataDict, None)



    @staticmethod
    def single_ticker_calculation(tickerFloatOnlineData: dict, tickerListOnlineData:dict, tickerOfflineData: dict, tickerHistoryData:dict, tickerId:int):
                     
        valueDif = tickerFloatOnlineData['ValueDif']
            
        score = min(100, int(valueDif/(5 * 10**10)*100))
        
        return(False, score)