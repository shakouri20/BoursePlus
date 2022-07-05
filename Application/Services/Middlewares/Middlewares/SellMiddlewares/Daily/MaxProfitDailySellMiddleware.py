from numba.core.decorators import jit
from Application.Services.ReadData.ReadOnline.MarketWatchDataHandler import marketWatchDataHandler
from time import strftime
from Application.Services.ReadData.ReadOnline.OnlineDataHandler import onlineDataHandler
from Application.Services.Middlewares.MiddlewareFramework.Middleware import cast_list_to_numba, get_numba_types, middleware
from Application.Services.ReadData.ReadOffline.ReadOfflineServices import read_offline_services as rfs
from Application.Services.ReadData.ReadOffline.ReadOfflineServices import read_offline_services
from Domain.Enums.OnlineColumns import onlineColumns
from numba.types import float32, unicode_type, ListType, float64, DictType, int64
from numba.typed import Dict, List
from datetime import datetime
from ta.volatility import *
import pandas as pd
from math import log10

class maxProfitDailySellMiddleware(middleware):

    def __init__(self, dataHandler, marketWatchHandler, mainTickersList: list, kargs):
        super(maxProfitDailySellMiddleware, self).__init__(dataHandler, marketWatchHandler, mainTickersList, kargs)

    def create_history_data(self, idList: list, dataHandler: onlineDataHandler, marketWatchHandler: marketWatchDataHandler) -> dict:
        if len(idList)==0:
            return None
            
        # Getting  >> Float64 <<
        (floatInnerDict, FloatDataDict) = get_numba_types('Float', False)
        floatInnerDict.clear()
        FloatDataDict.clear()

        # currentTime = dataHandler.time(num= 1)

        for id in idList:
            floatInnerDict.update({'MaxPrice' : 0})

            # Assembling
            FloatDataDict.update({id: floatInnerDict.copy()})
        return FloatDataDict

    def get_online_data(self, tickersList: list, dataHandler: onlineDataHandler, marketWatchHandler: marketWatchDataHandler):

        # Getting  >> Float64 <<
        (floatInnerDict, FloatDataDict) = get_numba_types('Float', True)
        floatInnerDict.clear()
        FloatDataDict.clear()

        lastPrice = dataHandler.lastPrice(num= 1)
        time = dataHandler.time(num= 1)
        minAllowedPrice = dataHandler.minAllowedPrice()

        for Id in tickersList:

            if Id in lastPrice:

                # Float
                floatInnerDict.update({'LastPrice' : lastPrice[Id][0]})
                floatInnerDict.update({'Time' : int(time[Id][0].strftime('%H%M'))})
                floatInnerDict.update({'MinAllowedPrice' : minAllowedPrice[Id]})

                # Assembling
                FloatDataDict.update({Id: floatInnerDict.copy()})

        return (FloatDataDict, None)

    @staticmethod
    def single_ticker_calculation(tickerFloatOnlineData: dict, tickerListOnlineData:dict, tickerOfflineData: dict, tickerHistoryData:dict, tickerId:int):
        # Check whether ticker history is None or not
        if tickerHistoryData is None:
            print('history is None!!')
            return (True, 0)

        lastPrice = tickerFloatOnlineData['LastPrice']
        minAllowedPrice = tickerFloatOnlineData['MinAllowedPrice']

        tickerHistoryData['MaxPrice'] = max(tickerHistoryData['MaxPrice'], lastPrice)

        if tickerFloatOnlineData['Time'] > 1225:
            maxProfit = (tickerHistoryData['MaxPrice']-minAllowedPrice)/minAllowedPrice*100-1.25
            score = int(max(min(8.3*maxProfit+25, 100), 0))
            return (False, score)
        else:
            return (False, 0)