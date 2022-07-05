from Application.Services.Middlewares.MiddlewareFramework.Middleware import *
from Infrastructure.Repository.OnlineDataRepository import onlineData_repo
from Infrastructure.Repository.OfflineDataRepository import offlineData_repo
from Application.Services.ReadData.ReadOffline.ReadOfflineServices import read_offline_services as rfs
from numba import jit
from numba.types import float32, unicode_type, ListType, float64, DictType, int64
from numba.typed import Dict, List
from math import log10
from datetime import datetime, timedelta

S15 = [15]
S3 = [100]
S = S3


class obSellPerCapitaDailyBuyMiddleware(middleware):

    def __init__(self, dataHandler, marketWatchHandler, mainTickersList: list, kargs):
        super(obSellPerCapitaDailyBuyMiddleware, self).__init__(dataHandler, marketWatchHandler, mainTickersList, kargs)


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

        row1 = dataHandler.row1(num= S[0], IDList= tickersList)
        supplyVolume1 = row1[onlineColumns.SupplyVolume1.value]
        supplyPrice1 = row1[onlineColumns.SupplyPrice1.value]
        supplyNumber1 = row1[onlineColumns.SupplyNumber1.value]

        for Id in supplyVolume1:
            # List
            core_list = cast_list_to_numba(core_list, supplyPrice1[Id])
            listInnerDict.update({onlineColumns.SupplyPrice1.value: core_list.copy()})

            core_list = cast_list_to_numba(core_list, supplyVolume1[Id])
            listInnerDict.update({onlineColumns.SupplyVolume1.value: core_list.copy()})

            core_list = cast_list_to_numba(core_list, supplyNumber1[Id])
            listInnerDict.update({onlineColumns.SupplyNumber1.value: core_list.copy()})

            # Assembling
            listDataDict.update({Id: listInnerDict.copy()})

            # Float
            floatInnerDict.update({'None': 0})
            
            # Assembling
            FloatDataDict.update({Id: floatInnerDict.copy()})

        return (FloatDataDict, listDataDict)


    @staticmethod
    def single_ticker_calculation(tickerFloatOnlineData: dict, tickerListOnlineData:dict, tickerOfflineData: dict, tickerHistoryData:dict, tickerId:int):
        
        limitPerCapita = 70

        supplyPrice1: list = tickerListOnlineData[onlineColumns.SupplyPrice1.value]
        supplyVolume1: list = tickerListOnlineData[onlineColumns.SupplyVolume1.value]
        supplyNumber1:list = tickerListOnlineData[onlineColumns.SupplyNumber1.value]

        for i in range(len(supplyNumber1)):
            if supplyNumber1[i] == 0:
                return (True, 0)

        supplyPerCapita1 = [supplyVolume1[i]*supplyPrice1[i]/supplyNumber1[i]/10**7 for i in range(len(supplyNumber1))]
        maxSupplyPerCapita = listSum(supplyPerCapita1) / len(supplyPerCapita1)

        if maxSupplyPerCapita > limitPerCapita:
            return (True, 20)
        else:
            return (False, 100)

    
@jit
def listSum(numList):
    Sum = 0
    for num in numList:
        Sum += num
    return Sum
