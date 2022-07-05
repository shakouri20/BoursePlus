from Application.Services.Middlewares.MiddlewareFramework.Middleware import *
from Infrastructure.Repository.OnlineDataRepository import onlineData_repo
from Infrastructure.Repository.OfflineDataRepository import offlineData_repo
from Application.Services.ReadData.ReadOffline.ReadOfflineServices import read_offline_services as rfs
from numba import jit
from numba.types import float32, unicode_type, ListType, float64, DictType, int64
from numba.typed import Dict, List
from math import log10
from datetime import datetime, timedelta

class obBuyPerCapitaDailyBuyMiddleware(middleware):

    def __init__(self, dataHandler, marketWatchHandler, mainTickersList: list, kargs):
        super(obBuyPerCapitaDailyBuyMiddleware, self).__init__(dataHandler, marketWatchHandler, mainTickersList, kargs)


    def get_online_data(self, tickersList: list, dataHandler: onlineDataHandler, marketWatchHandler: marketWatchDataHandler):
        # Getting  >> List << 
        (core_list, listInnerDict, listDataDict) = get_numba_types('List' , True)
        core_list.clear()
        listInnerDict.clear()
        listDataDict.clear()

        # Getting  >> Float64 <<
        (floatInnerDict, FloatDataDict) = get_numba_types('Float', True)
        floatInnerDict.clear()
        FloatDataDict.clear()

        buyPerCapita = dataHandler.demandPerCapita(num= 1)

        for Id in tickersList:
            if Id in buyPerCapita:

                # Float
                floatInnerDict.update({'PerCapitaDemand': buyPerCapita[Id][0]})
                
                # Assembling
                FloatDataDict.update({Id: floatInnerDict.copy()})

        return (FloatDataDict, None)



    @staticmethod
    def single_ticker_calculation(tickerFloatOnlineData: dict, tickerListOnlineData:dict, tickerOfflineData: dict, tickerHistoryData:dict, tickerId:int):
        
        limitScore = 0

        perCapitaDemand = tickerFloatOnlineData['PerCapitaDemand']

        # score = int(max(min(40 * log10(perCapitaDemand/30) + 35, 100), 0))
        score = int(max(min(perCapitaDemand/2, 100), 0))
        
        if score < limitScore:
            return (True, 0)
        else:
            return (False, score)


