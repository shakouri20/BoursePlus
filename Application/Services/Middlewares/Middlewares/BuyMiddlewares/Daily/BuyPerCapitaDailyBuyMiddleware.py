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


class buyPerCapitaDailyBuyMiddleware(middleware):

    def __init__(self, dataHandler, marketWatchHandler, mainTickersList: list, kargs):
        super(buyPerCapitaDailyBuyMiddleware, self).__init__(dataHandler, marketWatchHandler, mainTickersList, kargs)


    def get_online_data(self, tickersList: list, dataHandler: onlineDataHandler, marketWatchHandler: marketWatchDataHandler):
        # Getting  >> Float64 <<
        (floatInnerDict, FloatDataDict) = get_numba_types('Float', True)
        floatInnerDict.clear()
        FloatDataDict.clear()

        buyPerCapita = dataHandler.perCapitaBuyDif(decNum= S[0], num= 1)

        for Id in tickersList:
            if Id in buyPerCapita:
                # Float
                perCapita = buyPerCapita[Id][-1]
                if perCapita >=0 :
                    floatInnerDict.update({'BuyPerCapita' : perCapita})
                
                     # Assembling
                    FloatDataDict.update({Id: floatInnerDict.copy()})

        # if len(FloatDataDict.keys()) == 0:
        #     return (None, None)

        return (FloatDataDict, None)



    @staticmethod
    def single_ticker_calculation(tickerFloatOnlineData: dict, tickerListOnlineData:dict, tickerOfflineData: dict, tickerHistoryData:dict, tickerId:int):
        
        limitScore = 40

        buyPerCapita = tickerFloatOnlineData['BuyPerCapita']
            
        score = int(max(min(40 * log10(buyPerCapita/30) + 35, 100), 0))
        
        if score < limitScore:
            return (True, 0)
        else:
            return (False, score)