
from Application.Services.ReadData.ReadOnline.MarketWatchDataHandler import marketWatchDataHandler
from math import atan, floor, log10, pi
from Domain.Enums.OnlineColumns import onlineColumns
from Application.Services.ReadData.ReadOnline.OnlineDataHandler import onlineDataHandler
from Application.Services.Middlewares.MiddlewareFramework.Middleware import cast_list_to_numba, get_numba_types, middleware
from Application.Services.ReadData.ReadOffline.ReadOfflineServices import read_offline_services
from numba.types import float64, unicode_type, ListType, DictType, int64
from numba.typed import Dict, List
from math import inf
import datetime
from numba.core.decorators import jit

S15 = [10]
S3 = [50]
S = S3


class demandPowerDailySellMiddleware(middleware):

    def __init__(self, dataHandler, marketWatchHandler, mainTickersList: list, kargs):
        super(demandPowerDailySellMiddleware, self).__init__(dataHandler, marketWatchHandler, mainTickersList, kargs)

    def create_history_data(self, idList: list, dataHandler: onlineDataHandler, marketWatchHandler: marketWatchDataHandler) -> dict:
        if len(idList)==0:
            return None
            
        # Getting  >> Float64 <<
        (floatInnerDict, FloatDataDict) = get_numba_types('Float', False)
        floatInnerDict.clear()
        FloatDataDict.clear()

        for id in idList:
            floatInnerDict.update({'BuyTime' : 0})

            # Assembling
            FloatDataDict.update({id: floatInnerDict.copy()})
        return FloatDataDict

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
        lastPrice = dataHandler.lastPrice(num= S[0], IDList= tickersList)
        time = dataHandler.time(num= 1, IDList= tickersList)

        for Id in time:
            if len(lastPrice[Id]) > 5:
                # List
                core_list = cast_list_to_numba(core_list, row1[onlineColumns.SupplyPrice1.value][Id])
                listInnerDict.update({onlineColumns.SupplyPrice1.value: core_list.copy()})

                core_list = cast_list_to_numba(core_list, row1[onlineColumns.DemandPrice1.value][Id])
                listInnerDict.update({onlineColumns.DemandPrice1.value: core_list.copy()})
                core_list = cast_list_to_numba(core_list, row1[onlineColumns.DemandPrice1.value][Id])
                listInnerDict.update({onlineColumns.DemandPrice1.value: core_list.copy()})
                
                core_list = cast_list_to_numba(core_list, lastPrice[Id])
                listInnerDict.update({'LastPrice': core_list.copy()})

                # Assembling
                listDataDict.update({Id: listInnerDict.copy()})

                # Float
                floatInnerDict.update({'Time':  int(time[Id][-1].strftime('%H%M'))})
                
                # Assembling
                FloatDataDict.update({Id: floatInnerDict.copy()})

        return (FloatDataDict, listDataDict)

    @staticmethod
    def single_ticker_calculation(tickerFloatOnlineData: dict, tickerListOnlineData:dict, tickerOfflineData: dict, tickerHistoryData:dict, tickerId:int):
        # Check whether ticker history is None or not
        if tickerHistoryData is None:
            print('history is None!!')
            return (False, 69)

        if tickerHistoryData['BuyTime'] == 0:
            tickerHistoryData['BuyTime'] = tickerFloatOnlineData['Time']

        buyTimeDif = get_time_dif(tickerHistoryData['BuyTime'], tickerFloatOnlineData['Time'])

        if buyTimeDif > 10:

            supplyPrice1: list = tickerListOnlineData[onlineColumns.SupplyPrice1.value]
            demandPrice1: list = tickerListOnlineData[onlineColumns.DemandPrice1.value]
            lastPrice: list = tickerListOnlineData['LastPrice']
           
            demandPowerList = [0 for i in range(len(lastPrice))]
            for i in range(len(lastPrice)):
                if demandPrice1[i] <= lastPrice[i] <= supplyPrice1[i] and supplyPrice1[i] != demandPrice1[i]:
                    demandPowerList[i] = (lastPrice[i]-demandPrice1[i])/(supplyPrice1[i]-demandPrice1[i])*100
                elif lastPrice[i] < demandPrice1[i]:
                    demandPowerList[i] = 1

            if sum(demandPowerList)/len(demandPowerList) < 15:
                return (False, 100)
                
        return (False, 69)

@jit
def get_time_dif(t1,t2):
    t1m = t1 % 100
    t1H = (t1 - t1m)/100

    t2m = t2 % 100
    t2H = (t2 - t2m)/100

    difm = t2m - t1m
    difH = (t2H - t1H)*60
    return difH + difm