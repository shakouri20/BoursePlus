from Application.Services.Middlewares.MiddlewareFramework.Middleware import *
from Infrastructure.Repository.OnlineDataRepository import onlineData_repo
from Infrastructure.Repository.OfflineDataRepository import offlineData_repo
from Application.Services.ReadData.ReadOffline.ReadOfflineServices import read_offline_services as rfs
from Infrastructure.Repository.TickerRepository import ticker_repo
from numba import jit
from numba.types import float32, unicode_type, ListType, float64, DictType, int64
from numba.typed import Dict, List
from math import log10
from datetime import datetime, timedelta
from Infrastructure.Repository.OfflineDataRepository import offlineData_repo as orepo

S15 = [4]
S3 = [20]
S = S15

class priceChangeDailyBuyMiddleware(middleware):

    def __init__(self, dataHandler, marketWatchHandler, mainTickersList: list, kargs):
        super(priceChangeDailyBuyMiddleware, self).__init__(dataHandler, marketWatchHandler, mainTickersList, kargs)

    def read_offline_data(self, mainTickersList: list) -> dict:
        (inner_dict, dataDict) = get_numba_types('Float', False)
         
        data7day = orepo().read_last_N_offlineData('ClosePrice', Num= 5, IDList= mainTickersList)

        for Id in data7day:

            Price1 = data7day[Id]['ClosePrice'][0]
            Price2 = data7day[Id]['ClosePrice'][-1]

            inner_dict.update({'Price1' : Price1})
            inner_dict.update({'Price2' : Price2})
            dataDict[Id] = inner_dict.copy()
        return dataDict

    def get_online_data(self, tickersList: list, dataHandler: onlineDataHandler, marketWatchHandler: marketWatchDataHandler):
        # Getting  >> Float64 <<
        (floatInnerDict, FloatDataDict) = get_numba_types('Float', True)
        floatInnerDict.clear()
        FloatDataDict.clear()

        lastPrice = dataHandler.lastPrice(num= 1)

        for Id in tickersList:
            if Id in lastPrice:

                floatInnerDict.update({'None' : 0})

                # Assembling
                FloatDataDict.update({Id: floatInnerDict.copy()})

        return (FloatDataDict, None)



    @staticmethod
    def single_ticker_calculation(tickerFloatOnlineData: dict, tickerListOnlineData:dict, tickerOfflineData: dict, tickerHistoryData:dict, tickerId:int):

        price1 = tickerOfflineData['Price1']
        price2 = tickerOfflineData['Price2']

        if price1 != 0:
            priceChange = (price2-price1)/price1*100
        else:
            priceChange = 0

        score = max(min(100, int(priceChange*5/3+50)), 0)
        
        return(False, score)
