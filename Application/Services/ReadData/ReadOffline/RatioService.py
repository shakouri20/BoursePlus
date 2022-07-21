import datetime
from Application.Utility.Indicators.IndicatorService import calculateMacd, calculateRsi, calculateSma
from Domain.Enums.dateType import dateType
from Infrastructure.Repository.OfflineDataRepository import offlineData_repo
from Old.DateConverter import *

class tickerCompare:
    
    def __init__(self, ticker1, ticker2, fromDate, toDate) -> None:

        if type(ticker1) == str:
            tickerData1 = offlineData_repo().read_by_farsiTicker_and_time('Time', 'ClosePrice', 'OpenPrice', 'HighPrice', 'LowPrice', farsiTicker= ticker1, fromDate= fromDate, toDate= toDate, outputDateType= dateType.gregorian)
            tickerData2 = offlineData_repo().read_by_farsiTicker_and_time('Time', 'ClosePrice', 'OpenPrice', 'HighPrice', 'LowPrice', farsiTicker= ticker2, fromDate= fromDate, toDate= toDate, outputDateType= dateType.gregorian)
        else:
            tickerData1 = offlineData_repo().read_by_ID_and_time('Time', 'ClosePrice', 'OpenPrice', 'HighPrice', 'LowPrice', ID= ticker1, fromDate= fromDate, toDate= toDate, outputDateType= dateType.gregorian)
            tickerData2 = offlineData_repo().read_by_ID_and_time('Time', 'ClosePrice', 'OpenPrice', 'HighPrice', 'LowPrice', ID= ticker2, fromDate= fromDate, toDate= toDate, outputDateType= dateType.gregorian)

        tickerDatesG1 = tickerData1['Time']
        tickerDatesG2 = tickerData2['Time']

        self.tickerClosePrice1 = []
        self.tickerOpenPrice1 = []
        self.tickerHighPrice1 = []
        self.tickerLowPrice1 = []

        self.tickerClosePrice2 = []
        self.tickerOpenPrice2 = []
        self.tickerHighPrice2 = []
        self.tickerLowPrice2 = []

        self.datesG = []

        for date in tickerDatesG2:
            if date in tickerDatesG1:
                self.datesG.append(date)
                for i in range(len(tickerDatesG1)):
                    if tickerDatesG1[i] == date:
                        self.tickerClosePrice1.append(tickerData1['ClosePrice'][i] if len(self.tickerClosePrice1)==0 or 0.3 < tickerData1['ClosePrice'][i]/self.tickerClosePrice1[-1] < 2.1 else self.tickerClosePrice1[-1])
                        self.tickerOpenPrice1.append(tickerData1['OpenPrice'][i] if len(self.tickerOpenPrice1)==0 or 0.3 < tickerData1['OpenPrice'][i]/self.tickerOpenPrice1[-1] < 2.1 else self.tickerOpenPrice1[-1])
                        self.tickerHighPrice1.append(tickerData1['HighPrice'][i] if len(self.tickerHighPrice1)==0 or 0.3 < tickerData1['HighPrice'][i]/self.tickerHighPrice1[-1] < 2.1 else self.tickerHighPrice1[-1])
                        self.tickerLowPrice1.append(tickerData1['LowPrice'][i] if len(self.tickerLowPrice1)==0 or 0.3 < tickerData1['LowPrice'][i]/self.tickerLowPrice1[-1] < 2.1 else self.tickerLowPrice1[-1])
                for i in range(len(tickerDatesG2)):
                    if tickerDatesG2[i] == date:
                        self.tickerClosePrice2.append(tickerData2['ClosePrice'][i] if len(self.tickerClosePrice2)==0 or 0.3 < tickerData2['ClosePrice'][i]/self.tickerClosePrice2[-1] < 2.1 else self.tickerClosePrice2[-1])
                        self.tickerOpenPrice2.append(tickerData2['OpenPrice'][i] if len(self.tickerOpenPrice2)==0 or 0.3 < tickerData2['OpenPrice'][i]/self.tickerOpenPrice2[-1] < 2.1 else self.tickerOpenPrice2[-1])
                        self.tickerHighPrice2.append(tickerData2['HighPrice'][i] if len(self.tickerHighPrice2)==0 or 0.3 < tickerData2['HighPrice'][i]/self.tickerHighPrice2[-1] < 2.1 else self.tickerHighPrice2[-1])
                        self.tickerLowPrice2.append(tickerData2['LowPrice'][i] if len(self.tickerLowPrice2)==0 or 0.3 < tickerData2['LowPrice'][i]/self.tickerLowPrice2[-1] < 2.1 else self.tickerLowPrice2[-1])

        tickerPriceChangePrc1 = [(self.tickerClosePrice1[i]-self.tickerClosePrice1[i-1])/self.tickerClosePrice1[i-1]*100 if i != 0 and self.tickerClosePrice1[i-1] != 0 else 0 for i in range(len(self.datesG))]
        tickerPriceChangePrc2 = [(self.tickerClosePrice2[i]-self.tickerClosePrice2[i-1])/self.tickerClosePrice2[i-1]*100 if i != 0 and self.tickerClosePrice2[i-1] != 0 else 0 for i in range(len(self.datesG))]

        self.priceChangeDif = [(tickerPriceChangePrc1[i]-tickerPriceChangePrc2[i])/2*50+50 for i in range(len(self.datesG))]

        self.datesJ = [gregorian_to_jalali(date) + '   ' + str((datetime.datetime.strptime(date, "%Y-%m-%d").weekday()+2)%7)+'    ' for date in self.datesG]

        self.ratio = [self.tickerClosePrice1[i-1] / self.tickerClosePrice2[i-1] if self.tickerClosePrice2[i] == 0 else self.tickerClosePrice1[i] / self.tickerClosePrice2[i] for i in range(len(self.datesG))]

        self.ratioMa1 = calculateSma(self.ratio, 10)
        self.ratioMa2 = calculateSma(self.ratio, 20)
        self.ratioRsi = calculateRsi(self.ratio)

        self.ratioMacd = calculateMacd(self.ratio)
        macdAmp = max(abs(max(self.ratioMacd[33:])), abs(min(self.ratioMacd[33:])))
        self.ratioMacd = [item/macdAmp*50+50 for item in self.ratioMacd]
        self.ratioMacdMa = calculateSma(self.ratioMacd, 10)


        


