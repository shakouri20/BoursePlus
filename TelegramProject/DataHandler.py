from cmath import nan
import datetime
from Application.Utility.Indicators.IndicatorService import calculateIchimoko
from Infrastructure.Repository.OfflineDataRepository import offlineData_repo
from Infrastructure.Repository.TickerRepository import ticker_repo
from math import inf, log10
from TelegramProject.DataClasses import pastData

class dataHandler():

    def __init__(self, allowedIDs: list, historySettings: dict) -> None:
        
        if allowedIDs != None:
            self.allowedIDs = allowedIDs
        else:
            self.allowedIDs = ticker_repo().read_list_of_tickers(tickerTypes = [1])['ID']

        self.historySettings = historySettings

        self.get_past_data()
        self.presentData = {}
        self.history = {}
        for key in historySettings:
            self.history[key] = {}

        self.activeIDs = []
    
    def get_past_data(self):

        print('Reading past data ...')
        data = offlineData_repo().read_last_N_offlineData('all', Num=208, IDList= self.allowedIDs, table= 'OfflineData')
        self.pastData = {}

        number = 0
        length = len(data)

        for ID in data:

            number += 1
            print(' ', round(number/length*100, 1), ' ...', end= '\r')

            try:
                monthlyValue = sum(data[ID]['Value'][-30:])/len(data[ID]['Value'][-30:])
                weeklyValue = sum(data[ID]['Value'][-7:])/len(data[ID]['Value'][-7:])

                maxPrice8 = max(data[ID]['HighPrice'][-8:])
                minPrice8 = min(data[ID]['LowPrice'][-8:])
                maxPrice25 = max(data[ID]['HighPrice'][-25:])
                minPrice25 = min(data[ID]['LowPrice'][-25:])

                yesterdayMinPrice = data[ID]['LowPrice'][-1]

                buyPercapitaAvg = 0
                buyPercapitaNumber = 0
                for i in range(-1, -min(20, len(data[ID]['RealBuyValue'])), -1):
                    if data[ID]['RealBuyNumber'][i] != 0:
                        buyPercapitaAvg += log10(data[ID]['RealBuyValue'][i]/data[ID]['RealBuyNumber'][i]/10**7)
                        buyPercapitaNumber += 1
                buyPercapitaAvg = 10**(buyPercapitaAvg/buyPercapitaNumber).real if buyPercapitaNumber!= 0 else nan
                sellPercapitaAvg = 0
                sellPercapitaNumber = 0
                for i in range(-1, -min(20, len(data[ID]['RealSellValue'])), -1):
                    if data[ID]['RealSellNumber'][i] != 0:
                        sellPercapitaAvg += log10(data[ID]['RealSellValue'][i]/data[ID]['RealSellNumber'][i]/10**7)
                        sellPercapitaNumber += 1
                sellPercapitaAvg = 10**(sellPercapitaAvg/sellPercapitaNumber).real if sellPercapitaNumber!= 0 else nan

                ich = calculateIchimoko(data[ID]['HighPrice'], data[ID]['LowPrice'], 9, 26, 52, False, False)
                tenkansen = ich[0][-1]
                kijunsen = ich[1][-1]
                spanA = ich[2][-1]
                spanB = ich[3][-1]
                    
                spanAshifted = ich[2][-26]
                spanBshifted = ich[3][-26]

                ich = calculateIchimoko(data[ID]['HighPrice'], data[ID]['LowPrice'], 104, 208, 52, False, False)
                tenkansenLong = ich[0][-1]
                kijunsenLong  = ich[1][-1]

                self.pastData[ID] = pastData()
                tickerPastData: pastData = self.pastData[ID]

                tickerPastData.MonthlyValue= monthlyValue
                tickerPastData.WeeklyValue= weeklyValue
                
                tickerPastData.Tenkansen = tenkansen
                tickerPastData.Kijunsen = kijunsen
                tickerPastData.SpanA = spanA
                tickerPastData.SpanB = spanB
                tickerPastData.SpanAshifted = spanAshifted
                tickerPastData.SpanBshifted = spanBshifted

                tickerPastData.TenkansenLong = tenkansenLong
                tickerPastData.KijunsenLong = kijunsenLong

                tickerPastData.maxPrice8 = maxPrice8
                tickerPastData.minPrice8 = minPrice8
                tickerPastData.maxPrice25 = maxPrice25
                tickerPastData.minPrice25 = minPrice25
                tickerPastData.yesterdayMinPrice = yesterdayMinPrice

                tickerPastData.buyPercapitaAvg = buyPercapitaAvg
                tickerPastData.sellPercapitaAvg = sellPercapitaAvg
            except:
                pass
        
    def update_data(self, mwData: dict, ctData: dict) -> None:

        self.activeIDs = [ID for ID in mwData if ID in self.allowedIDs]

        now = datetime.datetime.now()
        nowInSeconds = now.hour*3600 + now.minute*60 + now.second
        
        print(str(now.hour)+':'+str(now.minute)+':'+str(now.second), 'activeIDs:', len(self.activeIDs))

        for ID in self.activeIDs:

            if ID not in self.presentData:
                self.presentData[ID] = presentData()

            tickerPresentData: presentData = self.presentData[ID]

            tickerPresentData.Time = nowInSeconds

            if len(mwData[ID]['Constant']) != 0:
                for column in mwData[ID]['Constant']:
                    setattr(tickerPresentData, column, mwData[ID]['Constant'][column])

            if len(mwData[ID]['Variable']) != 0 and\
                mwData[ID]['Variable']['Volume'] != 0 and\
                mwData[ID]['Variable']['MinPrice'] != 0 and\
                    mwData[ID]['Variable']['TodayPrice'] != 0 and\
                        mwData[ID]['Variable']['LastPrice'] != 0:

                for column in mwData[ID]['Variable']:
                    setattr(tickerPresentData, column, mwData[ID]['Variable'][column])

            if len(mwData[ID]['OrdersBoard']) != 0:
                for column in mwData[ID]['OrdersBoard']:
                    setattr(tickerPresentData, column, mwData[ID]['OrdersBoard'][column])

        for ID in self.presentData:

            tickerPresentData: presentData = self.presentData[ID]

            if ID in ctData and tickerPresentData.Volume != None:

                if ctData[ID]['RealBuyVolume'] + ctData[ID]['CorporateBuyVolume'] <= tickerPresentData.Volume*1.2 and tickerPresentData.MinPrice != None:

                    for column in ctData[ID]:
                        setattr(tickerPresentData, column, ctData[ID][column])
                else:
                    print('ct Error', ID)

    def update_history(self, historyType) -> None:

        now = datetime.datetime.now()
        now = now.hour*3600 + now.minute*60 + now.second

        for ID in self.presentData:

            if ID not in self.history[historyType]:
                self.history[historyType][ID] = historyData()

            tickerPresentData: presentData = self.presentData[ID]
            tickerHistoryData: historyData = self.history[historyType][ID]

            historyAttrs = vars(tickerHistoryData)

            for column in historyAttrs:

                if column == 'Time':
                    historyAttrs[column].append(now)

                elif getattr(tickerPresentData, column) != None:
                    historyAttrs[column].append(getattr(tickerPresentData, column))

                if self.historySettings[historyType]['cacheSize'] != None:
                    historyAttrs[column] = historyAttrs[column][-self.historySettings[historyType]['cacheSize']:] 

