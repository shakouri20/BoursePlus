import datetime
from math import log10
from Application.Utility.DateConverter import *
from Application.Utility.Indicators.IndicatorService import *
from Infrastructure.Repository.OnlineDataRepository import onlineData_repo

class tickerOfflineData:
    def __init__(self, data: dict[list], truncateNumber) -> None:
        
        self.set_data(data, truncateNumber)

        self.onlineData: onlineData = onlineData(self)

    def set_data(self, data, truncateNumber):

        if len(data['Time']) < truncateNumber:
            truncateNumber = 0

        self.dateTime: list[datetime.date] = data['Time'][truncateNumber:]
        self.time: list[str] = [gregorian_to_jalali(day.strftime("%Y-%m-%d")) for day in self.dateTime]
        
        self.priceData = pricesItems(data, truncateNumber)
        self.clientData = clientItems(data, truncateNumber)
        self.volumeData = volumeItems(data, truncateNumber)
        self.indicatorData = indicatorItems(data, truncateNumber)

        self.rpvp = [self.volumeData.realVolume[i]/self.volumeData.volumeAvg[i]*self.clientData.realPowerLog[i] for i in range(len(self.dateTime))]
        self.realValueInput = [int((self.clientData.realBuyValue[i]-self.clientData.realSellValue[i])/10**7) for i in range(len(self.dateTime))]


class ordersBoard:
    def __init__(self) -> None:

        self.row1 = ordersBoardItems()
        self.row2 = ordersBoardItems()
        self.row3 = ordersBoardItems()
    

class ordersBoardItems:
    def __init__(self) -> None:
        self.demandPrice: list[list] = []
        self.demandVolume: list[list] = []
        self.demandNumber: list[list] = []
        self.supplyPrice: list[list] = []
        self.supplyVolume: list[list] = []
        self.supplyNumber: list[list] = []

class onlineData:
    def __init__(self, offlineData: tickerOfflineData) -> None:
        self.offlineData = offlineData
        self.time: list[list[datetime.datetime]] = []
        self.openPrice: list[list] = []
        self.closePrice: list[list] = []
        self.highPrice: list[list] = []
        self.lowPrice: list[list] = []
        self.volume: list[list] = []
        self.ordersBoard: ordersBoard = ordersBoard()

    @staticmethod
    def adjust_price(price, adjustedClosePrice, unAdjustedClosePrice):
        dif = (unAdjustedClosePrice-adjustedClosePrice)/adjustedClosePrice*100
        if abs(dif) < 1:
            return price
        else:
            if type(price) == list:
                tempPrice = price.copy()
                return [int(thisPrice * adjustedClosePrice / unAdjustedClosePrice) for thisPrice in tempPrice]
            else:
                return int(price * adjustedClosePrice / unAdjustedClosePrice)

    def create_new_variables(self):

        highPriceVec = []
        lowPriceVec = []
        self.openPriceAdj = []
        self.closePriceAdj = []
        self.highPriceAdj = [] 
        self.lowPriceAdj = [] 
        for i in range(len(self.time)):
            highPriceVec  = highPriceVec + self.adjust_price(self.highPrice[i], self.offlineData.priceData.closePrice[i], self.offlineData.onlineData.closePrice[i][-1])
            lowPriceVec  = lowPriceVec + self.adjust_price(self.lowPrice[i], self.offlineData.priceData.closePrice[i], self.offlineData.onlineData.closePrice[i][-1])
            self.openPriceAdj.append(self.adjust_price(self.openPrice[i], self.offlineData.priceData.closePrice[i], self.offlineData.onlineData.closePrice[i][-1]))
            self.closePriceAdj.append(self.adjust_price(self.closePrice[i], self.offlineData.priceData.closePrice[i], self.offlineData.onlineData.closePrice[i][-1]))
            self.highPriceAdj.append(self.adjust_price(self.highPrice[i], self.offlineData.priceData.closePrice[i], self.offlineData.onlineData.closePrice[i][-1]))
            self.lowPriceAdj.append(self.adjust_price(self.lowPrice[i], self.offlineData.priceData.closePrice[i], self.offlineData.onlineData.closePrice[i][-1]))

        # tenkansen9 = calculateIchimoko(highPriceVec, lowPriceVec, 9, 26, 52, True, False)[0]
        ich = calculateIchimoko(highPriceVec, lowPriceVec, 9, 36, 52, True, False)
        ten = ich[0]
        kij = ich[1]
        self.ten = []
        self.kij = []

        for i in range(len(self.time)):
            self.ten.append(ten[:len(self.time[i])])
            ten = ten[len(self.time[i]):]
            self.kij.append(kij[:len(self.time[i])])
            kij = kij[len(self.time[i]):]

