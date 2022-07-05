from Application.Services.Middlewares.MiddlewareFramework.Middleware import *
from Infrastructure.Repository.OnlineDataRepository import onlineData_repo
from Infrastructure.Repository.OfflineDataRepository import offlineData_repo
from Application.Services.ReadData.ReadOffline.ReadOfflineServices import read_offline_services as rfs
from numba import jit
from numba.types import float32, unicode_type, ListType, float64, DictType, int64
from numba.typed import Dict, List
from math import log10
from datetime import datetime, timedelta
from Infrastructure.Repository.OfflineDataRepository import offlineData_repo as orepo

S15 = [4]
S3 = [20]
S = S15

class volumeAverageDailyBuyMiddleware(middleware):

    def __init__(self, dataHandler, marketWatchHandler, mainTickersList: list, kargs):
        super(volumeAverageDailyBuyMiddleware, self).__init__(dataHandler, marketWatchHandler, mainTickersList, kargs)

    def create_history_data(self, idList: list, dataHandler: onlineDataHandler, marketWatchHandler: marketWatchDataHandler) -> dict:
        if len(idList)==0:
            return None
            
        # Getting  >> Float64 <<
        (floatInnerDict, FloatDataDict) = get_numba_types('Float', False)
        floatInnerDict.clear()
        FloatDataDict.clear()

        # currentTime = dataHandler.time(num= 1)

        for id in idList:
            floatInnerDict.update({'StartTime' : 0})
            floatInnerDict.update({'StartVolume' : 0})
            # Assembling
            FloatDataDict.update({id: floatInnerDict.copy()})
        return FloatDataDict

    def read_offline_data(self, mainTickersList: list) -> dict:
        (inner_dict, dataDict) = get_numba_types('Float', False)
         
        monthlyVolume = rfs.average.get_averge_volume(mainTickersList, 30)
        volumeAvg5day = rfs.average.get_averge_volume(mainTickersList, 5)

        for Id in monthlyVolume:
            inner_dict.update({'MonthlyVolume' : monthlyVolume[Id]})
            inner_dict.update({'VolumeAvg5day' : volumeAvg5day[Id]})
            dataDict[Id] = inner_dict.copy()
        return dataDict

    def get_online_data(self, tickersList: list, dataHandler: onlineDataHandler, marketWatchHandler: marketWatchDataHandler):
        # Getting  >> Float64 <<
        (floatInnerDict, FloatDataDict) = get_numba_types('Float', True)
        floatInnerDict.clear()
        FloatDataDict.clear()

        volume = dataHandler.volume(num= 1)
        currentTime = dataHandler.time(num= 1)


        for Id in tickersList:
            if Id in volume:

                floatInnerDict.update({'Volume' : volume[Id][-1]})
                floatInnerDict.update({'Time' : int(currentTime[Id][-1].strftime('%H%M'))})

                # Assembling
                FloatDataDict.update({Id: floatInnerDict.copy()})

        return (FloatDataDict, None)



    @staticmethod
    def single_ticker_calculation(tickerFloatOnlineData: dict, tickerListOnlineData:dict, tickerOfflineData: dict, tickerHistoryData:dict, tickerId:int):

        if tickerHistoryData is None:
            print('history is None!!')
            return (True, 0)

        if tickerHistoryData['StartTime'] == 0:
            tickerHistoryData['StartTime'] = tickerFloatOnlineData['Time']

        thisTimeDif = get_time_dif(tickerHistoryData['StartTime'], tickerFloatOnlineData['Time'])
        totalTimeDif = get_time_dif(tickerHistoryData['StartTime'], 1230)

        if thisTimeDif <= 10:
            tickerHistoryData['StartVolume'] = tickerFloatOnlineData['Volume']


        monthlyVolume = tickerOfflineData['MonthlyVolume']
        volumeAvg5day = tickerOfflineData['VolumeAvg5day']
        todayVolume = tickerFloatOnlineData['Volume']


        if thisTimeDif > 10:
            todayScaledVolume = tickerHistoryData['StartVolume'] + (todayVolume-tickerHistoryData['StartVolume']) * (totalTimeDif / thisTimeDif)
            normalVolume = (todayScaledVolume + 5 * volumeAvg5day) / 6
        else:
            normalVolume = volumeAvg5day

        normalVolume /= monthlyVolume
        
        score = max(min(100, int(50*log10(normalVolume)+50)), 0)
        
        return(False, score)

@jit
def get_time_dif(t1,t2):
    t1m = t1 % 100
    t1H = (t1 - t1m)/100

    t2m = t2 % 100
    t2H = (t2 - t2m)/100

    difm = t2m - t1m
    difH = (t2H - t1H)*60
    return difH + difm