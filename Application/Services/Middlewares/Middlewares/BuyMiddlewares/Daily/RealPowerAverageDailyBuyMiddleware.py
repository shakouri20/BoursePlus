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

class realPowerAverageDailyBuyMiddleware(middleware):

    def __init__(self, dataHandler, marketWatchHandler, mainTickersList: list, kargs):
        super(realPowerAverageDailyBuyMiddleware, self).__init__(dataHandler, marketWatchHandler, mainTickersList, kargs)

    def read_offline_data(self, mainTickersList: list) -> dict:
        (inner_dict, dataDict) = get_numba_types('Float', False)
         
        data5day = orepo().read_last_N_offlineData('RealPower', 'Value', 'TodayPrice', Num= 5, IDList= mainTickersList)
        Ids = ticker_repo().read_list_of_tickers(IPO = 1)['ID'] # IPO Ids

        for Id in data5day:

            volumes = [int(data5day[Id]['Value'][i]/data5day[Id]['TodayPrice'][i]) for i in range(len(data5day[Id]['Value']))]
            realPowers = data5day[Id]['RealPower']

            rpvpSigma = 0

            realPowerAvg = 1
            if Id in Ids:
                realPowerAvg = sum(realPowers)/len(realPowers)

            for i in range(len(realPowers)):
                rpvpSigma += volumes[i]*realPowers[i]

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
        realPower = dataHandler.realPower(num= 1)


        for Id in tickersList:
            if Id in volume:

                floatInnerDict.update({'Volume' : volume[Id][-1]})
                floatInnerDict.update({'RealPower' : realPower[Id][-1]})

                # Assembling
                FloatDataDict.update({Id: floatInnerDict.copy()})

        return (FloatDataDict, None)



    @staticmethod
    def single_ticker_calculation(tickerFloatOnlineData: dict, tickerListOnlineData:dict, tickerOfflineData: dict, tickerHistoryData:dict, tickerId:int):

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
        
        score = max(min(100, int(71*log10(realPowerAverage6day)+50)), 0)
        
        return(False, score)