class pricesItems:
    def __init__(self, data, truncateNumber) -> None:

        self.yesterdayPrice = data['YesterdayPrice']
        self.lowPrice = data['LowPrice']
        self.lowPricePRC = [(self.lowPrice[i]-self.yesterdayPrice[i])/self.yesterdayPrice[i]*100 for i in range(len(self.yesterdayPrice))]
        self.highPrice = data['HighPrice']
        self.highPricePRC = [(self.highPrice[i]-self.yesterdayPrice[i])/self.yesterdayPrice[i]*100 for i in range(len(self.yesterdayPrice))]
        self.openPrice = data['OpenPrice']
        self.openPricePRC = [(self.openPrice[i]-self.yesterdayPrice[i])/self.yesterdayPrice[i]*100 for i in range(len(self.yesterdayPrice))]
        self.closePrice = data['ClosePrice']
        self.closePricePRC = [(self.closePrice[i]-self.yesterdayPrice[i])/self.yesterdayPrice[i]*100 for i in range(len(self.yesterdayPrice))]
        self.todayPrice = data['TodayPrice']
        self.todayPricePRC = [(self.todayPrice[i]-self.yesterdayPrice[i])/self.yesterdayPrice[i]*100 for i in range(len(self.yesterdayPrice))]
        self.closePriceMa = calculateSma(data['ClosePrice'], fillna= True)
        self.minAllowedPrice = data['MinAllowedPrice']
        self.maxAllowedPrice = data['MaxAllowedPrice']

        truncator(self, truncateNumber)



class volumeItems:
    def __init__(self, data, truncateNumber) -> None:

        self.unAdjustedVolume = data['Volume']
        self.number = data['Number']
        self.value = data['Value']
        self.realVolume = [int(data['RealBuyValue'][i]/data['TodayPrice'][i]) for i in range(len(data['Time']))]
        self.volume = [int(data['Value'][i]/data['TodayPrice'][i]) for i in range(len(data['Time']))]
        self.volumeAvg = []
        for i in range(len(data['Time'])):
            if i==0:
                self.volumeAvg.append(self.volume[0])
            else:
                self.volumeAvg.append(sum(self.volume[max(0, i-30):i])/len(self.volume[max(0, i-30):i]))
        
        self.realVolumeAvg = []
        for i in range(len(data['Time'])):
            if i==0:
                self.realVolumeAvg.append(self.realVolume[0])
            else:
                self.realVolumeAvg.append(sum(self.realVolume[max(0, i-30):i])/len(self.realVolume[max(0, i-30):i]))

        truncator(self, truncateNumber)


