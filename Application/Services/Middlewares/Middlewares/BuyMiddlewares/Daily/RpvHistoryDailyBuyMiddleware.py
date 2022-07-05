from typing import final
from Application.Services.Middlewares.MiddlewareFramework.Middleware import *
from Infrastructure.Repository.OnlineDataRepository import onlineData_repo
from Infrastructure.Repository.OfflineDataRepository import offlineData_repo
from Application.Services.ReadData.ReadOffline.ReadOfflineServices import read_offline_services as rfs
from Infrastructure.Repository.TickerRepository import ticker_repo
from numba import jit
from numba.types import float32, unicode_type, ListType, float64, DictType, int64
from numba.typed import Dict, List
from math import exp, log10
from datetime import datetime, timedelta
from Infrastructure.Repository.OfflineDataRepository import offlineData_repo as orepo

S15 = [4]
S3 = [20]
S = S15

class rpvHistoryDailyBuyMiddleware(middleware):

    def __init__(self, dataHandler, marketWatchHandler, mainTickersList: list, kargs):
        super(rpvHistoryDailyBuyMiddleware, self).__init__(dataHandler, marketWatchHandler, mainTickersList, kargs)

    def create_history_data(self, idList: list, dataHandler: onlineDataHandler, marketWatchHandler: marketWatchDataHandler) -> dict:
        if len(idList)==0:
            return None
            
        # Getting  >> Float64 <<
        (floatInnerDict, FloatDataDict) = get_numba_types('Float', False)
        floatInnerDict.clear()
        FloatDataDict.clear()

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
        
        data5day = orepo().read_last_N_offlineData('RealPower', 'Value', 'TodayPrice', Num= 5, IDList= mainTickersList)
        IpoIds = ticker_repo().read_list_of_tickers(IPO = 1)['ID'] # IPO Ids


        for Id in monthlyVolume:

            volumes = [int(data5day[Id]['Value'][i]/data5day[Id]['TodayPrice'][i]) for i in range(len(data5day[Id]['Value']))]
            realPowers = data5day[Id]['RealPower']

            rpvpSigma = 0

            realPowerAvg = 1
            if Id in IpoIds:
                realPowerAvg = sum(realPowers)/len(realPowers)

            for i in range(len(realPowers)):
                rpvpSigma += volumes[i]*realPowers[i]

            inner_dict.update({'MonthlyVolume' : monthlyVolume[Id]})
            inner_dict.update({'VolumeAvg5day' : volumeAvg5day[Id]})
            inner_dict.update({'RpvpSigma5day' : rpvpSigma})
            inner_dict.update({'VolumesSigma5day' : sum(volumes)})
            inner_dict.update({'RealPowerAvg' : realPowerAvg})
            dataDict[Id] = inner_dict.copy()
        return dataDict

    def get_online_data(self, tickersList: list, dataHandler: onlineDataHandler, marketWatchHandler: marketWatchDataHandler):
        # Getting  >> Float64 <<
        (floatInnerDict, FloatDataDict) = get_numba_types('Float', True)
        floatInnerDict.clear()
        FloatDataDict.clear()

        volume = dataHandler.volume(num= 1)
        currentTime = dataHandler.time(num= 1)
        realPower = dataHandler.realPower(num= 1)

        for Id in tickersList:
            if Id in volume:

                floatInnerDict.update({'Volume' : volume[Id][-1]})
                floatInnerDict.update({'Time' : int(currentTime[Id][-1].strftime('%H%M'))})
                floatInnerDict.update({'RealPower' : realPower[Id][-1]})

                # Assembling
                FloatDataDict.update({Id: floatInnerDict.copy()})

        return (FloatDataDict, None)



    @staticmethod
    def single_ticker_calculation(tickerFloatOnlineData: dict, tickerListOnlineData:dict, tickerOfflineData: dict, tickerHistoryData:dict, tickerId:int):

        limitScore = 35

        if tickerHistoryData is None:
            print('history is None!!')
            return (True, 0)
        
        # volume calculation
        if tickerHistoryData['StartTime'] == 0:
            tickerHistoryData['StartTime'] = tickerFloatOnlineData['Time']

        todayTime = get_time_dif(tickerHistoryData['StartTime'], tickerFloatOnlineData['Time'])

        if todayTime <= 5:
            tickerHistoryData['StartVolume'] = tickerFloatOnlineData['Volume']


        monthlyVolume = tickerOfflineData['MonthlyVolume']
        volumeAvg5day = tickerOfflineData['VolumeAvg5day']
        todayVolume = tickerFloatOnlineData['Volume']


        if todayTime > 5:
            todayScaledVolume = tickerHistoryData['StartVolume'] + (todayVolume-tickerHistoryData['StartVolume']) * (205 / (todayTime-5))
            normalVolume = (todayScaledVolume + 5 * volumeAvg5day) / 6
        else:
            normalVolume = volumeAvg5day

        normalVolume /= monthlyVolume
        
        volumeLog = log10(normalVolume)
        
        # realPower calculation
        rpvpSigma5day = tickerOfflineData['RpvpSigma5day']
        volumesSigma5day = tickerOfflineData['VolumesSigma5day']
        todayVolume = tickerFloatOnlineData['Volume']
        todayRealPower = tickerFloatOnlineData['RealPower']
        realPowerAverage5day = tickerOfflineData['RealPowerAvg']

        try:
            realPowerAverage6day = (rpvpSigma5day + todayVolume*todayRealPower) / (volumesSigma5day+todayVolume)
        except:
            realPowerAverage6day = 1

        realPowerAverage6day /= realPowerAverage5day # realPowerAverage5day is 1 for nonIpo tickers.
        
        realPowerLog = log10(realPowerAverage6day)
        
        # final calculation
        volumeLog_ExpRealPowerLog = volumeLog * exp(realPowerLog)

        if volumeLog >= 0:
            if realPowerLog >= 0:
                finalScore = int(max(min(40+volumeLog_ExpRealPowerLog*20/0.3, 80), 40))
            else:
                finalScore = 0
        else:
            if realPowerLog >= 0:
                finalScore = int(max(min(20-volumeLog_ExpRealPowerLog*160, 100), 20))
            else:
                finalScore = int(max(min(35-volumeLog_ExpRealPowerLog*125, 85), 35))


        if finalScore < limitScore:
            return (True, 0)
        else:
            return (False, finalScore)


@jit
def get_time_dif(t1,t2):
    t1m = t1 % 100
    t1H = (t1 - t1m)/100

    t2m = t2 % 100
    t2H = (t2 - t2m)/100

    difm = t2m - t1m
    difH = (t2H - t1H)*60
    return difH + difm