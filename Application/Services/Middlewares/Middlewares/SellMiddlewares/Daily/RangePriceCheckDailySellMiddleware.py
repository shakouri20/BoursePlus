from Application.Services.ReadData.ReadOnline.MarketWatchDataHandler import marketWatchDataHandler
from time import strftime
from Application.Services.ReadData.ReadOnline.OnlineDataHandler import onlineDataHandler
from Application.Services.Middlewares.MiddlewareFramework.Middleware import cast_list_to_numba, get_numba_types, middleware
from Application.Services.ReadData.ReadOffline.ReadOfflineServices import read_offline_services
from Domain.Enums.OnlineColumns import onlineColumns
from numba.types import float32, unicode_type, ListType, float64, DictType, int64
from numba.typed import Dict, List
from datetime import datetime
from math import log10


class rangePriceCheckDailySellMiddleware(middleware):

    def __init__(self, dataHandler, marketWatchHandler, mainTickersList: list, kargs):
        super(rangePriceCheckDailySellMiddleware, self).__init__(dataHandler, marketWatchHandler, mainTickersList, kargs)


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
            floatInnerDict.update({'BuyPrice' : 0})
            # Assembling
            FloatDataDict.update({id: floatInnerDict.copy()})
        return FloatDataDict

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

        S15 = [10]
        S3 = [60]
        S = S15

        price = dataHandler.lastPricePRC(num= S[0])
        currentTime = dataHandler.time(num= 1)

        for Id in tickersList:
            if Id in price and len(price[Id]) > 5:
                # List
                core_list = cast_list_to_numba(core_list, price[Id])
                listInnerDict.update({'LastPrices': core_list.copy()})
                # Assembling
                listDataDict.update({Id: listInnerDict.copy()})

                # Float
                floatInnerDict.update({'Time' : int(currentTime[Id][-1].strftime('%H%M'))})
                
                    # Assembling
                FloatDataDict.update({Id: floatInnerDict.copy()})

        return (FloatDataDict, listDataDict)


    @staticmethod
    def single_ticker_calculation(tickerFloatOnlineData: dict, tickerListOnlineData:dict, tickerOfflineData: dict, tickerHistoryData:dict, tickerId:int):
        # Check whether ticker history is None or not
        if tickerHistoryData is None:
            print('history is None!!')
            return (True, 0)

        # Check whether buy time and buy price is set in ticker history
        if tickerHistoryData['BuyTime'] == 0:
            tickerHistoryData['BuyPrice'] = tickerListOnlineData['LastPrices'][-1]
            tickerHistoryData['BuyTime'] = tickerFloatOnlineData['Time']
        
        # if tickerHistoryData is None:
        #     print('Ticker History data is none!!!')
        #     return (False, 50)
        currentTime = tickerFloatOnlineData['Time']
        price = tickerListOnlineData['LastPrices']

        maxP = max(price)
        minP = min(price)
        firstPrice = price[0]

        buyTime = tickerHistoryData['BuyTime']
        buyPrice = tickerHistoryData['BuyPrice']

        timeDif = currentTime - buyTime
        timeDif = timeDif if timeDif >= 0 else timeDif + 60

        if timeDif < 4 and (firstPrice - buyPrice) < 0.5:
            return (False, 50)

        if maxP == minP:
            return (False, 100)

        score = 50 - 42 * log10((maxP-minP)/1.5)
        
        if score > 100:
            score = 100
        if score < 0:
            score = 0

        return (False, score)