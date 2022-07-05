from Application.Services.ReadData.ReadOffline.ReadOfflineServices import read_offline_services as rfs
from Application.Services.Middlewares.MiddlewareFramework.Middleware import *
import time as t

S15 = {'row1': 20}
S3 = {'row1': 120}
S = S3


class sellQueueCheckDailyBuyMiddleware(middleware):

    def __init__(self, dataHandler, marketWatchHandler, mainTickersList: list, kargs):
        super(sellQueueCheckDailyBuyMiddleware, self).__init__(dataHandler, marketWatchHandler, mainTickersList, kargs)


    def read_offline_data(self, mainTickersList: list) -> dict:
        (inner_dict, dataDict) = get_numba_types('Float', False)
         
        volumeAvg = rfs.average.get_averge_volume(mainTickersList, 30)

        for Id in volumeAvg:
            if volumeAvg[Id] != 0:
                inner_dict.update({'VolumeAvg' : volumeAvg[Id]/3.5/3600})
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

        row1 = dataHandler.row1(num= S['row1'], IDList= tickersList)
        minAllowedPrice = dataHandler.minAllowedPrice(IDList= tickersList)
        time = dataHandler.time(num= 1, IDList= tickersList)

        for Id in row1[onlineColumns.SupplyPrice1.value]:
            # List
            core_list = cast_list_to_numba(core_list, row1[onlineColumns.SupplyPrice1.value][Id])
            listInnerDict.update({onlineColumns.SupplyPrice1.value: core_list.copy()})

            core_list = cast_list_to_numba(core_list, row1[onlineColumns.SupplyVolume1.value][Id])
            listInnerDict.update({onlineColumns.SupplyVolume1.value: core_list.copy()})

            # Assembling
            listDataDict.update({Id: listInnerDict.copy()})

            # Float
            floatInnerDict.update({onlineColumns.MinAllowedPrice.value: minAllowedPrice[Id]})
            floatInnerDict.update({'Time':  int(time[Id][-1].strftime('%H%M'))})
            
            # Assembling
            FloatDataDict.update({Id: floatInnerDict.copy()})
                
        return (FloatDataDict, listDataDict)

    @staticmethod
    def single_ticker_calculation(tickerFloatOnlineData: dict, tickerListOnlineData:dict, tickerOfflineData: dict, tickerHistoryData:dict, tickerId:int):
        
        supplyPrice1: list = tickerListOnlineData[onlineColumns.SupplyPrice1.value]
        supplyVolume1: list = tickerListOnlineData[onlineColumns.SupplyVolume1.value]
        minAllowedPrice = tickerFloatOnlineData[onlineColumns.MinAllowedPrice.value]
        monthlyVolumeAvgInSecond = tickerOfflineData['VolumeAvg']

        maxSellQueueVolume = max(supplyVolume1)
        maxSellQueueVolumeIndex = supplyVolume1.index(maxSellQueueVolume)
        firstIndex = 0 if tickerFloatOnlineData['Time'] > 918 else maxSellQueueVolumeIndex

        for i in range(firstIndex, len(supplyPrice1)-3):
            if supplyPrice1[i] != minAllowedPrice:
                return (True, 10)

        normalVolumeDif = (maxSellQueueVolume - supplyVolume1[-1]) / (60 * monthlyVolumeAvgInSecond)

        if normalVolumeDif > 35:
            if supplyPrice1[-1] != minAllowedPrice:
                return (False, min(50 + int(normalVolumeDif),100))
            else:
                # nowSellQueueValue = supplyVolume1[-1] * minAllowedPrice / 10**7
                if supplyVolume1[-1] < 0.20 * maxSellQueueVolume: #  and nowSellQueueValue < 350
                    return (False, min(50, int(normalVolumeDif)))

        return (True, 20)