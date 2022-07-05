from Application.Services.Middlewares.MiddlewareFramework.Middleware import *
from numba import jit
from numba.types import float32, unicode_type, ListType, float64, DictType, int64
from numba.typed import Dict, List
from math import log10

class volumeDailySellMiddleware(middleware):
    def __init__(self, mainTickersList: list, **kargs):
        middleware(volumeDailySellMiddleware, self).__init__(mainTickersList, kargs)
        
    def read_offline_data(self, mainTickersList: list) -> dict:
        inner_dict_type = DictType(unicode_type, float64)
        inner_dict = Dict.empty(unicode_type, float64)
        
        dataDict = Dict.empty(
         key_type = int64,
         value_type= inner_dict_type,)

        db = database_repo()
        db.connect()
        volumeAvg = db.read_monthly_Volume_by_ID_list(mainTickersList)
        db.close()
        for Id in volumeAvg:
            inner_dict['volumeAvg'] = volumeAvg[Id]
            dataDict[Id] = inner_dict.copy()
        return dataDict

    def get_online_data(self, tickersList: list) -> dict:
        inner_dict_type = DictType(unicode_type, float64)
        inner_dict = Dict.empty(unicode_type, float64)
        
        dataDict = Dict.empty(
         key_type = int64,
         value_type= inner_dict_type,)

        db = database_repo()
        db.connect()
        data = db.read_online_lastData('Volume', 'RealPower', IDList= tickersList)
        db.close()

        for Id in data:
            inner_dict['RealPower'] = data[Id]['RealPower']
            inner_dict['Volume'] = data[Id]['Volume']
            dataDict[Id] = inner_dict.copy()
        return dataDict

    @staticmethod
    def single_ticker_calculation(tickerOnlineData: dict, tickerOfflineData: dict):
        delete = False # True or False
        score = 0 # 0 < score < 100
        volLog = log10(tickerOnlineData['Volume'] / tickerOfflineData['volumeAvg'])
        if volLog < -1:
            delete = True
            return delete, score
        else:
            if volLog >= 1:
                score = 100
            elif volLog >= 0:
                score = int(30   + 70*(volLog))
            elif volLog < 0:
                score = int(30 + 30*(volLog))
            delete = False
        if score < 50 :
            delete = True
        return delete, score