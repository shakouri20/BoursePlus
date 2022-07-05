from time import strftime
from Application.Services.ReadData.ReadOnline.OnlineDataHandler import onlineDataHandler
from Application.Services.Middlewares.MiddlewareFramework.Middleware import middleware
from Application.Services.ReadData.ReadOffline.ReadOfflineServices import read_offline_services
from Domain.Enums.OnlineColumns import onlineColumns
from numba.types import float32, unicode_type, ListType, float64, DictType, int64
from numba.typed import Dict, List


class sellQueueDailySellMiddleware(middleware):

    def __init__(self, dataHandler, mainTickersList: list, kargs):
        super(sellQueueDailySellMiddleware, self).__init__(dataHandler, mainTickersList, kargs)

    def read_offline_data(self, mainTickersList: list) -> dict:
        inner_dict_type = DictType(unicode_type, float64)
        inner_dict = Dict.empty(unicode_type, float64)
        
        dataDict = Dict.empty(
         key_type = int64,
         value_type= inner_dict_type,)
         
        volumeAvg = read_offline_services.average.get_averge_volume(mainTickersList, 30)

        for Id in volumeAvg:
            inner_dict['volumeAvg'] = volumeAvg[Id]
            dataDict[Id] = inner_dict.copy()
        return dataDict

    def get_online_data(self, tickersList: list, dataHandler: onlineDataHandler) -> dict:
        core_list_type = ListType(float64)
        core_list = List.empty_list(float64)

        inner_dict_type = DictType(unicode_type, core_list_type)
        inner_dict = Dict.empty(unicode_type, core_list_type)
        
        dataDict = Dict.empty(
         key_type = int64,
         value_type= inner_dict_type,)

        demToSupPower = dataHandler.demandToSupplyPower(num= 14)
        time = dataHandler.time(num= 1)

        for Id in demToSupPower:
            core_list = demToSupPower[Id]
            inner_dict['demToSupPower'] = core_list
            core_list = [int(time[Id][0].strftime('%H%M'))]
            inner_dict['Time'] = core_list
            core_list = [Id]
            inner_dict['Id'] = core_list
            dataDict[Id] = inner_dict.copy()

        return dataDict

    @staticmethod
    def single_ticker_calculation(tickerOnlineData: dict, tickerOfflineData: dict):
        time = tickerOnlineData['Time']
        if time > 1226:
            return False, 100

        Id = tickerOnlineData['Id'][0]

        lastPrice = tickerOnlineData['LastPrice']
        minAllowedPrice = tickerOnlineData['MinAllowedPrice']

        priceChange = 100 * (lastPrice - minAllowedPrice) / minAllowedPrice
        if priceChange <= 2.5:
            return True , 0
        else:
            return False , 100

