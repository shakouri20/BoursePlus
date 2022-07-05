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

S15 = [4,4,4,10]
S3 = [20,20,20,50]
S = S15

class realPowerDifDailyBuyMiddleware(middleware):

    def __init__(self, dataHandler, marketWatchHandler, mainTickersList: list, kargs):
        super(realPowerDifDailyBuyMiddleware, self).__init__(dataHandler, marketWatchHandler, mainTickersList, kargs)

    def read_offline_data(self, mainTickersList: list) -> dict:
        (inner_dict, dataDict) = get_numba_types('Float', False)

        Ids = ticker_repo().read_list_of_tickers(IPO = 1)['ID']
        realPowers = orepo().read_last_N_offlineData('RealPower', Num= 3, IDList= Ids)

        for Id in mainTickersList:
            realPowerAvg = 1
            if Id in realPowers:
                realPowerAvg = sum(realPowers[Id]['RealPower'])/len(realPowers[Id]['RealPower'])
            inner_dict.update({'RealPowerAvg' : realPowerAvg})
            dataDict[Id] = inner_dict.copy()
        return dataDict

    def get_online_data(self, tickersList: list, dataHandler: onlineDataHandler, marketWatchHandler: marketWatchDataHandler):
        # Getting  >> List << 
        # (core_list, listInnerDict, listDataDict) = get_numba_types('List' , True)
        # core_list.clear()
        # listInnerDict.clear()
        # listDataDict.clear()

        

        # row1 = dataHandler.row1(decNum= S[3], num= 2)
        # SupplyVolume1 = row1['SupplyVolume1']
        # SupplyPrice1 = row1['SupplyPrice1']

        # Getting  >> Float64 <<
        (floatInnerDict, FloatDataDict) = get_numba_types('Float', True)
        floatInnerDict.clear()
        FloatDataDict.clear()

        # volumeDif = dataHandler.clientVolumeDif(decNum= S[0], num= 1)
        realPowerDif = dataHandler.realPowerDif(decNum= S[1], num= 1)
        # perCapitaBuyDif = dataHandler.perCapitaBuyDif(decNum= S[2], num= 1)
        # perCapitaSell = dataHandler.perCapitaSell(num= 1)
        # lastPrice = dataHandler.lastPrice(num= 1)
        # lastPricePRC = dataHandler.lastPricePRC(num= 1)
        # minAllowedPrice = dataHandler.minAllowedPrice()
        # time = dataHandler.time(num= 1)
        

        for Id in tickersList:
            if Id in realPowerDif:
            # if Id in volumeDif:
                # # List
                # core_list = cast_list_to_numba(core_list, SupplyVolume1[Id])
                # listInnerDict.update({'SupplyVolume': core_list.copy()})

                # core_list = cast_list_to_numba(core_list, SupplyPrice1[Id])
                # listInnerDict.update({'SupplyPrice': core_list.copy()})
                # # Assembling
                # listDataDict.update({Id: listInnerDict.copy()})

                # # Float
                # floatInnerDict.update({'VolumeDif' : volumeDif[Id][-1]})
                # floatInnerDict.update({'MinAllowedPrice': minAllowedPrice[Id]})
                # floatInnerDict.update({'LastPricePRC': lastPricePRC[Id][0]})
                # floatInnerDict.update({'LastPrice': lastPrice[Id][0]})
                # floatInnerDict.update({'PerCapitaBuyDif': perCapitaBuyDif[Id][-1]})
                floatInnerDict.update({'RealPowerDif': realPowerDif[Id][-1]})
                # floatInnerDict.update({'PerCapitaSell' : perCapitaSell[Id][0]})
                # floatInnerDict.update({'Time': int(time[Id][0].strftime('%H%M'))})
                
                # Assembling
                FloatDataDict.update({Id: floatInnerDict.copy()})

        # Returning as tuple
        # return (FloatDataDict, listDataDict)
        if len(FloatDataDict.keys())==0:
            return (None, None)
            
        return (FloatDataDict, None)

    @staticmethod
    def single_ticker_calculation(tickerFloatOnlineData: dict, tickerListOnlineData:dict, tickerOfflineData: dict, tickerHistoryData:dict, tickerId:int):
       
        limitScore = 50

        realPowerDif = tickerFloatOnlineData['RealPowerDif']/tickerOfflineData['RealPowerAvg']

        logRealPowerDif = log10(realPowerDif)
        score = int(max(min(50 * logRealPowerDif + 25, 100), 0))
        
        if score < limitScore:
            return (True, 0)
        else:
            return (False, score)