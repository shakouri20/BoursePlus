from Domain.Enums.MarketGroups import marketGroupType
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

S15 = {'row1': 10, 'market': 5, 'demToSup': 10}
S3 = {'row1': 50, 'market': 25, 'demToSup': 50}
S = S3


class rangeDemToSupDailySellMiddleware(middleware):

    def __init__(self, dataHandler, marketWatchHandler, mainTickersList: list, kargs):
        super(rangeDemToSupDailySellMiddleware, self).__init__(dataHandler, marketWatchHandler, mainTickersList, kargs)


    def create_history_data(self, idList: list, dataHandler: onlineDataHandler, marketWatchHandler: marketWatchDataHandler) -> dict:
        if len(idList)==0:
            return None
            
        # Getting  >> Float64 <<
        (floatInnerDict, FloatDataDict) = get_numba_types('Float', False)
        floatInnerDict.clear()
        FloatDataDict.clear()

        for id in idList:
            floatInnerDict.update({'BuyTime' : 0})
            floatInnerDict.update({'TriggerTime' : 0})

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

        row1 = dataHandler.row1(num= S['row1'], IDList= tickersList)
        lastPrice = dataHandler.lastPrice(num= S['row1'], IDList= tickersList)
        marketLastIndex = marketWatchHandler.lastPricePRCAverge(num= 5 * S['market'])
        demToSup = dataHandler.demandToSupplyPower(num= S['demToSup'], IDList = tickersList)
        time = dataHandler.time(num= 1, IDList= tickersList)

        for Id in tickersList:
            # List
            core_list = cast_list_to_numba(core_list, row1[onlineColumns.SupplyPrice1.value][Id])
            listInnerDict.update({onlineColumns.SupplyPrice1.value: core_list.copy()})

            core_list = cast_list_to_numba(core_list, row1[onlineColumns.DemandPrice1.value][Id])
            listInnerDict.update({onlineColumns.DemandPrice1.value: core_list.copy()})

            core_list = cast_list_to_numba(core_list, lastPrice[Id])
            listInnerDict.update({'LastPrice': core_list.copy()})

            core_list = cast_list_to_numba(core_list, marketLastIndex[marketGroupType.TotalMarket.value])
            listInnerDict.update({'LastIndex': core_list.copy()})
            
            core_list = cast_list_to_numba(core_list, demToSup[Id])
            listInnerDict.update({'DemToSup': core_list.copy()})

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

        if buyTimeDif < 10:
            
            demToSup = tickerListOnlineData['DemToSup']
            demToSupAverage = listSum(demToSup)/len(demToSup)

            if demToSupAverage < -0.7:
                return (False, 95)

        else:

            # demandPower trigger
            supplyPrice1: list = tickerListOnlineData[onlineColumns.SupplyPrice1.value]
            demandPrice1: list = tickerListOnlineData[onlineColumns.DemandPrice1.value]
            lastPrice: list = tickerListOnlineData['LastPrice']
           
            demandPowerList = [0 for i in range(len(lastPrice))]
            for i in range(len(lastPrice)):
                if demandPrice1[i] <= lastPrice[i] <= supplyPrice1[i] and supplyPrice1[i] != demandPrice1[i]:
                    demandPowerList[i] = (lastPrice[i]-demandPrice1[i])/(supplyPrice1[i]-demandPrice1[i])*100
                elif lastPrice[i] < demandPrice1[i]:
                    demandPowerList[i] = 1

            demandPowerAverage = sum(demandPowerList)/len(demandPowerList)

            if demandPowerAverage < 15 or demandPowerAverage > 50:
                tickerHistoryData['TriggerTime'] = tickerFloatOnlineData['Time']

            # range trigger
            maxPrice = max(tickerListOnlineData['LastPrice'])
            minPrice = min(tickerListOnlineData['LastPrice'])   
            priceRange = (maxPrice-minPrice) / minPrice * 100
            if priceRange < 0.7:
                tickerHistoryData['TriggerTime'] = tickerFloatOnlineData['Time']

            triggerTimeDif = get_time_dif(tickerHistoryData['TriggerTime'], tickerFloatOnlineData['Time'])

            if triggerTimeDif > 5:
                return (False, 69)

            # demToSup confirmation
            demToSup = tickerListOnlineData['DemToSup']
            demToSupAverage = listSum(demToSup)/len(demToSup)

            if demToSupAverage < -0.2:
                return (False, 90)

            # market confirmation
            marketLastIndexList = tickerListOnlineData['LastIndex']

            if not (marketLastIndexList[-1] >= min(marketLastIndexList) + 1 and marketLastIndexList[-1] >= max(marketLastIndexList) - 1):
                if demToSupAverage < 0.8:
                    return (False, 85)


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

    
@jit
def listSum(numList):
    Sum = 0
    for num in numList:
        Sum += num
    return Sum
