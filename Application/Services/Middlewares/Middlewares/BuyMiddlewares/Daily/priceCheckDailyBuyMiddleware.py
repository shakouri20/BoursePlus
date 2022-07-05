from Application.Services.Middlewares.MiddlewareFramework.Middleware import *

S3 = [20]
S15 = [4]
S = S3

class priceCheckDailyBuyMiddleware(middleware):

    def __init__(self, dataHandler, marketWatchHandler, mainTickersList: list, kargs):
        super(priceCheckDailyBuyMiddleware, self).__init__(dataHandler, marketWatchHandler, mainTickersList, kargs)


    def get_online_data(self, tickersList: list, dataHandler: onlineDataHandler, marketWatchHandler: marketWatchDataHandler):
        # Getting  >> Float64 <<
        (floatInnerDict, FloatDataDict) = get_numba_types('Float', True)
        floatInnerDict.clear()
        FloatDataDict.clear()
        # Getting  >> List << 
        (core_list, listInnerDict, listDataDict) = get_numba_types('List' , True)
        core_list.clear()
        listInnerDict.clear()
        listDataDict.clear()

        lastPricePRC = dataHandler.lastPricePRC(num= 1, IDList= tickersList)
        minPrices = dataHandler.minAllowedPrice(IDList= tickersList)
        prices = dataHandler.lastPrice(decNum= S[0], num= 30, IDList= tickersList)
        maxPrices = dataHandler.maxPrice(num= 1, IDList= tickersList)
        time = dataHandler.time(num= 1, IDList= tickersList)


        for Id in prices:
            # List
            core_list = cast_list_to_numba(core_list, prices[Id])
            listInnerDict.update({'LastPrice': core_list.copy()})

            # Assembling
            listDataDict.update({Id: listInnerDict.copy()})
            
            # float
            floatInnerDict.update({'LastPricePRC': lastPricePRC[Id][-1]})
            floatInnerDict.update({'MinAllowedPrice': minPrices[Id]})
            floatInnerDict.update({'MaxPrice': maxPrices[Id][-1]})
            floatInnerDict.update({'Time':  int(time[Id][-1].strftime('%H%M'))})
            
            # Assembling
            FloatDataDict.update({Id: floatInnerDict.copy()})

        return (FloatDataDict, listDataDict)



    @staticmethod
    def single_ticker_calculation(tickerFloatOnlineData: dict, tickerListOnlineData:dict, tickerOfflineData: dict, tickerHistoryData:dict, tickerId:int):

        prices = tickerListOnlineData['LastPrice']
        minAllowedPrice = tickerFloatOnlineData['MinAllowedPrice']

        if prices[-1] < 1.01 * minAllowedPrice:
            
            pricePRC = tickerFloatOnlineData['LastPricePRC']
            maxPrice = tickerFloatOnlineData['MaxPrice']
            lastHourMaxPrice = max(prices) if tickerFloatOnlineData['Time'] > 930 else maxPrice

            lastHourPriceFall = (minAllowedPrice - lastHourMaxPrice) / lastHourMaxPrice * 100
            totalPriceFall = (minAllowedPrice - maxPrice) / maxPrice * 100

            if abs(lastHourPriceFall) <= 4 and abs(totalPriceFall) <= 7:
        
                if pricePRC <= -4 and pricePRC >= -5:
                    return (False, 100)
                elif pricePRC < -2 and pricePRC>= -3:
                    return (False, 50)

        return (True, 10)