class presentData:
    def __init__(self) -> None:

        self.Time = None
        self.FirstPrice = None
        self.TodayPrice = None
        self.LastPrice = None
        self.Volume = None
        self.MinPrice = None
        self.MaxPrice = None
        self.YesterdayPrice = None
        self.BaseVolume = None
        self.MaxAllowedPrice = None
        self.MinAllowedPrice = None
        self.ShareNumber = None

        self.SupplyNumber1 = None
        self.DemandNumber1 = None
        self.DemandPrice1 = None
        self.SupplyPrice1 = None
        self.DemandVolume1 = None
        self.SupplyVolume1 = None

        self.SupplyNumber2 = None
        self.DemandNumber2 = None
        self.DemandPrice2 = None
        self.SupplyPrice2 = None
        self.DemandVolume2 = None
        self.SupplyVolume2 = None

        self.SupplyNumber3 = None
        self.DemandNumber3 = None
        self.DemandPrice3 = None
        self.SupplyPrice3 = None
        self.DemandVolume3 = None
        self.SupplyVolume3 = None

        self.SupplyNumber4 = None
        self.DemandNumber4 = None
        self.DemandPrice4 = None
        self.SupplyPrice4 = None
        self.DemandVolume4 = None
        self.SupplyVolume4 = None

        self.SupplyNumber5 = None
        self.DemandNumber5 = None
        self.DemandPrice5 = None
        self.SupplyPrice5 = None
        self.DemandVolume5 = None
        self.SupplyVolume5 = None

        self.RealBuyNumber = None
        self.CorporateBuyNumber = None
        self.RealBuyVolume = None
        self.CorporateBuyVolume = None
        self.RealSellNumber = None
        self.CorporateSellNumber = None
        self.RealSellVolume = None
        self.CorporateSellVolume = None