class clientItems:

    def __init__(self, data, truncateNumber) -> None:

        self.realBuyNumber = data['RealBuyNumber']
        self.corporateBuyNumber = data['CorporateBuyNumber']
        self.realSellNumber = data['RealSellNumber']
        self.corporateSellNumber = data['CorporateSellNumber']
        self.realBuyVolume = data['RealBuyVolume']
        self.corporateBuyVolume = data['CorporateBuyVolume']
        self.realSellVolume = data['RealSellVolume']
        self.corporateSellVolume = data['CorporateSellVolume']
        self.realBuyValue = data['RealBuyValue']
        self.corporateBuyValue = data['CorporateBuyValue']
        self.realSellValue = data['RealSellValue']
        self.corporateSellValue = data['CorporateSellValue']
        self.realPercapitaBuy = [int(self.realBuyValue[i]/self.realBuyNumber[i]/10**7) if self.realBuyNumber[i] != 0 else 0 for i in range(len(self.realBuyNumber))]
        self.realPercapitaSell = [int(self.realSellValue[i]/self.realSellNumber[i]/10**7) if self.realSellNumber[i] != 0 else 0 for i in range(len(self.realSellNumber))]
        self.corporatePercapitaBuy = [int(self.corporateBuyValue[i]/self.corporateBuyNumber[i]/10**7) if self.corporateBuyNumber[i] != 0 else 0 for i in range(len(self.corporateBuyNumber))]
        self.corporatePercapitaSell = [int(self.corporateSellValue[i]/self.corporateSellNumber[i]/10**7) if self.corporateSellNumber[i] != 0 else 0 for i in range(len(self.corporateSellNumber))]
        self.realBuyPrc = [int(self.realBuyValue[i]/(self.corporateBuyValue[i]+self.realBuyValue[i])*100) if self.corporateBuyValue[i]+self.realBuyValue[i] != 0 else 0 for i in range(len(self.realBuyValue))]
        self.realSellPrc = [int(self.realSellValue[i]/(self.corporateSellValue[i]+self.realSellValue[i])*100) if self.corporateSellValue[i]+self.realSellValue[i] != 0 else 0 for i in range(len(self.realSellValue))]
        self.realPower = data['RealPower']
        self.realPowerLog = [log10(realPower) for realPower in self.realPower]

        truncator(self, truncateNumber)


class indicatorItems:
    def __init__(self, data, truncateNumber) -> None:

        self.rsi = calculateRsi(data['ClosePrice'], fillna= True)
        self.stochRsi = calculateStochRsi(data['ClosePrice'], fillna= True)
        self.macd = calculateMacd(data['ClosePrice'], fillna= True)
        self.bb = bollingerBandsItems(data['ClosePrice'], truncateNumber= truncateNumber)

        truncator(self, truncateNumber)


class bollingerBandsItems:
    def __init__(self, price, truncateNumber) -> None:
        bb = calculateBB(price, fillna= True)
        self.bbm = bb[0]
        self.bbh = bb[1]
        self.bbl = bb[2]
        self.pbbl = [(price[i]-self.bbl[i])/self.bbl[i]*100 for i in range(len(price))]
        self.pbbh = [(self.bbh[i]-price[i])/price[i]*100 for i in range(len(price))]
        self.pbblma = calculateSma(self.pbbl)
        self.pbbhma = calculateSma(self.pbbh)
        self.cw = [(self.bbh[i]-self.bbl[i])/self.bbl[i]*100 for i in range(len(price))]

        self.pbbd = []
        for i in range(len(price)):
            if self.bbh[i] != self.bbl[i]:
                self.pbbd.append((price[i]-self.bbl[i])/(self.bbh[i]-self.bbl[i])*100)
            else:
                self.pbbd.append(50)
        
        truncator(self, truncateNumber)


def truncator(self, truncateNumber):
    attributes = vars(self)
    for atr in attributes:
        if type(attributes[atr]) == list:
            attributes[atr] = attributes[atr][truncateNumber:]

class tickersGroupData:

    def __init__(self, ID, day: datetime.date) -> None:

        data = onlineData_repo().read_onlineData_by_ID_and_day(ID, day.strftime("%Y-%m-%d"))
        self.time: list[datetime.datetime] = data[ID]['Time']
        self.yesterdayPrice: list[datetime.datetime] = data[ID]['YesterdayPrice']
        
        self.index = [item/1000 for item in data[ID]['LastPrice']]
        self.indexMa = calculateSma(self.index, 10, True) # 20

        # self.slope = [0.05 if self.index[i] > self.indexMa[i] and i > 3 else 0 for i in range(len(self.time))]
        self.slope = [0 for _ in range(len(self.time))]
        for i in range(3, len(self.time)):
            self.slope[i] = self.index[i] - self.index[max(i-5, 0)] # 5
            self.slope[i] /= ((self.time[i]-self.time[max(i-5, 0)]).total_seconds()/60)
        self.slopeMA = calculateSma(self.slope, 25, True)# 25


