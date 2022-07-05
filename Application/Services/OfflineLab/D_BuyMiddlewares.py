from math import log10
from Domain.Models.MiddlewareOffline import middlewareOffline
from Domain.Models.TickerOfflineData import tickerOfflineData
from Domain.Enums.MiddlewareOrder import middlewareOrder


class d_buyMiddlewares:

    class rsiBuyMiddleware(middlewareOffline):

        def __init__(self, IDs: list) -> None:
            super().__init__(IDs)

        def process(self, data: tickerOfflineData, i) -> tuple:
            if data.rsi[i] < 30:
                return (middlewareOrder.Continue, 75, data.closePrice[i])
            else:
                return (middlewareOrder.Continue, 0, data.closePrice[i])

    class realPowerBuyMiddleware(middlewareOffline):
        
        def __init__(self, IDs: list) -> None:
            super().__init__(IDs)

        def process(self, data: tickerOfflineData, i) -> tuple:
            if data.realPower[i] > 2:
                return (middlewareOrder.Buy, 100, data.closePrice[i])
            return (middlewareOrder.Continue, 0, data.closePrice[i])

    class stochRsiBuyMiddleware(middlewareOffline):

        def __init__(self, IDs: list) -> None:
            super().__init__(IDs)

        def process(self, data: tickerOfflineData, i) -> tuple:
            score = (1-data.stochRsi[i])*100
            return (middlewareOrder.Continue, score, data.closePrice[i])

    class bollingerBandBuyMiddleware(middlewareOffline):

        def __init__(self, IDs: list) -> None:
            super().__init__(IDs)


        def process(self, data: tickerOfflineData, i) -> tuple:

            # if data.pbbd[i] < 80:

            if data.realPower[i] > 2:
                return (middlewareOrder.Buy, 100, data.closePrice[i])

            if data.rpvp[i] > 0.4:
                return (middlewareOrder.Buy, 100, data.closePrice[i])

            if data.rpvp[i] > 0.15:

                if data.pbbl[i] < 4:
                    return (middlewareOrder.Buy, 100, data.closePrice[i])

                if data.pbbl[i] >= data.pbblma[i]:
                    for j in range(max(0, i-3), i+1):
                        if data.pbbl[j] < data.pbblma[j]:
                            return (middlewareOrder.Buy, 100, data.closePrice[i])

            if data.cw[i] < 15 and data.rpvp[i] > 0:
                for i in range(max(0, i-4), i+1):
                    if data.rpvp[i] < -0.2:
                        break
                else:
                    return (middlewareOrder.Buy, 100, data.closePrice[i])

    
            return (middlewareOrder.Continue, 0, data.closePrice[i])
            
    class priceMaBuyMiddleware(middlewareOffline):

        def __init__(self, IDs: list) -> None:
            super().__init__(IDs)

        def process(self, data: tickerOfflineData, i) -> tuple:

            if data.closePrice[i] > data.closePriceMa[i]:
                return (middlewareOrder.Buy, 100, data.closePrice[i])

            return (middlewareOrder.Continue, 0, data.closePrice[i])


    class heikinAshi(middlewareOffline):

        def __init__(self, IDs: list) -> None:
            super().__init__(IDs)

        def process(self, ID, data: tickerOfflineData, i) -> tuple:
            
            historyNumber = 5
            openPrices = data.priceData.openPrice[max(0, i-historyNumber):i+1]
            closePrices = data.priceData.closePrice[max(0, i-historyNumber):i+1]
            highPrices = data.priceData.highPrice[max(0, i-historyNumber):i+1]
            lowPrices = data.priceData.lowPrice[max(0, i-historyNumber):i+1]
            (haOpen, haClose, haHigh, haLow) = self.calc_heikinAshi(openPrices, closePrices, highPrices, lowPrices)
            candleBodyHeight = (haClose[-1]-haOpen[-1])/haOpen[-1]*100
            if candleBodyHeight > 0.5: #  and haOpen[-1] == haLow[-1]
                return (middlewareOrder.Buy, 100, data.priceData.closePrice[i]) 

            return (middlewareOrder.Continue, 0, data.priceData.closePrice[i])
