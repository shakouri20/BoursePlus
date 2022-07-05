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

S15 = {'BBPriceListLength': 30, 'BBWindowSize': 20, 'PriceLength': 5, 'RPDDecNum': 10}
S3 = {'BBPriceListLength': 150, 'BBWindowSize': 100, 'PriceLength': 25, 'RPDDecNum': 50}
S = S15

# S15 = [30, 20, 5]  # Price list length,  bollinger window size
# S3 = [180, 120, 20]
# S = S15

class bollingerBandDailySellMiddleware(middleware):

    def __init__(self, dataHandler, marketWatchHandler, mainTickersList: list, kargs):
        super(bollingerBandDailySellMiddleware, self).__init__(dataHandler, marketWatchHandler, mainTickersList, kargs)


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
            floatInnerDict.update({'RiseTime' : 0})
            floatInnerDict.update({'wasAboveHBand' : 0})
            floatInnerDict.update({'RpdFlag' : 0})
            floatInnerDict.update({'StartSell' : 0})

            # Assembling
            FloatDataDict.update({id: floatInnerDict.copy()})
        return FloatDataDict

    def read_offline_data(self, mainTickersList: list) -> dict:
        (inner_dict, dataDict) = get_numba_types('Float', False)
         
        volumeAvg = rfs.average.get_averge_volume(mainTickersList, 30)

        for Id in volumeAvg:
            inner_dict.update({'MonthlyVolume' : volumeAvg[Id]})
            dataDict[Id] = inner_dict.copy()
        return dataDict

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

        prices = dataHandler.lastPrice(num= S['BBPriceListLength'])
        # prices = dataHandler.row1(num= S['BBPriceListLength'])[onlineColumns.DemandPrice1.value]
        realPowerDif = dataHandler.realPowerDif(decNum= S['RPDDecNum'], num= 1)
        currentTime = dataHandler.time(num= 1)
        minAllowedPrice = dataHandler.minAllowedPrice()
        row1 = dataHandler.row1(num= 1)

        for Id in tickersList:
            if Id in prices and len(prices[Id]) > 5:
                # List

                # Bollinger
                LastPrice = prices[Id]
                bb = BollingerBands(pd.Series(LastPrice), fillna= True, window= S['BBWindowSize'])
                bbh = bb.bollinger_hband().to_list()
                bbl = bb.bollinger_lband().to_list()
                # bbma = bb.bollinger_mavg().to_list()
                core_list = cast_list_to_numba(core_list, bbh)
                listInnerDict.update({'BBH': core_list.copy()})

                core_list = cast_list_to_numba(core_list, bbl)
                listInnerDict.update({'BBL': core_list.copy()})

                core_list = cast_list_to_numba(core_list, LastPrice[-S['PriceLength']:])
                listInnerDict.update({'LastPrices': core_list.copy()})
                
                # Assembling
                listDataDict.update({Id: listInnerDict.copy()})

                #################

                supplyPrice1 = row1[onlineColumns.SupplyPrice1.value][Id][-1]
                supplyVolume1 = row1[onlineColumns.SupplyVolume1.value][Id][-1]
                demandVolume1 = row1[onlineColumns.DemandVolume1.value][Id][-1]

                # Float
                floatInnerDict.update({'RPD' : realPowerDif[Id][-1]})
                floatInnerDict.update({'MinAllowedPrice' : minAllowedPrice[Id]})
                floatInnerDict.update({'Time' : int(currentTime[Id][-1].strftime('%H%M'))})
                floatInnerDict.update({onlineColumns.SupplyPrice1.value : supplyPrice1})
                floatInnerDict.update({onlineColumns.SupplyVolume1.value : supplyVolume1})
                floatInnerDict.update({onlineColumns.DemandVolume1.value : demandVolume1})

                # if int(currentTime[Id][-1].strftime('%H%M')) > 922 and Id == 14744445176220774:
                #     x= 1
                
                # Assembling
                FloatDataDict.update({Id: floatInnerDict.copy()})

        return (FloatDataDict, listDataDict)

    @staticmethod
    def single_ticker_calculation(tickerFloatOnlineData: dict, tickerListOnlineData:dict, tickerOfflineData: dict, tickerHistoryData:dict, tickerId:int):
        # Check whether ticker history is None or not
        if tickerHistoryData is None:
            print('history is None!!')
            return (True, 0)

        lastPrice = tickerListOnlineData['LastPrices'][-1]
        currentTime = tickerFloatOnlineData['Time']
        supplyPrice1 = tickerFloatOnlineData[onlineColumns.SupplyPrice1.value]
        supplyVolume1 = tickerFloatOnlineData[onlineColumns.SupplyVolume1.value]
        demandVolume1 = tickerFloatOnlineData[onlineColumns.DemandVolume1.value]

        if tickerHistoryData['BuyTime'] == 0:
            tickerHistoryData['BuyPrice'] = tickerListOnlineData['LastPrices'][-2]
            tickerHistoryData['BuyTime'] = tickerFloatOnlineData['Time']

        if tickerHistoryData['StartSell'] == 0:
            buyTimeDif = get_time_dif(tickerHistoryData['BuyTime'], currentTime)
            if buyTimeDif > 4 or demandVolume1 > 0:
                tickerHistoryData['StartSell'] = 1
                tickerHistoryData['RiseTime'] = tickerFloatOnlineData['Time']

        if tickerHistoryData['StartSell'] == 1:
        
            minAllowedPrice = tickerFloatOnlineData['MinAllowedPrice']

            if supplyPrice1 == minAllowedPrice and demandVolume1 == 0:
                sellQueueValue = supplyPrice1 * supplyVolume1 / 10**7
                thresholdValue = tickerOfflineData['MonthlyVolume'] * supplyPrice1 / 5 / 10**7
                if sellQueueValue > 200 and sellQueueValue > thresholdValue:
                    return (False, 100)

            sellQueuePriceDistance = (lastPrice-minAllowedPrice)/minAllowedPrice*100

            bbh = tickerListOnlineData['BBH']
            bbl = tickerListOnlineData['BBL']
            CW = (bbh[-1] - bbl[-1]) / bbl[-1] * 100

            if sellQueuePriceDistance <= 0.5 and CW < 0.2:
                tickerHistoryData['RiseTime'] = tickerFloatOnlineData['Time']

            prices = tickerListOnlineData['LastPrices']
            rpd = tickerFloatOnlineData['RPD']

            if tickerHistoryData['RpdFlag'] == 1 and rpd < 1:
                tickerHistoryData['RpdFlag'] = 0
                return (False, 73)
            
            riseTime = tickerHistoryData['RiseTime']
            buyPrice = tickerHistoryData['BuyPrice']

            riseTimeDif = get_time_dif(riseTime, currentTime)

            # Checking cloud width (Upper band - Lower band)
            if riseTimeDif >= 4 and CW < 0.4:
                return (False, 95)
            
            if riseTimeDif < 4:
                profit = (prices[-1] - buyPrice) / buyPrice * 100 - 1.25
                if profit >= 1:
                    return (False, 80)
            
            # # Checking L band
            # for i in range(1, len(prices)+1):
            #     if prices[-i] > bbl[-i]:
            #         break
            # else:
            #     return (False, 90)

            priceBBHDif1 = (prices[-1] - bbh[-1]) / prices[-1] * 100

            if priceBBHDif1 < 0: # prices has entered
                # Check whether price was above cloud
                if tickerHistoryData['wasAboveHBand'] and priceBBHDif1 < -0.5:
                    tickerHistoryData['wasAboveHBand'] = 0 # Setting to false
                    # Price has pierced the hband => checking tiemDif to decide whether to sell
                    if riseTimeDif > 4:
                        
                        if rpd > 2:
                            tickerHistoryData['RpdFlag'] = 1
                        else:
                            return (False, 85)

            else:  # Price is above lower border of h band => checking distance from h band
                tickerHistoryData['wasAboveHBand'] = 1 # Setting to true
                # sell if price is above bbh by a certain amount
                if priceBBHDif1 >= 1:
                    return (False, 75)

        return (False, 69)

@jit
def get_time_dif(t1,t2):
    t1m = t1 % 100
    t1H = (t1 - t1m)/100

    t2m = t2 % 100
    t2H = (t2 - t2m)/100

    difm = t2m - t1m
    difH = (t2H - t1H)*60
    return difH + difm