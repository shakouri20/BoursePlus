from Application.Services.ReadData.ReadOnline.MarketWatchDataHandler import marketWatchDataHandler
from time import strftime
from Application.Services.ReadData.ReadOnline.OnlineDataHandler import onlineDataHandler
from Application.Services.Middlewares.MiddlewareFramework.Middleware import cast_list_to_numba, get_numba_types, middleware
from Application.Services.ReadData.ReadOffline.ReadOfflineServices import read_offline_services
from Domain.Enums.OnlineColumns import onlineColumns
from numba.types import float32, unicode_type, ListType, float64, DictType, int64, boolean
from numba.typed import Dict, List


class constantChangeDailySellMiddleware(middleware):

    def __init__(self, dataHandler, marketWatchHandler, mainTickersList: list, kargs):
        super(constantChangeDailySellMiddleware, self).__init__(dataHandler, marketWatchHandler, mainTickersList, kargs)

    def create_history_data(self, idList: list) -> dict:
        inner_dict_type = DictType(unicode_type, int64)
        inner_dict = Dict.empty(unicode_type, int64)
    
        dataDict = Dict.empty(
            key_type = int64,
            value_type= inner_dict_type,)

        inner_dict.update({'StartSell' : 0})
        inner_dict.update({'MaxSellQueueValue' : 0})
        for id in idList:
            dataDict.update({id: inner_dict.copy()})
        
        return dataDict

    def get_online_data(self, tickersList: list, dataHandler: onlineDataHandler, marketWatchHandler: marketWatchDataHandler):
        # Getting  >> List << 
        (core_list, listInnerDict, listDataDict) = get_numba_types('List' , True)
        core_list.clear()
        listInnerDict.clear()
        listDataDict.clear()

        S15 = [4,4,4,10]
        S3 = [28,28,28,70]
        S = S3

        row1 = dataHandler.row1(decNum= S[3], num= 2)
        SupplyVolume = row1['SupplyVolume1']

        # Getting  >> Float64 <<
        (floatInnerDict, FloatDataDict) = get_numba_types('Float', True)
        floatInnerDict.clear()
        FloatDataDict.clear()

        minAllowedPrice = dataHandler.minAllowedPrice()
        demandValue = dataHandler.demandValue(num= 1)
        supplyValue = dataHandler.supplyValue(num= 1)
        time = dataHandler.time(num= 1)

        for Id in SupplyVolume:
                # List
                core_list = cast_list_to_numba(core_list, SupplyVolume[Id])
                listInnerDict.update({'SupplyVolume': core_list.copy()})
                # Assembling
                listDataDict.update({Id: listInnerDict.copy()})

                # Float
                floatInnerDict.update({'MinAllowedPrice': minAllowedPrice[Id]})
                floatInnerDict.update({'DemandValue' : demandValue[Id][0]})
                floatInnerDict.update({'SupplyValue' : supplyValue[Id][0]})
                floatInnerDict.update({'Time': int(time[Id][0].strftime('%H%M'))})
                
                # Assembling
                FloatDataDict.update({Id: floatInnerDict.copy()})

        # Returning as tuple
        return (FloatDataDict, listDataDict)


    @staticmethod
    def single_ticker_calculation(tickerFloatOnlineData: dict, tickerListOnlineData:dict, tickerOfflineData: dict, tickerHistoryData:dict, tickerId:int):
        time = tickerFloatOnlineData['Time']
        if time > 1220:
            return (False, 100)

        # Lists
        SupplyVolume = tickerListOnlineData['SupplyVolume']

        # Floats
        demandValue = tickerFloatOnlineData['DemandValue']
        supplyValue = tickerFloatOnlineData['SupplyValue']
        minAllowedPrice = tickerFloatOnlineData['MinAllowedPrice']

        if tickerHistoryData['MaxSellQueueValue'] == 0:
            tickerHistoryData['MaxSellQueueValue'] = int(max(SupplyVolume) * minAllowedPrice / 10000000)


        if tickerHistoryData['StartSell']:
            sellQueueValue = tickerHistoryData['MaxSellQueueValue']
            if supplyValue > 0.08 * sellQueueValue and (demandValue == 0 or supplyValue / demandValue > 1.6):
                return (False, 100)

        if not tickerHistoryData['StartSell'] and demandValue > 1.5 *  supplyValue:
            tickerHistoryData['StartSell'] = 1

        return (True , 0)

