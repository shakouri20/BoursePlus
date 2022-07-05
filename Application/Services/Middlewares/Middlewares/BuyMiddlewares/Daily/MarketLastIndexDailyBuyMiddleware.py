from Application.Services.Middlewares.Middlewares.BuyMiddlewares.Daily.ValueDifDailyBuyMiddleware import valueDifDailyBuyMiddleware
from Application.Services.ReadData.ReadOnline.MarketWatchDataHandler import marketWatchDataHandler
from math import atan, floor, log10, pi
from Domain.Enums.OnlineColumns import onlineColumns
from Application.Services.ReadData.ReadOnline.OnlineDataHandler import onlineDataHandler
from Application.Services.Middlewares.MiddlewareFramework.Middleware import cast_list_to_numba, get_numba_types, middleware
from Application.Services.ReadData.ReadOffline.ReadOfflineServices import read_offline_services
from numba.types import float64, unicode_type, ListType, DictType, int64
from numba.typed import Dict, List
from Domain.ImportEnums import *

S3 = [100]
S15 = [20]
S = S3

class marketLastIndexDailyBuyMiddleware(middleware):

    def __init__(self, dataHandler, marketWatchHandler, mainTickersList: list, kargs):
        super(marketLastIndexDailyBuyMiddleware, self).__init__(dataHandler, marketWatchHandler, mainTickersList, kargs)

    def create_history_data(self, idList: list, dataHandler: onlineDataHandler, marketWatchHandler: marketWatchDataHandler) -> dict:
        if len(idList)==0:
            return None
            
        # Getting  >> Float64 <<
        (floatInnerDict, FloatDataDict) = get_numba_types('Float', False)
        floatInnerDict.clear()
        FloatDataDict.clear()

        # currentTime = dataHandler.time(num= 1)

        for id in idList:
            floatInnerDict.update({'MaxIndex' : -100})
            floatInnerDict.update({'TradeFlag' : 0})
            # Assembling
            FloatDataDict.update({id: floatInnerDict.copy()})
        return FloatDataDict

    def get_online_data(self, tickersList: list, dataHandler: onlineDataHandler, marketWatchHandler:marketWatchDataHandler):
        # Getting  >> Float64 <<
        (floatInnerDict, FloatDataDict) = get_numba_types('Float', True)
        floatInnerDict.clear()
        FloatDataDict.clear()

        marketLastIndex = marketWatchHandler.lastPricePRCAverge(decNum= S[0], num= 2)

        if len(marketLastIndex.keys()) == 0:
            return (None,None)

        marketLastIndex = marketLastIndex[marketGroupType.TotalMarket.value]
        if len(marketLastIndex) == 2:
            marketLastIndexDif = int(marketLastIndex[1]-marketLastIndex[0])
        else:
            marketLastIndexDif = 0

        realPowerLog = marketWatchHandler.realPowerLog(num= 1)[marketGroupType.TotalMarket.value][0]

        time = marketWatchHandler.time(decNum= S[0], num= 2)
        time = time[marketGroupType.TotalMarket.value]
        if len(time) == 2:
            timeDif = int((time[1]-time[0]).total_seconds())
        else:
            timeDif = 0

        lastPrice = dataHandler.lastPrice(num= 1, IDList= tickersList)

        # Assembling
        for Id in lastPrice:
            floatInnerDict.update({'TimeDif': timeDif})
            floatInnerDict.update({'MarketLastIndexDif': marketLastIndexDif})
            floatInnerDict.update({'MarketLastIndex': marketLastIndex[-1]})
            floatInnerDict.update({'RealPowerLog': realPowerLog})
            FloatDataDict.update({Id: floatInnerDict.copy()})

        return (FloatDataDict, None)
        

    @staticmethod
    def single_ticker_calculation(tickerFloatOnlineData: dict, tickerListOnlineData:dict, tickerOfflineData: dict, tickerHistoryData:dict, tickerId:int):
        
        tickerHistoryData['MaxIndex'] = max(tickerHistoryData['MaxIndex'], tickerFloatOnlineData['MarketLastIndex'])
        
        indexFall = tickerHistoryData['MaxIndex']-tickerFloatOnlineData['MarketLastIndex']

        if indexFall < 15:

            if tickerFloatOnlineData['TimeDif'] == 0:

                if tickerFloatOnlineData['RealPowerLog'] >= 1:
                    return (False, 90)

            else:

                slope = tickerFloatOnlineData['MarketLastIndexDif']/(tickerFloatOnlineData['TimeDif']/60)
                if slope >= 0.2:
                    tickerHistoryData['TradeFlag'] = 1
                if slope < 0.1:
                    tickerHistoryData['TradeFlag'] = 0
                if tickerHistoryData['TradeFlag'] == 1:
                    return (False, 80)


        return (True, 20)





