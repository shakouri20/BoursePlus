from numba.core.decorators import jit
from Application.Services.ReadData.ReadOnline.MarketWatchDataHandler import marketWatchDataHandler
from time import strftime
from Application.Services.ReadData.ReadOnline.OnlineDataHandler import onlineDataHandler
from Application.Services.Middlewares.MiddlewareFramework.Middleware import cast_list_to_numba, get_numba_types, middleware
from Application.Services.ReadData.ReadOffline.ReadOfflineServices import read_offline_services as rfs
from Application.Services.ReadData.ReadOffline.ReadOfflineServices import read_offline_services
from Domain.Enums.OnlineColumns import onlineColumns
from numba.types import float32, unicode_type, ListType, float64, DictType, int64
from numba.typed import Dict, List
from datetime import datetime
from ta.volatility import *
import pandas as pd
from math import log10

S15 = {'PriceLength': 4}
S3 = {'PriceLength': 20}
S = S3

class sellQueueSellDailySellMiddleware(middleware):

    def __init__(self, dataHandler, marketWatchHandler, mainTickersList: list, kargs):
        super(sellQueueSellDailySellMiddleware, self).__init__(dataHandler, marketWatchHandler, mainTickersList, kargs)


    def create_history_data(self, idList: list, dataHandler: onlineDataHandler, marketWatchHandler: marketWatchDataHandler) -> dict:
        if len(idList)==0:
            return None
            
        # Getting  >> Float64 <<
        (floatInnerDict, FloatDataDict) = get_numba_types('Float', False)
        floatInnerDict.clear()
        FloatDataDict.clear()

        # currentTime = dataHandler.time(num= 1)

        for id in idList:
            floatInnerDict.update({'BuyTime' : 0})
            floatInnerDict.update({'StartSell' : 0})

            # Assembling
            FloatDataDict.update({id: floatInnerDict.copy()})
        return FloatDataDict

    def read_offline_data(self, mainTickersList: list) -> dict:
        (inner_dict, dataDict) = get_numba_types('Float', False)
         
        volumeAvg = rfs.average.get_averge_volume(mainTickersList, 30)

        for Id in volumeAvg:
            inner_dict.update({'MonthlyVolume' : volumeAvg[Id]})
            dataDict[Id] = inner_dict.copy()
        return dataDict

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

        currentTime = dataHandler.time(num= 1, IDList= tickersList)
        minAllowedPrice = dataHandler.minAllowedPrice(IDList= tickersList)
        row1 = dataHandler.row1(decNum= 10, num= S['PriceLength'], IDList= tickersList)

        for Id in row1[onlineColumns.SupplyPrice1.value]:
            if len(row1[onlineColumns.SupplyPrice1.value][Id]) > 5:
                # List
                supplyPrice1 = row1[onlineColumns.SupplyPrice1.value][Id]

                core_list = cast_list_to_numba(core_list, supplyPrice1)
                listInnerDict.update({onlineColumns.SupplyPrice1.value: core_list.copy()})
                
                # Assembling
                listDataDict.update({Id: listInnerDict.copy()})

                supplyVolume1 = row1[onlineColumns.SupplyVolume1.value][Id][-1]
                demandVolume1 = row1[onlineColumns.DemandVolume1.value][Id][-1]

                # Float
                floatInnerDict.update({'MinAllowedPrice' : minAllowedPrice[Id]})
                floatInnerDict.update({'Time': int(currentTime[Id][-1].strftime('%H%M'))})
                floatInnerDict.update({onlineColumns.SupplyVolume1.value: supplyVolume1})
                floatInnerDict.update({onlineColumns.DemandVolume1.value: demandVolume1})
                
                # Assembling
                FloatDataDict.update({Id: floatInnerDict.copy()})

        return (FloatDataDict, listDataDict)

    @staticmethod
    def single_ticker_calculation(tickerFloatOnlineData: dict, tickerListOnlineData:dict, tickerOfflineData: dict, tickerHistoryData:dict, tickerId:int):
        # Check whether ticker history is None or not
        if tickerHistoryData is None:
            print('history is None!!')
            return (False, 69)

        currentTime = tickerFloatOnlineData['Time']
        supplyPrice1 = tickerListOnlineData[onlineColumns.SupplyPrice1.value]
        supplyVolume1 = tickerFloatOnlineData[onlineColumns.SupplyVolume1.value]
        demandVolume1 = tickerFloatOnlineData[onlineColumns.DemandVolume1.value]
        minAllowedPrice = tickerFloatOnlineData['MinAllowedPrice']

        

        if tickerHistoryData['BuyTime'] == 0:
            tickerHistoryData['BuyTime'] = tickerFloatOnlineData['Time']

        if tickerHistoryData['StartSell'] == 0:
            buyTimeDif = get_time_dif(tickerHistoryData['BuyTime'], currentTime)
            if buyTimeDif > 4 or demandVolume1 > 0:
                tickerHistoryData['StartSell'] = 1

        if tickerHistoryData['StartSell'] == 1:
            for price in supplyPrice1:
                if price != minAllowedPrice:
                    break
            else:
                return (False, 85)
            if supplyPrice1[-1] == minAllowedPrice and demandVolume1 == 0:
                sellQueueValue = supplyPrice1[-1] * supplyVolume1 / 10**7
                thresholdValue = tickerOfflineData['MonthlyVolume'] * supplyPrice1[-1] / 5 / 10**7
                if sellQueueValue > 300 and sellQueueValue > thresholdValue:
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