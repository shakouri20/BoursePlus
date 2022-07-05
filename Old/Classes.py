from SqlServerDataBaseLib import DatabaseConnection, UpdateDailyRecordsOfDataTable, convert_ar_characters
from DateConverter import *
from typing import Dict

class Ticker:
    def __init__(self, ID, fromDate, Todate) -> None:
        DB = DatabaseConnection()
        DB.connect()
        fromDate = jalali_to_gregorian(fromDate)
        Todate = jalali_to_gregorian(Todate)
        cmd = '''
        SELECT * FROM OfflineData Where ID = {} and Time BETWEEN '{}' and '{}' ORDER BY Time ASC 
        '''.format(ID, fromDate, Todate)
        DB.execute(cmd)
        self.Date = []
        self.LowPrice = []
        self.HighPrice = []
        self.OpenPrice = []
        self.ClosePrice = []
        self.ClosePricePRC = []
        self.TodayPrice = []
        self.TodayPricePRC = []
        self.YesterdayPrice = []
        self.Volume = []
        self.Number = []
        self.RealBuynumber = []
        self.CorporateBuyNumber = []
        self.RealSellNumber = []
        self.CorporateSellNumber = []
        self.RealBuyVolume = []
        self.CorporateBuyVolume = []
        self.RealSellVolume = []
        self.CorporateSellVolume = []
        self.RealBuyValue = []
        self.CorporateBuyValue = []
        self.RealSellValue = []
        self.CorporateSellvalue = []
        self.RealPower = []
        for row in DB.cursor:
            self.Date.append(gregorian_to_jalali(row['Time'].strftime("%Y-%m-%d")))
            # self.Date.append(row['Date'])
            self.LowPrice.append(row['LowPrice'])
            self.HighPrice.append(row['HighPrice'])
            self.OpenPrice.append(row['OpenPrice'])
            self.ClosePrice.append(row['ClosePrice'])
            self.ClosePricePRC.append(row['ClosePricePRC'])
            self.TodayPrice.append(row['TodayPrice'])
            self.TodayPricePRC.append(row['TodayPricePRC'])
            self.YesterdayPrice.append(row['YesterdayPrice'])
            self.Volume.append(row['Volume'])
            self.Number.append(row['Number'])
            self.RealBuynumber.append(row['RealBuyNumber'])
            self.CorporateBuyNumber.append(row['CorporateBuyNumber'])
            self.RealSellNumber.append(row['RealSellNumber'])
            self.CorporateSellNumber.append(row['CorporateSellNumber'])
            self.RealBuyVolume.append(row['RealBuyVolume'])
            self.CorporateBuyVolume.append(row['CorporateBuyVolume'])
            self.RealSellVolume.append(row['RealSellVolume'])
            self.CorporateSellVolume.append(row['CorporateSellVolume'])
            self.RealBuyValue.append(row['RealBuyValue'])
            self.CorporateBuyValue.append(row['CorporateBuyValue'])
            self.RealSellValue.append(row['RealSellValue'])
            self.CorporateSellvalue.append(row['CorporateSellValue'])
            self.RealPower.append(row['RealPower'])
            # self.ClosePricePRC = [(self.ClosePrice[i]-self.YesterdayPrice[i])/self.YesterdayPrice[i]*100 for i in range(len(self.ClosePrice))]
            # self.TodayPricePRC = [(self.TodayPrice[i]-self.YesterdayPrice[i])/self.YesterdayPrice[i]*100 for i in range(len(self.TodayPrice))]
            self.dateDict = {}
        # self.RealPower = [self.RealPower[i] if type(self.RealPower[i]) is float else 1 for i in range(len(self.RealPower))]
        for i in range(len(self.Date)):
            self.dateDict[self.Date[i]] = i
        DB.commit()
        DB.close()

        if len(self.Volume) < 30 and len(self.Volume) != 0:
            self.VolumeAvg1 = sum(self.Volume) / len(self.Volume)
        else:
            self.VolumeAvg1 = sum(self.Volume[-30:]) / 30
    

    def getLowPrice(self, str):
        return self.LowPrice[self.dateDict[str]]
    def getHighPrice(self, str):
        return self.HighPrice[self.dateDict[str]]
    def getOpenPrice(self, str):
        return self.OpenPrice[self.dateDict[str]]
    def getClosePrice(self, str):
        return self.ClosePrice[self.dateDict[str]]
    def getClosePricePRC(self, str):
        return self.ClosePricePRC[self.dateDict[str]]
    def getTodayPrice(self, str):
        return self.TodayPrice[self.dateDict[str]]
    def getTodayPricePRC(self, str):
        return self.TodayPricePRC[self.dateDict[str]]
    def getYesterdayPrice(self, str):
        return self.YesterdayPrice[self.dateDict[str]]
    def getVolume(self, str):
        return self.Volume[self.dateDict[str]]
    def getNumber(self, str):
        return self.Number[self.dateDict[str]]
    def getRealBuynumber(self, str):
        return self.RealBuynumber[self.dateDict[str]]
    def getCorporateBuyNumber(self, str):
        return self.CorporateBuyNumber[self.dateDict[str]]
    def getRealSellNumber(self, str):
        return self.RealSellNumber[self.dateDict[str]]
    def getCorporateSellNumber(self, str):
        return self.CorporateSellNumber[self.dateDict[str]]
    def getRealBuyVolume(self, str):
        return self.RealBuyVolume[self.dateDict[str]]
    def getCorporateBuyVolume(self, str):
        return self.CorporateBuyVolume[self.dateDict[str]]
    def getRealSellVolume(self, str):
        return self.RealSellVolume[self.dateDict[str]]
    def getCorporateSellVolume(self, str):
        return self.CorporateSellVolume[self.dateDict[str]]
    def getRealBuyValue(self, str):
        return self.RealBuyValue[self.dateDict[str]]
    def getCorporateBuyValue(self, str):
        return self.CorporateBuyValue[self.dateDict[str]]
    def getRealSellValue(self, str):
        return self.RealSellValue[self.dateDict[str]]
    def getCorporateSellvalue(self, str):
        return self.CorporateSellvalue[self.dateDict[str]]
    def getRealPower(self, str):
        return self.RealPower[self.dateDict[str]]


def getTickers(FarsiTickers, fromDate, ToDate) -> dict[Ticker]:
    DB = DatabaseConnection()
    DB.connect()
    cmd = 'SELECT ID, FarsiTicker FROM Tickers WHERE FarsiTicker IN ('
    for i in range(len(FarsiTickers)):
        if i != len(FarsiTickers) - 1:
            cmd += "'{}', ".format(FarsiTickers[i])
        else:
            cmd += "'{}') ".format(FarsiTickers[i])
    DB.execute(cmd)

    Tickers = {}
    for row in DB.cursor:
        Tickers[convert_ar_characters(row['FarsiTicker']).replace(' ', '')] = Ticker(row['ID'], fromDate, ToDate)
        
    DB.commit()
    DB.close()
    return Tickers



