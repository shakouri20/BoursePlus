from datetime import datetime
from math import log10
from turtle import ondrag
from Application.Utility.Indicators.IndicatorService import calculateBB, calculateEma, calculateRsi, calculateSma
from Domain.Models.MiddlewareOffline import middlewareOffline
from Domain.Models.TickerOfflineData import tickersGroupData, tickerOfflineData, onlineData
from Domain.Enums.MiddlewareOrder import middlewareOrder
from Infrastructure.Repository.OfflineDataRepository import offlineData_repo
from Infrastructure.Repository.OnlineDataRepository import onlineData_repo


class m_buyMiddlewares:

    class test(middlewareOffline):

        def __init__(self, IDs: list) -> None:
            super().__init__(IDs)
            self.name = 'test'

        def process(self, ID, offData: tickerOfflineData, i, onData: onlineData, j, todaytickersGroupData: tickersGroupData) -> tuple:
            
            lastPrice = self.adjust_price(onData.closePrice[i][j], offData.priceData.closePrice[i], onData.closePrice[i][-1])
            if offData.time[i] == '1400-08-10':
                return (middlewareOrder.Buy, 100, lastPrice, 1)
            return (middlewareOrder.Continue, 0, lastPrice, 1)

    class buyQueue(middlewareOffline):

        def __init__(self, IDs: list) -> None:
            super().__init__(IDs)
            self.name = 'buyQueue'

        def process(self, ID, offData: tickerOfflineData, i, onData: onlineData, j, todaytickersGroupData: tickersGroupData) -> tuple:

            lastPrice = self.adjust_price(onData.closePrice[i][j], offData.priceData.closePrice[i], onData.closePrice[i][-1])

            if onData.closePrice[i][j] == offData.priceData.maxAllowedPrice[i]:
                # normalVolume = onData.volume[i][j] / offData.volumeData.volumeAvg[i-1] * 210
            #     if normalVolume > 20:
                return (middlewareOrder.Buy, 100, lastPrice, 1)

            return (middlewareOrder.Continue, 0, lastPrice, 1)

    class sellQueue(middlewareOffline):

        def __init__(self, IDs: list) -> None:
            super().__init__(IDs)
            self.name = 'sellQueue'

        def process(self, ID, offData: tickerOfflineData, i, onData: onlineData, j, todaytickersGroupData: tickersGroupData) -> tuple:

            normalVolume = onData.volume[i][j] / offData.volumeData.volumeAvg[i-1] * 210
            
            for k in range(4):
                if j >= k and onData.closePrice[i][j-k] == offData.priceData.minAllowedPrice[i]:
                    if normalVolume > 30:
                        return (middlewareOrder.Buy, 100, offData.priceData.minAllowedPrice[i], 1)
                    

            return (middlewareOrder.Continue, 0, onData.closePrice[i][j], 1)

    class ma180(middlewareOffline):

        def __init__(self, IDs: list) -> None:
            super().__init__(IDs)
            self.name = 'ma180'

        def process(self, ID, offData: tickerOfflineData, i, onData: onlineData, j, todaytickersGroupData: tickersGroupData) -> tuple:

            price = []
            for k in range(5, 0, -1):
                price  = price + self.adjust_price(onData.closePrice[i-k], offData.priceData.closePrice[i], onData.closePrice[i][-1])
            price = price + self.adjust_price(onData.closePrice[i][:j+1], offData.priceData.closePrice[i], onData.closePrice[i][-1])

            priceMa = calculateSma(price, 180, True)
            
            if offData.clientData.realPower[i] > 1:
                for k in range(1, 5):
                    try:
                        if price[-k] < priceMa[-k]:
                            break
                    except:
                        pass
                else:
                    return (middlewareOrder.Buy, 100, price[-1], 1)

            return (middlewareOrder.Continue, 0, price[-1], 1)

    class rsi(middlewareOffline):

        def __init__(self, IDs: list) -> None:
            super().__init__(IDs)
            self.name = 'rsi'

        def process(self, ID, offData: tickerOfflineData, i, onData: onlineData, j, todaytickersGroupData: tickersGroupData) -> tuple:

            price = []
            for k in range(2, 0, -1):
                if i >= k:
                    price  = price + self.adjust_price(onData.closePrice[i-k], offData.priceData.closePrice[i], onData.closePrice[i][-1])
            price = price + self.adjust_price(onData.closePrice[i][:j+1], offData.priceData.closePrice[i], onData.closePrice[i][-1])

            rsi = calculateRsi(price, fillna= True)
            
            if rsi[-1] < 20 and onData.closePrice[i][j] != offData.priceData.minAllowedPrice[i]:
                return (middlewareOrder.Buy, 100, price[-1], 1)

            return (middlewareOrder.Continue, 0, price[-1], 1)

    class bb(middlewareOffline):

        def __init__(self, IDs: list) -> None:
            super().__init__(IDs)
            self.name = 'bb'

        def process(self, ID, offData: tickerOfflineData, i, onData: onlineData, j, todaytickersGroupData: tickersGroupData) -> tuple:

            if j >= 4:
                # if offData.clientData.realPower[i] > 0.666:
                    dayMinPrice = min(onData.lowPrice[i][:j+1])
                    dif = (onData.closePrice[i][j]-dayMinPrice)/dayMinPrice*100
                    if dif < 2:        
                        if onData.closePrice[i][j] > 1.005 * min(onData.lowPrice[i][j-4:j+1]):
                            for k in range(j):
                                if onData.lowPrice[i][k] == offData.priceData.minAllowedPrice[i]:
                                    break
                            else:                             
                                bbPrice = []
                                for k in range(6, 0, -1):
                                    if i >= k:
                                        bbPrice  = bbPrice + self.adjust_price(onData.closePrice[i-k], offData.priceData.closePrice[i-k], onData.closePrice[i-k][-1])
                                bbPrice = bbPrice + self.adjust_price(onData.closePrice[i][:j+1], offData.priceData.closePrice[i], onData.closePrice[i][-1])

                                bb = calculateBB(bbPrice, 240, 2, True)
                                bbl = bb[2]
                                bbh = bb[1]

                                bbPRC = [(bbPrice[k]-bbl[k])/(bbh[k]-bbl[k])*100 if bbh[k] != bbl[k] else 50 for k in range(len(bbPrice))]   

                                lastClosePrice = self.adjust_price(onData.closePrice[i][j], offData.priceData.closePrice[i], onData.closePrice[i][-1])
                
                                for m in range(4):
                                    if m <= j:
                                        if bbPRC[-1-m] < 10:
                                            # if offData.time[i] == '1400-07-18':
                                            marketIndex = -1
                                            for m in range(1, len(todaytickersGroupData.time)):
                                                if onData.time[i][j] < todaytickersGroupData.time[m]:
                                                    marketIndex = m-1
                                                    break
                                            if todaytickersGroupData.slope[marketIndex] > 0.01:
                                                x = 1
                                                return (middlewareOrder.Buy, 100, lastClosePrice, 1)
                                            break

            return (middlewareOrder.Continue, 0, 0, 1)
       
    class bb2(middlewareOffline):

        def __init__(self, IDs: list) -> None:
            super().__init__(IDs)
            self.name = 'bb2'

        def process(self, ID, offData: tickerOfflineData, i, onData: onlineData, j, todaytickersGroupData: tickersGroupData) -> tuple:
            
            if i > 1 and j >= 4:
                dayMinPrice = min(onData.lowPrice[i][:j+1])
                dif = (onData.closePrice[i][j]-dayMinPrice)/dayMinPrice*100
                if dif < 2:
                    yesterdayClosePrice = sum(onData.lowPrice[i-1][-5:])/len(onData.lowPrice[i-1][-5:])
                    yesterdayCloseMinAllowedPriceDif = (yesterdayClosePrice-offData.priceData.minAllowedPrice[i-1])/offData.priceData.minAllowedPrice[i-1]*100
                    lastCloseYesterdayPriceDif = (onData.closePrice[i][j]-yesterdayClosePrice)/yesterdayClosePrice*100
                    if yesterdayCloseMinAllowedPriceDif > 0.1 or yesterdayCloseMinAllowedPriceDif < 0.1 and abs(lastCloseYesterdayPriceDif) > 0:      
                        for k in range(j):
                            if onData.lowPrice[i][k] == offData.priceData.minAllowedPrice[i]:
                                break
                        else:  
                            marketIndex = -1
                            for m in range(1, len(todaytickersGroupData.time)):
                                if onData.time[i][j] < todaytickersGroupData.time[m]:
                                    marketIndex = m-1
                                    break
                            if todaytickersGroupData.slope[marketIndex] > 0.01:                           
                                bbPrice = []
                                for k in range(6, 0, -1):
                                    if i >= k:
                                        bbPrice  = bbPrice + self.adjust_price(onData.closePrice[i-k], offData.priceData.closePrice[i-k], onData.closePrice[i-k][-1])
                                bbPrice = bbPrice + self.adjust_price(onData.closePrice[i][:j+1], offData.priceData.closePrice[i], onData.closePrice[i][-1])

                                bb = calculateBB(bbPrice, 240, 2, True)
                                bbl = bb[2]
                                bbh = bb[1]

                                bbPRC = [(bbPrice[k]-bbl[k])/(bbh[k]-bbl[k])*100 if bbh[k] != bbl[k] else 50 for k in range(len(bbPrice))]   

                                for m in range(10):
                                    if m <= j:
                                        if bbPRC[-1-m] < 10:
                                            # if offData.time[i] == '1400-01-17':
                                                return (middlewareOrder.Buy, 100, bbPrice[-1], 1)

            return (middlewareOrder.Continue, 0, 0, 1)

    class marketTrigger(middlewareOffline):

        def __init__(self, IDs: list) -> None:
            super().__init__(IDs)
            self.name = 'marketTrigger'

        def process(self, ID, offData: tickerOfflineData, i, onData: onlineData, j, todaytickersGroupData: tickersGroupData) -> tuple:
            
            # lastClosePrice = self.adjust_price(onData.closePrice[i][j], offData.priceData.closePrice[i], onData.closePrice[i][-1])
            # try:
            #     lastClosePrice = self.adjust_price(onData.closePrice[i][j+1], offData.priceData.closePrice[i], onData.closePrice[i][-1])
            # except:
            #     lastClosePrice = self.adjust_price(onData.closePrice[i][j], offData.priceData.closePrice[i], onData.closePrice[i][-1])

            lastClosePrice = self.adjust_price(onData.ordersBoard.row1.supplyPrice[i][j], offData.priceData.closePrice[i], onData.closePrice[i][-1])
            # lastClosePrice = self.adjust_price(int((onData.ordersBoard.row1.supplyPrice[i][j]+onData.ordersBoard.row1.demandPrice[i][j])/2), offData.priceData.closePrice[i], onData.closePrice[i][-1])

            marketIndex = -1
            for m in range(1, len(todaytickersGroupData.time)):
                if onData.time[i][j] < todaytickersGroupData.time[m]:
                    marketIndex = m-1
                    break

            if todaytickersGroupData.slope[marketIndex] > 0.03 and todaytickersGroupData.index[marketIndex] > todaytickersGroupData.indexMa[marketIndex]:
                # if onData.time[i][j] < onData.time[i][j].replace(hour= 10, minute= 30): # onData.time[i][j].replace(hour= 9, minute= 15) <
                # rsiPrice = []
                # for k in range(3, 0, -1):
                #     if i >= k:
                #         rsiPrice  = rsiPrice + self.adjust_price(onData.closePrice[i-k], offData.priceData.closePrice[i-k], onData.closePrice[i-k][-1])[::5]
                # rsiPrice = rsiPrice + self.adjust_price(onData.closePrice[i][:j+1], offData.priceData.closePrice[i], onData.closePrice[i][-1])[::5]

                # rsi = calculateRsi(rsiPrice, 14, True)
                # for m in range(10):
                #     if m < len(rsi):
                #         if rsi[-1-m] < 30:
                #             if offData.time[i] == '1400-11-03':
                                return (middlewareOrder.Buy, 100, lastClosePrice, 1)

            return (middlewareOrder.Continue, 0, lastClosePrice, 1)
    
    class marketTrigger2(middlewareOffline):

        def __init__(self, IDs: list) -> None:
            super().__init__(IDs)
            self.name = 'marketTrigger2'

        def process(self, ID, offData: tickerOfflineData, i, onData: onlineData, j, todaytickersGroupData: tickersGroupData) -> tuple:
            
            lastClosePrice = self.adjust_price(onData.closePrice[i][j], offData.priceData.closePrice[i], onData.closePrice[i][-1])

            marketIndex = -1
            for m in range(1, len(todaytickersGroupData.time)):
                if onData.time[i][j] < todaytickersGroupData.time[m]:
                    marketIndex = m-1
                    break

            if todaytickersGroupData.slope[marketIndex] > 0.03 and todaytickersGroupData.index[marketIndex] > todaytickersGroupData.indexMa[marketIndex]: 
                tickerPriceMa = calculateEma(onData.closePrice[i][:j+1], 30, True)
                # tickerPriceMaMa = calculateEma(tickerPriceMa, 20, True)
                # maDif = [(tickerPriceMa[i]-tickerPriceMaMa[i])*10 for i in range(len(tickerPriceMa))]
                # if maDif[-1] > 0:
                if onData.closePrice[i][j] > tickerPriceMa[-1]:
                    return (middlewareOrder.Buy, 100, lastClosePrice, 1)

            return (middlewareOrder.Continue, 0, lastClosePrice, 1)

    class pivot(middlewareOffline):

        def __init__(self, IDs: list) -> None:
            super().__init__(IDs)
            self.name = 'pivot'

        def process(self, ID, offData: tickerOfflineData, i, onData: onlineData, j, todaytickersGroupData: tickersGroupData) -> tuple:
            
            lastClosePrice = self.adjust_price(onData.closePrice[i][j], offData.priceData.closePrice[i], onData.closePrice[i][-1])

            if i > 0:
                closePrices = onData.closePrice[i-1] + onData.closePrice[i][:j+1]
                if onData.closePrice[i][j] > 1.02 * min(closePrices[-60:]):
                    return (middlewareOrder.Buy, 100, lastClosePrice, 1)

            return (middlewareOrder.Continue, 0, lastClosePrice, 1)
    
    class tenkansenCross(middlewareOffline):

        def __init__(self, IDs: list) -> None:
            super().__init__(IDs)
            self.name = 'tenkansenCross'

        def process(self, ID, offData: tickerOfflineData, i, onData: onlineData, j, todaytickersGroupData: tickersGroupData) -> tuple:
            
            lastClosePrices = offData.onlineData.closePriceAdj[i-2] + offData.onlineData.closePriceAdj[i-1] + offData.onlineData.closePriceAdj[i][:j]
            if i > 1:
                if offData.onlineData.closePriceAdj[i][j] > offData.onlineData.tenkansen9[i][j] and offData.onlineData.tenkansen9[i][j] > offData.onlineData.tenkansen36[i][j] and\
                    offData.onlineData.closePriceAdj[i][j] > max(lastClosePrices) and offData.onlineData.closePrice[i][j] > offData.onlineData.openPrice[i][j]:
                        return (middlewareOrder.Buy, 100, offData.onlineData.closePriceAdj[i][j], 1)

            return (middlewareOrder.Continue, 0, offData.onlineData.closePriceAdj[i][j], 1)
    
    class tenkansenCross2(middlewareOffline):

        def __init__(self, IDs: list) -> None:
            super().__init__(IDs)
            self.name = 'tenkansenCross2'

        def process(self, ID, offData: tickerOfflineData, i, onData: onlineData, j, todaytickersGroupData: tickersGroupData) -> tuple:
            
            # lastClosePrices = offData.onlineData.closePriceAdj[i-3] + offData.onlineData.closePriceAdj[i-2] + offData.onlineData.closePriceAdj[i-1] + offData.onlineData.closePriceAdj[i][:j]
            # lastHighPrices = offData.onlineData.highPriceAdj[i-3] + offData.onlineData.highPriceAdj[i-2] + offData.onlineData.highPriceAdj[i-1] + offData.onlineData.highPriceAdj[i][:j]
            if i > 2:
                if offData.onlineData.ten[i][j] > offData.onlineData.kij[i][j] and offData.onlineData.ten[i-1][-1] < offData.onlineData.kij[i-1][-1]:
                    try:
                        crossDif = (offData.onlineData.ten[i][j]-offData.onlineData.ten[i][j-1])/offData.onlineData.ten[i][j-1]*100
                    except:
                        crossDif = (offData.onlineData.ten[i][j]-offData.onlineData.ten[i-1][-1])/offData.onlineData.ten[i-1][-1]*100
                    
                    if crossDif > 1:
                        return (middlewareOrder.Buy, 100, offData.onlineData.closePriceAdj[i][j], 1)

            return (middlewareOrder.Continue, 0, offData.onlineData.closePriceAdj[i][j], 1)

    class positiveRange(middlewareOffline):

        def __init__(self, IDs: list) -> None:
            super().__init__(IDs)
            self.name = 'positiveRange'

        def process(self, ID, offData: tickerOfflineData, i, onData: onlineData, j, todaytickersGroupData: tickersGroupData) -> tuple:
            
            if i > 0 and j > 30:
                lastClosePrices = onData.closePriceAdj[i][j-4:j+1]
                maxPriceOfDay = max(onData.closePriceAdj[i][:j])
                if lastClosePrices[-1] > maxPriceOfDay:
                    priceChange = (lastClosePrices[-1]-lastClosePrices[0])/lastClosePrices[0]*100
                    if priceChange > 1:
                        # normalVolume = sum(onData.volume[i][j-4:j+1])/5/offData.volumeData.volumeAvg[i-1]*210
                        normalVolume = sum(onData.volume[i][j-4:j+1])/sum(onData.volume[i][j-9:j-4])
                        if normalVolume > 10:
                            return (middlewareOrder.Buy, 100, offData.onlineData.closePriceAdj[i][j], 1)

            return (middlewareOrder.Continue, 0, offData.onlineData.closePriceAdj[i][j], 1)
    
    class positiveRange2(middlewareOffline):

        def __init__(self, IDs: list) -> None:
            super().__init__(IDs)
            self.name = 'positiveRange2'

        def process(self, ID, offData: tickerOfflineData, i, onData: onlineData, j, todaytickersGroupData: tickersGroupData) -> tuple:
            
            if onData.time[i][j] > datetime(2022, 4, 6, 9, 47):
                x = 1

            if i > 0 and j > 15 and (onData.time[i][j].hour > 9 or onData.time[i][j].hour == 9 and onData.time[i][j].minute > 30):

                lastHighPrices = onData.highPriceAdj[i][:j+1]

                window = 15
                priceMa= calculateSma(lastHighPrices, window= window,  fillna= True)

                if priceMa[window] > priceMa[window-1]: 
                    Rising = True
                else:
                    Rising = False

                levels = [] #priceMa[window]
                for k in range(window+1, len(priceMa)):

                    if priceMa[k] > priceMa[k-1] and Rising == False:
                        Rising = True

                    elif priceMa[k] < priceMa[k-1] and Rising == True:
                        Rising = False
                        levels.append(priceMa[k-1])

                if len(levels) > 0:

                    highPricesRange = (max(levels)-min(levels))/min(levels)*100

                    res = (max(levels) + min(levels))/2

                    if onData.closePriceAdj[i][j] > onData.openPriceAdj[i][j] and onData.closePriceAdj[i][j-1] > onData.openPriceAdj[i][j-1]:

                        if highPricesRange < 1 and onData.closePriceAdj[i][j] > res and onData.closePriceAdj[i][j-1] > res:

                            dayHighPrice = max(onData.highPriceAdj[i][:j])
                            dayHighPriceDif = (onData.highPriceAdj[i][j]-dayHighPrice)/dayHighPrice*100

                            if abs(dayHighPriceDif) < 2 and onData.closePriceAdj[i][j] > dayHighPrice:

                                priceChange = (onData.closePriceAdj[i][j]-onData.closePriceAdj[i][j-2])/onData.closePriceAdj[i][j-2]*100
                                if priceChange > 1:

                                    # normalVolume = sum(onData.volume[i][j-4:j+1])/5/offData.volumeData.volumeAvg[i-1]*210
                                    normalVolume = sum(onData.volume[i][j-1:j+1])/sum(onData.volume[i][j-3:j-1])
                                    if normalVolume > 5:
                                        return (middlewareOrder.Buy, 100, offData.onlineData.closePriceAdj[i][j], 1)

            return (middlewareOrder.Continue, 0, offData.onlineData.closePriceAdj[i][j], 1)
    
    class positiveRange3(middlewareOffline):

        def __init__(self, IDs: list) -> None:
            super().__init__(IDs)
            self.name = 'positiveRange3'

        def process(self, ID, offData: tickerOfflineData, i, onData: onlineData, j, todaytickersGroupData: tickersGroupData) -> tuple:
            
            if i > 0 and j > 30:
                lastPrices = [(onData.highPriceAdj[i][j-k]+onData.lowPriceAdj[i][j-k])/2 for k in range(30)]

                pricesRange = (max(lastPrices)-min(lastPrices))/min(lastPrices)*100

                if pricesRange < 2:
                    priceChange = (onData.closePriceAdj[i][j]-onData.closePriceAdj[i][j-1])/onData.closePriceAdj[i][j-1]*100
                    if priceChange > 1:
                        # normalVolume = sum(onData.volume[i][j-4:j+1])/5/offData.volumeData.volumeAvg[i-1]*210
                        normalVolume = sum(onData.volume[i][j-2:j+1])/sum(onData.volume[i][j-5:j-2])
                        if normalVolume > 10:
                            return (middlewareOrder.Buy, 100, offData.onlineData.closePriceAdj[i][j], 1)

            return (middlewareOrder.Continue, 0, offData.onlineData.closePriceAdj[i][j], 1)

    class realPowerCheck(middlewareOffline):

        def __init__(self, IDs: list) -> None:
            super().__init__(IDs)
            self.name = 'realPowerCheck'

        def process(self, ID, offData: tickerOfflineData, i, onData: onlineData, j, todaytickersGroupData: tickersGroupData) -> tuple:
            
            if offData.clientData.realPower[i] < 0.7:
                    
                    return (middlewareOrder.Delete, 100, offData.onlineData.closePriceAdj[i][j], 1)

            return (middlewareOrder.Continue, 0, offData.onlineData.closePriceAdj[i][j], 1)
         