class historyData:
    def __init__(self) -> None:

        self.Time = []
        self.LastPrice = []
        self.Volume = [] 
        self.MinPrice = [] 
        self.MaxPrice = [] 
        self.RealBuyVolume = []
        self.RealSellVolume = []
        self.RealBuyNumber = []
        self.RealSellNumber = []
        self.CorporateBuyVolume = []
        self.CorporateSellVolume = []
        self.CorporateBuyNumber = []
        self.CorporateSellNumber = []
        self.DemandVolume1 = []
        self.DemandPrice1 = []
        self.DemandNumber1 = []
        self.SupplyVolume1 = []
        self.SupplyPrice1 = []
        self.SupplyNumber1 = []



    # def lastPricePrc(self, historyType, allowedIDs= None, num = 0) -> dict:
    #     lastPrice = self.lastPrice(historyType, allowedIDs, num)
    #     return {ID: [round((lastPrice[ID][i]-self.presentData[ID]['YesterdayPrice'])/self.presentData[ID]['YesterdayPrice']*100, 2) for i in range(len(lastPrice[ID]))] for ID in lastPrice}

    # def realPower(self, historyType, allowedIDs= None, num = 0) -> dict:
        
    #     realValues = self.realValues(decNum, num, allowedIDs)
    #     realBuyVolume = realValues['RealBuyVolume']
    #     realBuyNumber = realValues['RealBuyNumber']
    #     realSellVolume = realValues['RealSellVolume']
    #     realSellNumber = realValues['RealSellNumber']
    #     realPower ={}

    #     IDs = allowedIDs if allowedIDs != None else self.history[historyType]
    #     for ID in IDs:
    #         realPower[ID] = []
    #         for i in range(len(realBuyVolume[ID])):
    #             try:
    #                 realPower[ID].append((realBuyVolume[ID][i]/realBuyNumber[ID][i])/(realSellVolume[ID][i]/realSellNumber[ID][i]))
    #             except:
    #                 realPower[ID].append(1)

    #     return realPower

    # def demandValue(self, historyType, allowedIDs= None, num = 0) -> dict:
        
    #     row1 = self.row1(decNum, num, allowedIDs)
    #     row2 = self.row2(decNum, num, allowedIDs)
    #     row3 = self.row3(decNum, num, allowedIDs)
    #     row4 = self.row4(decNum, num, allowedIDs)
    #     row5 = self.row5(decNum, num, allowedIDs)

    #     demandValue = {}

    #     IDs = allowedIDs if allowedIDs != None else self.history[historyType]
    #     for ID in IDs:

    #         length = len(row1['DemandVolume1'][ID])

    #         value1 = [row1['DemandVolume1'][ID][i] * row1['DemandPrice1'][ID][i] for i in range(length)]
    #         value2 = [row2['DemandVolume2'][ID][i] * row2['DemandPrice2'][ID][i] for i in range(length)]
    #         value3 = [row3['DemandVolume3'][ID][i] * row3['DemandPrice3'][ID][i] for i in range(length)]
    #         value4 = [row4['DemandVolume4'][ID][i] * row4['DemandPrice4'][ID][i] for i in range(length)]
    #         value5 = [row5['DemandVolume5'][ID][i] * row5['DemandPrice5'][ID][i] for i in range(length)]

    #         demandValuesZip = zip(value1, value2, value3, value4, value5)
    #         demandValue[ID] = [(v1 + v2 + v3 + v4 + v5)/10000000 for (v1, v2, v3, v4, v5) in demandValuesZip]

    #     return demandValue

    # def supplyValue(self, historyType, allowedIDs= None, num = 0) -> dict:
        
    #     row1 = self.row1(decNum, num, allowedIDs)
    #     row2 = self.row2(decNum, num, allowedIDs)
    #     row3 = self.row3(decNum, num, allowedIDs)
    #     row4 = self.row4(decNum, num, allowedIDs)
    #     row5 = self.row5(decNum, num, allowedIDs)

    #     supplyValue = {}

    #     IDs = allowedIDs if allowedIDs != None else self.history[historyType]
    #     for ID in IDs:

    #         length = len(row1['SupplyVolume1'][ID])

    #         value1 = [row1['SupplyVolume1'][ID][i] * row1['SupplyPrice1'][ID][i] for i in range(length)]
    #         value2 = [row2['SupplyVolume2'][ID][i] * row2['SupplyPrice2'][ID][i] for i in range(length)]
    #         value3 = [row3['SupplyVolume3'][ID][i] * row3['SupplyPrice3'][ID][i] for i in range(length)]
    #         value4 = [row4['SupplyVolume4'][ID][i] * row4['SupplyPrice4'][ID][i] for i in range(length)]
    #         value5 = [row5['SupplyVolume5'][ID][i] * row5['SupplyPrice5'][ID][i] for i in range(length)]

    #         supplyValuesZip = zip(value1, value2, value3, value4, value5)
    #         supplyValue[ID] = [(v1 + v2 + v3 + v4 + v5)/10000000 for (v1, v2, v3, v4, v5) in supplyValuesZip]

    #     return supplyValue
                
    # def demandPerCapita(self, historyType, allowedIDs= None, num = 0) -> dict:
        
    #     number1 = self.row1(decNum, num, allowedIDs)['DemandNumber1']
    #     number2 = self.row2(decNum, num, allowedIDs)['DemandNumber2']
    #     number3 = self.row3(decNum, num, allowedIDs)['DemandNumber3']
    #     number4 = self.row4(decNum, num, allowedIDs)['DemandNumber4']
    #     number5 = self.row5(decNum, num, allowedIDs)['DemandNumber5']

    #     demandValue = self.demandValue(decNum, num, allowedIDs)

    #     demandPerCapita = {}

    #     IDs = allowedIDs if allowedIDs != None else self.history[historyType]
    #     for ID in IDs:

    #         totalNumber = [number1[ID][i]+number2[ID][i]+number3[ID][i]+number4[ID][i]+number5[ID][i] for i in range(len(number1[ID]))]
    #         demandPerCapita[ID] = []

    #         for i in range(len(number1[ID])):
    #             totalNumber = number1[ID][i]+number2[ID][i]+number3[ID][i]+number4[ID][i]+number5[ID][i]
    #             try:
    #                 demandPerCapita[ID].append(demandValue[ID][i]/totalNumber)
    #             except:
    #                 demandPerCapita[ID].append(0)
    #     return demandPerCapita

    # def supplyPerCapita(self, historyType, allowedIDs= None, num = 0) -> dict:
        
    #     number1 = self.row1(decNum, num, allowedIDs)['SupplyNumber1']
    #     number2 = self.row2(decNum, num, allowedIDs)['SupplyNumber2']
    #     number3 = self.row3(decNum, num, allowedIDs)['SupplyNumber3']
    #     number4 = self.row4(decNum, num, allowedIDs)['SupplyNumber4']
    #     number5 = self.row5(decNum, num, allowedIDs)['SupplyNumber5']

    #     supplyValue = self.supplyValue(decNum, num, allowedIDs)

    #     supplyPerCapita = {}

    #     IDs = allowedIDs if allowedIDs != None else self.history[historyType]
    #     for ID in IDs:

    #         totalNumber = [number1[ID][i]+number2[ID][i]+number3[ID][i]+number4[ID][i]+number5[ID][i] for i in range(len(number1[ID]))]
    #         supplyPerCapita[ID] = []

    #         for i in range(len(number1[ID])):
    #             totalNumber = number1[ID][i]+number2[ID][i]+number3[ID][i]+number4[ID][i]+number5[ID][i]
    #             try:
    #                 supplyPerCapita[ID].append(supplyValue[ID][i]/totalNumber)
    #             except:
    #                 supplyPerCapita[ID].append(0)
    #     return supplyPerCapita

    # # Diff
    # def volumeDif(self, historyType, num = 0, length = 1, allowedIDs) -> dict:
        
    #     if num == 0:
    #         requieredLength = 0
    #     else:
    #         requieredLength = num+length

    #     volume = self.volume(decNum, requieredLength, allowedIDs)
    #     volumeDif = {}

    #     IDs = allowedIDs if allowedIDs != None else self.history[historyType]
    #     for ID in IDs:
    #         volumeDif[ID] = []
    #         for i in range(-1, -len(volume[ID])-1, -1):
    #             if abs(i) + length <= len(volume[ID]):   
    #                 thisVolumeDif = max(volume[ID][i]-volume[ID][i-length], 0)
    #             else:
    #                 thisVolumeDif = max(volume[ID][i], 0)
    #             volumeDif[ID].append(thisVolumeDif)
    #         if num == 0:
    #             volumeDif[ID] = volumeDif[ID][::-1]
    #         else:
    #             volumeDif[ID] = volumeDif[ID][::-1][-num:]

    #     return volumeDif

    # def clientVolumeDif(self, historyType, num = 0, length = 1, allowedIDs) -> dict:
        
    #     if num == 0:
    #         requieredLength = 0
    #     else:
    #         requieredLength = num+length

    #     realValues = self.realValues(decNum, requieredLength, allowedIDs)
    #     realBuyVolume = realValues['RealBuyVolume']
    #     corporateValues = self.corporateValues(decNum, requieredLength, allowedIDs)
    #     corporateBuyVolume = corporateValues['CorporateBuyVolume']
    #     clientVolumeDif = {}

    #     IDs = allowedIDs if allowedIDs != None else self.history[historyType]
    #     for ID in IDs:
    #         clientVolumeDif[ID] = []
    #         for i in range(-1, -len(realBuyVolume[ID])-1, -1):
    #             if abs(i) + length <= len(realBuyVolume[ID]):   
    #                 thisVolumeDif = max((realBuyVolume[ID][i]+corporateBuyVolume[ID][i])-(realBuyVolume[ID][i-length]+corporateBuyVolume[ID][i-length]), 0)
    #             else:
    #                 thisVolumeDif = max(realBuyVolume[ID][i]+corporateBuyVolume[ID][i], 0)
    #             clientVolumeDif[ID].append(thisVolumeDif)
    #         if num == 0:
    #             clientVolumeDif[ID] = clientVolumeDif[ID][::-1]
    #         else:
    #             clientVolumeDif[ID] = clientVolumeDif[ID][::-1][-num:]

    #     return clientVolumeDif

    # def realPowerDif(self, historyType, num = 0, length = 1, allowedIDs) -> dict:
        
    #     if num == 0:
    #         requieredLength = 0
    #     else:
    #         requieredLength = num+length

    #     realValues = self.realValues(decNum, requieredLength, allowedIDs)
    #     realBuyVolume = realValues['RealBuyVolume']
    #     realBuyNumber = realValues['RealBuyNumber']
    #     realSellVolume = realValues['RealSellVolume']
    #     realSellNumber = realValues['RealSellNumber']
    #     realPowerDif ={}

    #     IDs = allowedIDs if allowedIDs != None else self.history[historyType]
    #     for ID in IDs:
    #         realPowerDif[ID] = []
    #         for i in range(-1, -len(realBuyVolume[ID])-1, -1):
    #             try:
    #                 if abs(i) + length <= len(realBuyVolume[ID]):   
    #                     thisRealPowerDif = ((realBuyVolume[ID][i]-realBuyVolume[ID][i-length])/(realBuyNumber[ID][i]-realBuyNumber[ID][i-length]))/\
    #                     ((realSellVolume[ID][i]-realSellVolume[ID][i-length])/(realSellNumber[ID][i]-realSellNumber[ID][i-length]))
    #                 else:
    #                     thisRealPowerDif = (realBuyVolume[ID][i]/realBuyNumber[ID][i])/(realSellVolume[ID][i]/realSellNumber[ID][i])
    #             except:
    #                 thisRealPowerDif = 1
    #             if thisRealPowerDif <= 0:
    #                 thisRealPowerDif = 1
    #             realPowerDif[ID].append(thisRealPowerDif)
    #         if num == 0:
    #             realPowerDif[ID] = realPowerDif[ID][::-1]
    #         else:
    #             realPowerDif[ID] = realPowerDif[ID][::-1][-num:]

    #     return realPowerDif

    # def rpvp(self, historyType, num = 0, length = 1, allowedIDs) -> dict:
        

    #     VolumeDif = self.clientVolumeDif(decNum, num, length, allowedIDs)
    #     RealPowerDif = self.realPowerDif(decNum, num, length, allowedIDs)

    #     IDs = allowedIDs if allowedIDs != None else self.history[historyType]
    #     return {ID: [VolumeDif[ID][i]*log10(RealPowerDif[ID][i]) for i in range(len(VolumeDif[ID]))] for ID in IDs}

    # def perCapitaBuyDif(self, historyType, num = 0, length = 1, allowedIDs) -> dict:
        
    #     if num == 0:
    #         requieredLength = 0
    #     else:
    #         requieredLength = num+length

    #     lastPrice = self.lastPrice(decNum, requieredLength, allowedIDs)
    #     realValues = self.realValues(decNum, requieredLength, allowedIDs)
    #     realBuyVolume = realValues['RealBuyVolume']
    #     realBuyNumber = realValues['RealBuyNumber']
    #     perCapitaBuyDif = {}

    #     IDs = allowedIDs if allowedIDs != None else self.history[historyType]
    #     for ID in IDs:
    #         perCapitaBuyDif[ID] = []
    #         for i in range(-1, -len(realBuyVolume[ID])-1, -1):
    #             try:
    #                 if abs(i) + length <= len(realBuyVolume[ID]):   
    #                     thisPerCapitaBuyDif = max(int((realBuyVolume[ID][i]-realBuyVolume[ID][i-length])/(realBuyNumber[ID][i]-realBuyNumber[ID][i-length]) * lastPrice[ID][i] / 10**7), 0)
    #                 else:
    #                     thisPerCapitaBuyDif = max(int((realBuyVolume[ID][i]/realBuyNumber[ID][i]) * lastPrice[ID][i] / 10**7), 0)
    #             except:
    #                 thisPerCapitaBuyDif = 0
    #             perCapitaBuyDif[ID].append(thisPerCapitaBuyDif)
    #         if num == 0:
    #             perCapitaBuyDif[ID] = perCapitaBuyDif[ID][::-1]
    #         else:
    #             perCapitaBuyDif[ID] = perCapitaBuyDif[ID][::-1][-num:]

    #     return perCapitaBuyDif

    # def perCapitaSellDif(self, historyType, num = 0, length = 1, allowedIDs) -> dict:
        
    #     if num == 0:
    #         requieredLength = 0
    #     else:
    #         requieredLength = num+length

    #     lastPrice = self.lastPrice(decNum, requieredLength, allowedIDs)
    #     realValues = self.realValues(decNum, requieredLength, allowedIDs)
    #     realSellVolume = realValues['RealSellVolume']
    #     realSellNumber = realValues['RealSellNumber']
    #     perCapitaSellDif = {}

    #     IDs = allowedIDs if allowedIDs != None else self.history[historyType]
    #     for ID in IDs:
    #         perCapitaSellDif[ID] = []
    #         for i in range(-1, -len(realSellVolume[ID])-1, -1):
    #             try:
    #                 if abs(i) + length <= len(realSellVolume[ID]):   
    #                     thisPerCapitaSellDif = max(int((realSellVolume[ID][i]-realSellVolume[ID][i-length])/(realSellNumber[ID][i]-realSellNumber[ID][i-length]) * lastPrice[ID][i] / 10**7), 0)
    #                 else:
    #                     thisPerCapitaSellDif = max(int((realSellVolume[ID][i]/realSellNumber[ID][i]) * lastPrice[ID][i] / 10**7), 0)
    #             except:
    #                 thisPerCapitaSellDif = 0
    #             perCapitaSellDif[ID].append(thisPerCapitaSellDif)
    #         if num == 0:
    #             perCapitaSellDif[ID] = perCapitaSellDif[ID][::-1]
    #         else:
    #             perCapitaSellDif[ID] = perCapitaSellDif[ID][::-1][-num:]

    #     return perCapitaSellDif
