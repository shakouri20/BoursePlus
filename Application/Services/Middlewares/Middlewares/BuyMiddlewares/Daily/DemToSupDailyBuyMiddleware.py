from Infrastructure.Repository.TickerRepository import ticker_repo
from Application.Services.ReadData.ReadOnline.MarketWatchDataHandler import marketWatchDataHandler
from Application.Services.ReadData.ReadOffline.ReadOfflineServices import read_offline_services as rfs
from Infrastructure.Repository.OfflineDataRepository import offlineData_repo as orepo

from math import atan, floor, log10, pi
from Domain.Enums.OnlineColumns import onlineColumns
from Application.Services.ReadData.ReadOnline.OnlineDataHandler import onlineDataHandler
from Application.Services.Middlewares.MiddlewareFramework.Middleware import cast_list_to_numba, get_numba_types, middleware
from Application.Services.ReadData.ReadOffline.ReadOfflineServices import read_offline_services
from numba.types import float64, unicode_type, ListType, DictType, int64
from numba.typed import Dict, List


class demToSupDailyBuyMiddleware(middleware):

    def __init__(self, dataHandler, marketWatchHandler, mainTickersList: list, kargs):
        super(demToSupDailyBuyMiddleware, self).__init__(dataHandler, marketWatchHandler, mainTickersList, kargs)

    def get_online_data(self, tickersList: list, dataHandler: onlineDataHandler, marketWatchHandler: marketWatchDataHandler):
        # Getting  >> Float64 <<
        (floatInnerDict, FloatDataDict) = get_numba_types('Float', True)
        floatInnerDict.clear()
        FloatDataDict.clear()

        demToSup = dataHandler.demandToSupplyPower(num= 1)

        for Id in tickersList:
            if Id in demToSup:
                floatInnerDict.update({'DemToSup': demToSup[Id][-1]})
                
                # Assembling
                FloatDataDict.update({Id: floatInnerDict.copy()})

        # Returning as tuple
        if len(FloatDataDict.keys())==0:
            return (None, None)
            
        return (FloatDataDict, None)

    @staticmethod
    def single_ticker_calculation(tickerFloatOnlineData: dict, tickerListOnlineData:dict, tickerOfflineData: dict, tickerHistoryData:dict, tickerId:int):
       
        limitScore = 25

        logDemToSup = tickerFloatOnlineData['DemToSup']

        score = int(max(min(50 * logDemToSup + 25, 100), 0))
        
        if score < limitScore:
            return (True, 0)
        else:
            return (False, score)