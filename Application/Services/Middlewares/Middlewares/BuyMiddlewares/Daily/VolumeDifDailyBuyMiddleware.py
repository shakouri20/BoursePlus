from Application.Services.Middlewares.MiddlewareFramework.Middleware import *
from Infrastructure.Repository.OnlineDataRepository import onlineData_repo
from Infrastructure.Repository.OfflineDataRepository import offlineData_repo
from Application.Services.ReadData.ReadOffline.ReadOfflineServices import read_offline_services as rfs
from numba import jit
from numba.types import float32, unicode_type, ListType, float64, DictType, int64
from numba.typed import Dict, List
from math import log10
from datetime import datetime, timedelta
import time as t

S15 = [4]
S3 = [20]
S = S3

class volumeDifDailyBuyMiddleware(middleware):

    def __init__(self, dataHandler, marketWatchHandler, mainTickersList: list, kargs):
        super(volumeDifDailyBuyMiddleware, self).__init__(dataHandler, marketWatchHandler, mainTickersList, kargs)

    def read_offline_data(self, mainTickersList: list) -> dict:
        (inner_dict, dataDict) = get_numba_types('Float', False)
         
        volumeAvg = rfs.average.get_averge_volume(mainTickersList, 30)

        for Id in volumeAvg:
            if volumeAvg[Id] != 0:
                inner_dict.update({'VolumeAvg' : volumeAvg[Id]/3.5/3600})
                dataDict[Id] = inner_dict.copy()
        return dataDict

    def get_online_data(self, tickersList: list, dataHandler: onlineDataHandler, marketWatchHandler: marketWatchDataHandler):
        # Getting  >> Float64 <<
        (floatInnerDict, FloatDataDict) = get_numba_types('Float', True)
        floatInnerDict.clear()
        FloatDataDict.clear()

        volumes = dataHandler.volumeDif(decNum= S[0], num= 1, IDList= tickersList)
        time = dataHandler.time(decNum= S[0], num= 2, IDList= tickersList)

        for Id in volumes:
            # Float
            volumeDif = volumes[Id][-1]
            if len(time[Id]) == 2:
                timeDif = (time[Id][1] - time[Id][0]).seconds
            else:
                timeDif = 1
            if volumeDif >=0 and timeDif > 0.1:
                floatInnerDict.update({'VolumeDif' : volumeDif})
                floatInnerDict.update({'TimeDif': timeDif})

                # Assembling
                FloatDataDict.update({Id: floatInnerDict.copy()})

        return (FloatDataDict, None)


    @staticmethod
    def single_ticker_calculation(tickerFloatOnlineData: dict, tickerListOnlineData:dict, tickerOfflineData: dict, tickerHistoryData:dict, tickerId:int):

        limitScore = 40

        monthlyVolumeAvgInSecond = tickerOfflineData['VolumeAvg']
        timeDif = tickerFloatOnlineData['TimeDif']
        volumeDif = tickerFloatOnlineData['VolumeDif']

        normalVolume = volumeDif / (monthlyVolumeAvgInSecond * timeDif)
            
        logNormalVolume = log10(normalVolume)
        score = int(max(min(30 * logNormalVolume + 25, 100), 0))
        
        if score < limitScore:
            return (True, 0)
        else:
            return (False, score)