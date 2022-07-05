from math import log10
from Application.Services.Middlewares.MiddlewareFramework.Middleware import middleware
from Domain.Models.MiddlewareOffline import middlewareOffline
from Domain.Models.TickerOfflineData import tickerOfflineData
from Domain.Enums.MiddlewareOrder import middlewareOrder


class d_sellMiddlewares:

    class rsiSellMiddleware(middlewareOffline):

        def process(data: tickerOfflineData, i) -> tuple:
            if data.rsi[i] > 50:
                return (middlewareOrder.Continue, 100, data.closePrice[i])
            else:
                return (middlewareOrder.Continue, 0, data.closePrice[i])

    class realPowerSellMiddleware(middlewareOffline):

        def __init__(self, IDs: list) -> None:
            super().__init__(IDs)

        def process(self, data: tickerOfflineData, i) -> tuple:
            if data.realPower[i] < 0.5:
                return (middlewareOrder.Sell, 100, data.closePrice[i])
            return (middlewareOrder.Continue, 0, data.closePrice[i])

    class stochRsiSellMiddleware(middlewareOffline):

        def process(data: tickerOfflineData, i) -> tuple:
            score = data.stochRsi[i]*100
            return (middlewareOrder.Continue, score, data.closePrice[i])

    class bollingerBandSellMiddleware(middlewareOffline):

        def __init__(self, IDs: list) -> None:
            super().__init__(IDs)

            self.maxPrice = 0

        def process(self, data: tickerOfflineData, i) -> tuple:

            self.maxPrice = max(data.closePrice[max(0, i-4): i+1])

            priceDif = (data.closePrice[i]-self.maxPrice)/self.maxPrice*100
            if priceDif < -15:
                return (middlewareOrder.Sell, 100, data.closePrice[i])

            if data.rpvp[i] < -0.2:
                for j in range(max(0, i-3), i+1):
                    if data.pbbh[j] < 4:
                        return (middlewareOrder.Sell, 100, data.closePrice[i])

            if data.rpvp[i] < -0.3:
                return (middlewareOrder.Sell, 100, data.closePrice[i])

            if data.realPower[i] < 0.5:
                return (middlewareOrder.Sell, 100, data.closePrice[i])

            candleHeight = data.closePricePRC[i]-data.openPricePRC[i]

            if candleHeight < -5:
                return (middlewareOrder.Sell, 100, data.closePrice[i])

            return (middlewareOrder.Continue, 0, data.closePrice[i])

    class priceMaSellMiddleware(middlewareOffline):

        def __init__(self, IDs: list) -> None:
            super().__init__(IDs)

        def process(self, data: tickerOfflineData, i) -> tuple:

            if data.closePrice[i] < data.closePriceMa[i]:
                return (middlewareOrder.Sell, 100, data.closePrice[i])       
            
            return (middlewareOrder.Continue, 0, data.closePrice[i])

    class heikinAshi(middlewareOffline):

        def __init__(self, IDs: list) -> None:
            super().__init__(IDs)

        def process(self, ID, data: tickerOfflineData, i) -> tuple:
            
            if i == 49:
                x = 1
            historyNumber = 5
            openPrices = data.priceData.openPrice[max(0, i-historyNumber):i+1]
            closePrices = data.priceData.closePrice[max(0, i-historyNumber):i+1]
            highPrices = data.priceData.highPrice[max(0, i-historyNumber):i+1]
            lowPrices = data.priceData.lowPrice[max(0, i-historyNumber):i+1]
            (haOpen, haClose, haHigh, haLow) = calc_heikinAshi(openPrices, closePrices, highPrices, lowPrices)

            candleBodyHeight = (haClose[-1]-haOpen[-1])/haOpen[-1]*100
            if candleBodyHeight < -0.5: #  and haHigh[-1] == haOpen[-1]
                return (middlewareOrder.Sell, 100, data.priceData.closePrice[i]) 

            return (middlewareOrder.Continue, 0, data.priceData.closePrice[i])


def calc_heikinAshi(open, close, high, low):
    haOpen = []
    haClose = []
    haHigh = []
    haLow = []
    
    for i in range(len(open)):
        if i == 0:
            haOpen.append((open[i]+close[i])/2)
        else:
            haOpen.append((haOpen[i-1]+haClose[i-1])/2)
        haClose.append((open[i]+close[i]+high[i]+low[i])/4)
        haHigh.append(max(haOpen[i], haClose[i], high[i]))
        haLow.append(min(haOpen[i], haClose[i], low[i]))

    return (haOpen, haClose, haHigh, haLow)