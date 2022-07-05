from math import log10
from Application.Utility.Indicators.IndicatorService import calculateBB, calculateRsi, calculateSma
from Domain.Models.MiddlewareOffline import middlewareOffline
from Domain.Models.TickerOfflineData import tickersGroupData, onlineData, tickerOfflineData
from Domain.Enums.MiddlewareOrder import middlewareOrder

transactionFee = 1.25

class m_sellMiddlewares:

    class test(middlewareOffline):

        def __init__(self, IDs: list) -> None:
            super().__init__(IDs)
            self.name = 'test'

        def process(self, ID, offData: tickerOfflineData, i, onData: onlineData, j, todaytickersGroupData: tickersGroupData) -> tuple:

            # if self.history[ID] == {}:
            #     self.history[ID]['BuyIndex'] = (i, j)
                
            # buyI = self.history[ID]['BuyIndex'][0]
            # buyJ = self.history[ID]['BuyIndex'][1]
            # if i == buyI and j > buyJ + 15 or j == len(onData.time[i])-1: 
            #     return (middlewareOrder.Sell, 100, onData.closePrice[i][j], 1)
            
            if offData.time[i] == '1400-09-03':
                return (middlewareOrder.Sell, 100, onData.closePrice[i][j], 1)

            return (middlewareOrder.Continue, 0, onData.closePrice[i][j], 1)
            
    class stopLoss(middlewareOffline):

        def __init__(self, IDs: list, stopLoss, newStopLossLimit= 0, newStopLoss= 0, sellByClosePrice= True) -> None:
            super().__init__(IDs)
            self.name = 'stopLoss'
            self.stopLoss = stopLoss
            self.newStopLossLimit = newStopLossLimit
            self.newStopLoss = newStopLoss
            self.sellByClosePrice = sellByClosePrice

        def process(self, ID, offData: tickerOfflineData, i, onData: onlineData, j, todaytickersGroupData: tickersGroupData) -> tuple:
            
            if self.history[ID] == {}:
                self.history[ID]['BuyPrice'] = offData.onlineData.closePriceAdj[i][j-1] if j != 0 else offData.onlineData.closePriceAdj[i-1][-1]
                self.history[ID]['SetNewStopLoss'] = False

            lastPrice = offData.onlineData.closePriceAdj[i][j]
            buyPrice = self.history[ID]['BuyPrice']

            loss = (lastPrice-buyPrice)/buyPrice*100-transactionFee
            highDif = (offData.onlineData.highPriceAdj[i][j]-buyPrice)/buyPrice*100

            if self.newStopLossLimit > 0 and highDif > self.newStopLossLimit:
                 self.history[ID]['SetNewStopLoss'] = True

            if loss < -self.stopLoss:

                sellPrice = int((1-(self.stopLoss-transactionFee)/100)*self.history[ID]['BuyPrice'])

                if self.sellByClosePrice:
                    return (middlewareOrder.Sell, 100, lastPrice, 1)
                elif offData.onlineData.openPriceAdj[i][j] < sellPrice:
                    return (middlewareOrder.Sell, 100, offData.onlineData.openPriceAdj[i][j], 1)
                else:
                    return (middlewareOrder.Sell, 100, sellPrice, 1)
                
            if self.history[ID]['SetNewStopLoss'] and loss < -self.newStopLoss:
                
                sellPrice = int((1-(self.newStopLoss-transactionFee)/100)*self.history[ID]['BuyPrice'])

                if self.sellByClosePrice:
                    return (middlewareOrder.Sell, 100, lastPrice, 2)
                elif offData.onlineData.openPriceAdj[i][j] < sellPrice:
                    return (middlewareOrder.Sell, 100, offData.onlineData.openPriceAdj[i][j], 2)
                else:
                    return (middlewareOrder.Sell, 100, sellPrice, 2)

            return (middlewareOrder.Continue, 0, lastPrice, 1)

    class buyQueue(middlewareOffline):

        def __init__(self, IDs: list) -> None:
            super().__init__(IDs)
            self.name = 'buyQueue'

        def process(self, ID, offData: tickerOfflineData, i, onData: onlineData, j, todaytickersGroupData: tickersGroupData) -> tuple:
            
            lastPrice = self.adjust_price(onData.closePrice[i][j], offData.priceData.closePrice[i], onData.closePrice[i][-1])
            
            if self.history[ID] == {}:
                self.history[ID]['BuyIndex'] = (i, j)
                self.history[ID]['MaxPrice'] = lastPrice

            self.history[ID]['MaxPrice'] = max(self.history[ID]['MaxPrice'], lastPrice)

            buyI = self.history[ID]['BuyIndex'][0]
            buyJ = self.history[ID]['BuyIndex'][1]

            if i == buyI: # today
                pass
                # non buy queue
                if offData.clientData.realPower[i] < 1.3:

                    if j > buyJ+30:

                        numberOfNonBuyQueue = 0
                        for k in range(max(buyJ, j-59), j+1):
                            if onData.closePrice[i][k] != offData.priceData.maxAllowedPrice[i]:
                                numberOfNonBuyQueue += 1
                        if numberOfNonBuyQueue > 50:
                            return (middlewareOrder.Sell, 100, lastPrice, '1-NoneBuyQueue')

                        priceAverage = sum(onData.closePrice[i][j-29:j+1])/30
                        priceFall = (priceAverage-offData.priceData.maxAllowedPrice[i])/offData.priceData.maxAllowedPrice[i]*100
                        if priceFall < -2:
                            return (middlewareOrder.Sell, 100, lastPrice, '1-PriceAverage')

            else: # tomorrow and so on

                # price fall from yesterday close price
                priceFall = (lastPrice-offData.priceData.closePrice[i-1])/offData.priceData.closePrice[i-1]*100
                if priceFall < -4:
                    return (middlewareOrder.Sell, 100, lastPrice, '2-PriceFall')
                minute = 60
                if j > minute:
                    priceAverage = sum(onData.closePrice[i][j-59:j+1])/minute
                    priceFall = (priceAverage-offData.priceData.closePrice[i-1])/offData.priceData.closePrice[i-1]*100
                    if priceFall < -3:
                        return (middlewareOrder.Sell, 100, lastPrice, '2-PriceAverage')

                # time under yesterday close price
                # numberOfUnderYesterdayPrice = 0
                # if j > 60:
                #     for k in range(max(j-59, j+1), j+1):
                #         if lastPrice < offData.priceData.closePrice[i-1]:
                #             numberOfUnderYesterdayPrice += 1
                #     if numberOfUnderYesterdayPrice > 50:
                #         return (middlewareOrder.Sell, 100, lastPrice, '2-PriceUnder')


            # if onData.closePrice[i][j] == offData.priceData.minAllowedPrice[i]:
            #     return (middlewareOrder.Sell, 100, lastPrice, 'SellQueue')

            return (middlewareOrder.Continue, 0, lastPrice, 1)

    class sellQueue(middlewareOffline):

        def __init__(self, IDs: list) -> None:
            super().__init__(IDs)
            self.name = 'sellQueue'

        def process(self, ID, offData: tickerOfflineData, i, onData: onlineData, j, todaytickersGroupData: tickersGroupData) -> tuple:

            priceDif = (onData.closePrice[i][j]-offData.priceData.minAllowedPrice[i])/offData.priceData.minAllowedPrice[i]*100
            if  priceDif > 2.25:
                return (middlewareOrder.Sell, 100, onData.closePrice[i][j], 1)

            return (middlewareOrder.Continue, 0, onData.closePrice[i][j], 1)

    class ma180(middlewareOffline):

        def __init__(self, IDs: list) -> None:
            super().__init__(IDs)
            self.name = 'ma180'

        def process(self, ID, offData: tickerOfflineData, i, onData: onlineData, j, todaytickersGroupData: tickersGroupData) -> tuple:

            price = []
            for k in range(5, 0, -1):
                price  = price + onData.closePrice[i-k]
            price = price + onData.closePrice[i][:j+1]

            priceMa = calculateSma(price, 180, True)
            
            if offData.clientData.realPower[i] < 1:
                for k in range(1, 5):
                    try:
                        if price[-k] > priceMa[-k]:
                            break
                    except:
                        pass
                else:
                    return (middlewareOrder.Sell, 100, onData.closePrice[i][j], 1)

            return (middlewareOrder.Continue, 0, onData.closePrice[i][j], 1)

    class takeProfit(middlewareOffline):

        def __init__(self, IDs: list, takeProfitPRC) -> None:
            super().__init__(IDs)
            self.name = 'takeProfit'
            self.takeProfitPRC = takeProfitPRC

        def process(self, ID, offData: tickerOfflineData, i, onData: onlineData, j, todaytickersGroupData: tickersGroupData) -> tuple:

            if self.history[ID] == {}:
                self.history[ID]['BuyPrice'] = offData.onlineData.closePriceAdj[i][j-1] if j != 0 else offData.onlineData.closePriceAdj[i-1][-1]
            
            profit = (offData.onlineData.highPriceAdj[i][j]-self.history[ID]['BuyPrice'])/self.history[ID]['BuyPrice']*100-transactionFee
            
            sellPrice = int((1+(self.takeProfitPRC+transactionFee)/100)*self.history[ID]['BuyPrice'])
            if profit > self.takeProfitPRC:
                if offData.onlineData.openPriceAdj[i][j] > sellPrice:
                    return (middlewareOrder.Sell, 100, offData.onlineData.openPriceAdj[i][j], 1)
                else:
                    return (middlewareOrder.Sell, 100, sellPrice, 1)

            return (middlewareOrder.Continue, 0, sellPrice, 1)

    class trailingStopLoss(middlewareOffline):

        def __init__(self, IDs: list, trailingStopLoss) -> None:
            super().__init__(IDs)
            self.name = 'trailingStopLoss'
            self.trailingStopLoss = trailingStopLoss

        def process(self, ID, offData: tickerOfflineData, i, onData: onlineData, j, todaytickersGroupData: tickersGroupData) -> tuple:
            
            lastPrice = offData.onlineData.closePriceAdj[i][j]
            
            if self.history[ID] == {}:
                self.history[ID]['MaxPrice'] = lastPrice

            self.history[ID]['MaxPrice'] = max(self.history[ID]['MaxPrice'], lastPrice)

            dif = (lastPrice-self.history[ID]['MaxPrice'])/self.history[ID]['MaxPrice']*100

            if dif < -self.trailingStopLoss:
                return (middlewareOrder.Sell, 100, lastPrice, 1)

            return (middlewareOrder.Continue, 0, lastPrice, 1)

    class rsi(middlewareOffline):

        def __init__(self, IDs: list) -> None:
            super().__init__(IDs)
            self.name = 'rsi'

        def process(self, ID, offData: tickerOfflineData, i, onData: onlineData, j, todaytickersGroupData: tickersGroupData) -> tuple:

            price = []
            for k in range(2, 0, -1):
                price  = price + self.adjust_price(onData.closePrice[i-k], offData.priceData.closePrice[i], onData.closePrice[i][-1])
            price = price + self.adjust_price(onData.closePrice[i][:j+1], offData.priceData.closePrice[i], onData.closePrice[i][-1])

            rsi = calculateRsi(price, fillna= True)
            
            if rsi[-1] > 70 and onData.closePrice[i][j] != offData.priceData.maxAllowedPrice[i]:
                return (middlewareOrder.Sell, 100, price[-1], 1)

            return (middlewareOrder.Continue, 0, price[-1], 1)

    class bb(middlewareOffline):

        def __init__(self, IDs: list) -> None:
            super().__init__(IDs)
            self.name = 'bb'

        def process(self, ID, offData: tickerOfflineData, i, onData: onlineData, j, todaytickersGroupData: tickersGroupData) -> tuple:

            bbPrice = []
            lowPrice = []

            for k in range(6, 0, -1):
                bbPrice  = bbPrice + self.adjust_price(onData.closePrice[i-k], offData.priceData.closePrice[i], onData.closePrice[i][-1])
                # lowPrice  = lowPrice + self.adjust_price(onData.lowPrice[i-k], offData.priceData.closePrice[i], onData.closePrice[i][-1])
            bbPrice = bbPrice + self.adjust_price(onData.closePrice[i][:j+1], offData.priceData.closePrice[i], onData.closePrice[i][-1])
            # lowPrice = lowPrice + self.adjust_price(onData.lowPrice[i][:j+1], offData.priceData.closePrice[i], onData.closePrice[i][-1])

            bb = calculateBB(bbPrice, 240, 2, True)
            bbl = bb[2]
            bbh = bb[1]

            # bbPRC = [(lowPrice[k]-bbl[k])/(bbh[k]-bbl[k])*100 if bbh[k] != bbl[k] else 50 for k in range(len(bbPrice))]   
            bbPRC = [(bbPrice[k]-bbl[k])/(bbh[k]-bbl[k])*100 if bbh[k] != bbl[k] else 50 for k in range(len(bbPrice))]   

            lastPrice = self.adjust_price(onData.lowPrice[i][j], offData.priceData.closePrice[i], onData.closePrice[i][-1])
            if len(bbPRC) >= 2:
                if offData.clientData.realPower[i] > 0.7:
                    if bbPRC[-1] > 70:
                        return (middlewareOrder.Sell, 100, lastPrice, 1)

            return (middlewareOrder.Continue, 0, lastPrice, 1)

    class sellQueueCheck(middlewareOffline):

        def __init__(self, IDs: list) -> None:
            super().__init__(IDs)
            self.name = 'sellQueueCheck'

        def process(self, ID, offData: tickerOfflineData, i, onData: onlineData, j, todaytickersGroupData: tickersGroupData) -> tuple:

            price = self.adjust_price(onData.closePrice[i][max(j-2, 0):j+1], offData.priceData.closePrice[i], onData.closePrice[i][-1])

            for k in range(3):
                if price[-1-k] != offData.priceData.minAllowedPrice[i]:
                    break
            else:
                return (middlewareOrder.Sell, 100, price[-1], 1)

            return (middlewareOrder.Continue, 0, price[-1], 1)

    class marketTrigger(middlewareOffline):

        def __init__(self, IDs: list) -> None:
            super().__init__(IDs)
            self.name = 'marketTrigger'

        def process(self, ID, offData: tickerOfflineData, i, onData: onlineData, j, todaytickersGroupData: tickersGroupData) -> tuple:
            
            lastClosePrice = self.adjust_price(onData.closePrice[i][j], offData.priceData.closePrice[i], onData.closePrice[i][-1])
            # try:
            #     lastClosePrice = self.adjust_price(onData.closePrice[i][j+1], offData.priceData.closePrice[i], onData.closePrice[i][-1])
            # except:
            #     lastClosePrice = self.adjust_price(onData.closePrice[i][j], offData.priceData.closePrice[i], onData.closePrice[i][-1])
            lastClosePrice = self.adjust_price(onData.ordersBoard.row1.demandPrice[i][j], offData.priceData.closePrice[i], onData.closePrice[i][-1])
            # lastClosePrice = self.adjust_price(int((onData.ordersBoard.row1.supplyPrice[i][j]+onData.ordersBoard.row1.demandPrice[i][j])/2), offData.priceData.closePrice[i], onData.closePrice[i][-1])
            
            marketIndex = -1
            for m in range(1, len(todaytickersGroupData.time)):
                if onData.time[i][j] < todaytickersGroupData.time[m]:
                    marketIndex = m-1
                    break

            # if todaytickersGroupData.slope[marketIndex] < -0.02:
            #     return (middlewareOrder.Sell, 100, lastClosePrice, 1)

            # if todaytickersGroupData.index[marketIndex] < max(todaytickersGroupData.index[max(0, marketIndex-30):marketIndex])-0.35:
            #     return (middlewareOrder.Sell, 100, lastClosePrice, 1)

            # for k in range(4):
            #     if marketIndex >= k:
            #         if todaytickersGroupData.index[max(marketIndex-k, 0)] > todaytickersGroupData.indexMa[max(marketIndex-k, 0)]:
            #             break
            # else:
            #     if marketIndex >= k:
            #         return (middlewareOrder.Sell, 100, lastClosePrice, 1)

            # if offData.time[i] == '1400-01-17':
            maDif = todaytickersGroupData.index[marketIndex]-todaytickersGroupData.indexMa[marketIndex]
            if maDif < 0:
                if todaytickersGroupData.index[marketIndex] < 4:
                    return (middlewareOrder.Sell, 100, lastClosePrice, 1)

            return (middlewareOrder.Continue, 0, lastClosePrice, 1)

    class pivot(middlewareOffline):

        def __init__(self, IDs: list) -> None:
            super().__init__(IDs)
            self.name = 'pivot'

        def process(self, ID, offData: tickerOfflineData, i, onData: onlineData, j, todaytickersGroupData: tickersGroupData) -> tuple:
            
            lastClosePrice = self.adjust_price(onData.closePrice[i][j], offData.priceData.closePrice[i], onData.closePrice[i][-1])

            if i > 0:
                closePrices = onData.closePrice[i-1] + onData.closePrice[i][:j+1]
                if onData.closePrice[i][j] < 0.98 * max(closePrices[-60:]):
                    return (middlewareOrder.Sell, 100, lastClosePrice, 1)

            return (middlewareOrder.Continue, 0, lastClosePrice, 1)

    class tenkansenCross(middlewareOffline):

        def __init__(self, IDs: list) -> None:
            super().__init__(IDs)
            self.name = 'tenkansenCross'

        def process(self, ID, offData: tickerOfflineData, i, onData: onlineData, j, todaytickersGroupData: tickersGroupData) -> tuple:
            
            lastClosePrices = offData.onlineData.closePriceAdj[i-2] + offData.onlineData.closePriceAdj[i-1] + offData.onlineData.closePriceAdj[i][:j]
            if i > 1:
                if offData.onlineData.closePriceAdj[i][j] < offData.onlineData.tenkansen9[i][j] and offData.onlineData.tenkansen9[i][j] < offData.onlineData.tenkansen36[i][j] and\
                    offData.onlineData.closePriceAdj[i][j] < min(lastClosePrices) and offData.onlineData.closePrice[i][j] < offData.onlineData.openPrice[i][j]:
                        return (middlewareOrder.Sell, 100, offData.onlineData.closePriceAdj[i][j], 1)

            return (middlewareOrder.Continue, 0, offData.onlineData.closePriceAdj[i][j], 1)

    class tenkansenCross2(middlewareOffline):

        def __init__(self, IDs: list) -> None:
            super().__init__(IDs)
            self.name = 'tenkansenCross2'

        def process(self, ID, offData: tickerOfflineData, i, onData: onlineData, j, todaytickersGroupData: tickersGroupData) -> tuple:
            
            if i > 2:
                if offData.onlineData.ten[i][j] < offData.onlineData.kij[i][j] and offData.onlineData.ten[i-1][-1] < offData.onlineData.kij[i-1][-1]:
                    
                    return (middlewareOrder.Sell, 100, offData.onlineData.closePriceAdj[i][j], 1)

            return (middlewareOrder.Continue, 0, offData.onlineData.closePriceAdj[i][j], 1)

    class realPowerCheck(middlewareOffline):

        def __init__(self, IDs: list) -> None:
            super().__init__(IDs)
            self.name = 'realPowerCheck'

        def process(self, ID, offData: tickerOfflineData, i, onData: onlineData, j, todaytickersGroupData: tickersGroupData) -> tuple:
            
            if offData.clientData.realPower[i] < 0.7 and j == 3:
                    
                    return (middlewareOrder.Sell, 100, offData.onlineData.closePriceAdj[i][j], 1)

            return (middlewareOrder.Continue, 0, offData.onlineData.closePriceAdj[i][j], 1)