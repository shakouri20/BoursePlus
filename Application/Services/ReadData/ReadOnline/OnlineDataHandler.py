from datetime import datetime, timedelta
from tkinter import E
from Domain.ImportEnums import *
from Infrastructure.Repository.TickerRepository import ticker_repo as tr
from math import inf, log10


class onlineDataHandler():

    def __init__(self, allowedIDs: list, historySettings: dict = {'10S': 60}) -> None:
        
        self.historySettings = historySettings

        self.presentData = {}

        self.history = {}
        for key in historySettings:
            self.history[key] = {}

        if allowedIDs != None:
            self.allowedIDs = allowedIDs
        else:
            self.allowedIDs = tr().read_list_of_tickers(tickerTypes = [1])['ID']

        self.activeIDs = []
  
    def update_data(self, mwData: dict, ctData: dict) -> None:

        self.activeIDs = list(mwData.keys())

        for ID in self.activeIDs:

            if ID in self.allowedIDs:

                if ID not in self.presentData:
                    self.presentData[ID] = {}

                if len(mwData[ID]['Constant']) != 0:
                    for column in mwData[ID]['Constant']:
                        self.presentData[ID][column] = mwData[ID]['Constant'][column]

                if len(mwData[ID]['Variable']) != 0 and\
                    mwData[ID]['Variable'][onlineColumns.Volume.value] != 0 and\
                    mwData[ID]['Variable'][onlineColumns.MinPrice.value] != 0 and\
                        mwData[ID]['Variable'][onlineColumns.TodayPrice.value] != 0 and\
                            mwData[ID]['Variable'][onlineColumns.LastPrice.value] != 0:

                    for column in mwData[ID]['Variable']:
                        self.presentData[ID][column] = mwData[ID]['Variable'][column]

                if len(mwData[ID]['OrdersBoard']) != 0:
                    for column in mwData[ID]['OrdersBoard']:
                        self.presentData[ID][column] = mwData[ID]['OrdersBoard'][column]

        for ID in self.allowedIDs:

            if ID in ctData and ID in self.presentData and onlineColumns.Volume.value in self.presentData[ID]:

                if ctData[ID][onlineColumns.RealBuyVolume.value]+ctData[ID][onlineColumns.CorporateBuyVolume.value] <= self.presentData[ID][onlineColumns.Volume.value]*1.2 and\
                    self.presentData[ID][onlineColumns.MinPrice.value] != 0 and self.presentData[ID][onlineColumns.Volume.value] != 0:

                    for column in ctData[ID]:
                        self.presentData[ID][column] = ctData[ID][column]

    def update_history(self, historyType= '10S') -> None:

        now = datetime.now()
        now = now.hour*3600 + now.minute*60 + now.second

        for ID in self.presentData:

            if ID not in self.history[historyType]:
                self.history[historyType][ID] = {}

            if onlineColumns.Time.value not in self.history[historyType][ID]:
                self.history[historyType][ID][onlineColumns.Time.value] = [now]
            else:
                self.history[historyType][ID][onlineColumns.Time.value].append(now)
                if self.historySettings[historyType] != None:
                    self.history[historyType][ID][onlineColumns.Time.value] = self.history[historyType][ID][onlineColumns.Time.value][-self.historySettings[historyType]:] 

            for column in self.presentData[ID]:
                
                if column in [onlineColumns.LastPrice.value,
                                onlineColumns.Volume.value, 
                                onlineColumns.MinPrice.value, 
                                onlineColumns.RealBuyVolume.value,
                                onlineColumns.RealSellVolume.value,
                                onlineColumns.RealBuyNumber.value,
                                onlineColumns.RealSellNumber.value,
                                onlineColumns.CorporateBuyVolume.value,
                                onlineColumns.CorporateSellVolume.value,
                                onlineColumns.CorporateBuyNumber.value,
                                onlineColumns.CorporateSellNumber.value,
                                onlineColumns.DemandVolume1.value,
                                onlineColumns.DemandPrice1.value,
                                onlineColumns.DemandNumber1.value,
                                onlineColumns.SupplyVolume1.value,
                                onlineColumns.SupplyPrice1.value,
                                onlineColumns.SupplyNumber1.value]:

                    if column not in self.history[historyType][ID]:
                        self.history[historyType][ID][column] = [self.presentData[ID][column]]

                    else:
                        self.history[historyType][ID][column].append(self.presentData[ID][column])
                        if self.historySettings[historyType] != None:
                            self.history[historyType][ID][column] = self.history[historyType][ID][column][-self.historySettings[historyType]:] 

    def check_allowedIDs(self, allowedIDs: list) -> None:

        if allowedIDs == None:
            newallowedIDs = list(self.history.keys())
        else:
            tempallowedIDs = allowedIDs.copy()
            for ID in tempallowedIDs:
                if ID not in self.history:
                    allowedIDs.remove(ID)
            newallowedIDs = allowedIDs
        return newallowedIDs

    def time(self, decNum = 1, num = 0, allowedIDs: list= None) -> dict:
        allowedIDs = self.check_allowedIDs(allowedIDs)
        if num == 0:
            data = {ID: self.history[ID][onlineColumns.Time.value][::-1][::decNum][::-1] for ID in allowedIDs}
        else:
            data = {ID: self.history[ID][onlineColumns.Time.value][:-decNum*num-1:-1][::decNum][:num][::-1] for ID in allowedIDs}
        return data

    def todayPrice(self, decNum = 1, num = 0, allowedIDs: list= None) -> dict:
        allowedIDs = self.check_allowedIDs(allowedIDs)
        if num == 0:
            data = {ID: self.history[ID][onlineColumns.TodayPrice.value][::-1][::decNum][::-1] for ID in allowedIDs}
        else:
            data = {ID: self.history[ID][onlineColumns.TodayPrice.value][:-decNum*num-1:-1][::decNum][:num][::-1] for ID in allowedIDs}
        return data

    def lastPrice(self, decNum = 1, num = 0, allowedIDs: list= None) -> dict:
        allowedIDs = self.check_allowedIDs(allowedIDs)
        if num == 0:
            data = {ID: self.history[ID][onlineColumns.LastPrice.value][::-1][::decNum][::-1] for ID in allowedIDs}
        else:
            data = {ID: self.history[ID][onlineColumns.LastPrice.value][:-decNum*num-1:-1][::decNum][:num][::-1] for ID in allowedIDs}
        return data
    
    def number(self, decNum = 1, num = 0, allowedIDs: list= None) -> dict:
        allowedIDs = self.check_allowedIDs(allowedIDs)
        if num == 0:
            data = {ID: self.history[ID][onlineColumns.Number.value][::-1][::decNum][::-1] for ID in allowedIDs}
        else:
            data = {ID: self.history[ID][onlineColumns.Number.value][:-decNum*num-1:-1][::decNum][:num][::-1] for ID in allowedIDs}
        return data

    def volume(self, decNum = 1, num = 0, allowedIDs: list= None) -> dict:
        allowedIDs = self.check_allowedIDs(allowedIDs)
        if num == 0:
            data = {ID: self.history[ID][onlineColumns.Volume.value][::-1][::decNum][::-1] for ID in allowedIDs}
        else:
            data = {ID: self.history[ID][onlineColumns.Volume.value][:-decNum*num-1:-1][::decNum][:num][::-1] for ID in allowedIDs}
        return data

    def minPrice(self, decNum = 1, num = 0, allowedIDs: list= None) -> dict:
        allowedIDs = self.check_allowedIDs(allowedIDs)
        if num == 0:
            data = {ID: self.history[ID][onlineColumns.MinPrice.value][::-1][::decNum][::-1] for ID in allowedIDs}
        else:
            data = {ID: self.history[ID][onlineColumns.MinPrice.value][:-decNum*num-1:-1][::decNum][:num][::-1] for ID in allowedIDs}
        return data

    def maxPrice(self, decNum = 1, num = 0, allowedIDs: list= None) -> dict:
        allowedIDs = self.check_allowedIDs(allowedIDs)
        if num == 0:
            data = {ID: self.history[ID][onlineColumns.MaxPrice.value][::-1][::decNum][::-1] for ID in allowedIDs}
        else:
            data = {ID: self.history[ID][onlineColumns.MaxPrice.value][:-decNum*num-1:-1][::decNum][:num][::-1] for ID in allowedIDs}
        return data

    def yesterdayPrice(self, allowedIDs: list= None) -> dict:
        allowedIDs = self.check_allowedIDs(allowedIDs)
        return {ID: self.history[ID][onlineColumns.YesterdayPrice.value] for ID in allowedIDs}

    def minAllowedPrice(self, allowedIDs: list= None) -> dict:
        allowedIDs = self.check_allowedIDs(allowedIDs)
        return {ID: self.history[ID][onlineColumns.MinAllowedPrice.value] for ID in allowedIDs}

    def maxAllowedPrice(self, allowedIDs: list= None) -> dict:
        allowedIDs = self.check_allowedIDs(allowedIDs)
        return {ID: self.history[ID][onlineColumns.MaxAllowedPrice.value] for ID in allowedIDs}

    def realValues(self, decNum = 1, num = 0, allowedIDs: list= None) -> dict:
        allowedIDs = self.check_allowedIDs(allowedIDs)
        if num == 0:
            data = {onlineColumns.RealBuyNumber.value: {ID: self.history[ID][onlineColumns.RealBuyNumber.value][::-1][::decNum][::-1] for ID in allowedIDs},
                    onlineColumns.RealBuyVolume.value: {ID: self.history[ID][onlineColumns.RealBuyVolume.value][::-1][::decNum][::-1] for ID in allowedIDs},
                    onlineColumns.RealSellNumber.value: {ID: self.history[ID][onlineColumns.RealSellNumber.value][::-1][::decNum][::-1] for ID in allowedIDs},
                    onlineColumns.RealSellVolume.value: {ID: self.history[ID][onlineColumns.RealSellVolume.value][::-1][::decNum][::-1] for ID in allowedIDs}}
        else:
            data = {onlineColumns.RealBuyNumber.value: {ID: self.history[ID][onlineColumns.RealBuyNumber.value][:-decNum*num-1:-1][::decNum][:num][::-1] for ID in self.history},
                onlineColumns.RealBuyVolume.value: {ID: self.history[ID][onlineColumns.RealBuyVolume.value][:-decNum*num-1:-1][::decNum][:num][::-1] for ID in self.history},
                onlineColumns.RealSellNumber.value: {ID: self.history[ID][onlineColumns.RealSellNumber.value][:-decNum*num-1:-1][::decNum][:num][::-1] for ID in self.history},
                onlineColumns.RealSellVolume.value: {ID: self.history[ID][onlineColumns.RealSellVolume.value][:-decNum*num-1:-1][::decNum][:num][::-1] for ID in self.history}}
        return data

    def corporateValues(self, decNum = 1, num = 0, allowedIDs: list= None) -> dict:
        allowedIDs = self.check_allowedIDs(allowedIDs)
        if num == 0:
            data = {onlineColumns.CorporateBuyNumber.value: {ID: self.history[ID][onlineColumns.CorporateBuyNumber.value][::-1][::decNum][::-1] for ID in allowedIDs},
                onlineColumns.CorporateBuyVolume.value: {ID: self.history[ID][onlineColumns.CorporateBuyVolume.value][::-1][::decNum][::-1] for ID in allowedIDs},
                onlineColumns.CorporateSellNumber.value: {ID: self.history[ID][onlineColumns.CorporateSellNumber.value][::-1][::decNum][::-1] for ID in allowedIDs},
                onlineColumns.CorporateSellVolume.value: {ID: self.history[ID][onlineColumns.CorporateSellVolume.value][::-1][::decNum][::-1] for ID in allowedIDs}}
        else:
            data = {onlineColumns.CorporateBuyNumber.value: {ID: self.history[ID][onlineColumns.CorporateBuyNumber.value][:-decNum*num-1:-1][::decNum][:num][::-1] for ID in allowedIDs},
                onlineColumns.CorporateBuyVolume.value: {ID: self.history[ID][onlineColumns.CorporateBuyVolume.value][:-decNum*num-1:-1][::decNum][:num][::-1] for ID in allowedIDs},
                onlineColumns.CorporateSellNumber.value: {ID: self.history[ID][onlineColumns.CorporateSellNumber.value][:-decNum*num-1:-1][::decNum][:num][::-1] for ID in allowedIDs},
                onlineColumns.CorporateSellVolume.value: {ID: self.history[ID][onlineColumns.CorporateSellVolume.value][:-decNum*num-1:-1][::decNum][:num][::-1] for ID in allowedIDs}}
        return data

    def row1(self, decNum = 1, num = 0, allowedIDs: list= None) -> dict:
        allowedIDs = self.check_allowedIDs(allowedIDs)

        if num == 0:
            row1 = {onlineColumns.SupplyNumber1.value: {ID: self.history[ID][onlineColumns.SupplyNumber1.value][::-1][::decNum][::-1] for ID in allowedIDs},
                    onlineColumns.SupplyVolume1.value: {ID: self.history[ID][onlineColumns.SupplyVolume1.value][::-1][::decNum][::-1] for ID in allowedIDs},
                    onlineColumns.SupplyPrice1.value: {ID: self.history[ID][onlineColumns.SupplyPrice1.value][::-1][::decNum][::-1] for ID in allowedIDs},
                    onlineColumns.DemandPrice1.value: {ID: self.history[ID][onlineColumns.DemandPrice1.value][::-1][::decNum][::-1] for ID in allowedIDs},
                    onlineColumns.DemandVolume1.value: {ID: self.history[ID][onlineColumns.DemandVolume1.value][::-1][::decNum][::-1] for ID in allowedIDs},
                    onlineColumns.DemandNumber1.value: {ID: self.history[ID][onlineColumns.DemandNumber1.value][::-1][::decNum][::-1] for ID in allowedIDs}}
        else:
            row1 = {onlineColumns.SupplyNumber1.value: {ID: self.history[ID][onlineColumns.SupplyNumber1.value][:-decNum*num-1:-1][::decNum][:num][::-1] for ID in allowedIDs},
                onlineColumns.SupplyVolume1.value: {ID: self.history[ID][onlineColumns.SupplyVolume1.value][:-decNum*num-1:-1][::decNum][:num][::-1] for ID in allowedIDs},
                onlineColumns.SupplyPrice1.value: {ID: self.history[ID][onlineColumns.SupplyPrice1.value][:-decNum*num-1:-1][::decNum][:num][::-1] for ID in allowedIDs},
                onlineColumns.DemandPrice1.value: {ID: self.history[ID][onlineColumns.DemandPrice1.value][:-decNum*num-1:-1][::decNum][:num][::-1] for ID in allowedIDs},
                onlineColumns.DemandVolume1.value: {ID: self.history[ID][onlineColumns.DemandVolume1.value][:-decNum*num-1:-1][::decNum][:num][::-1] for ID in allowedIDs},
                onlineColumns.DemandNumber1.value: {ID: self.history[ID][onlineColumns.DemandNumber1.value][:-decNum*num-1:-1][::decNum][:num][::-1] for ID in allowedIDs}}

        for ID in allowedIDs:
            for i in range(len(row1[onlineColumns.SupplyPrice1.value][ID])):
                if row1[onlineColumns.SupplyPrice1.value][ID][i] > self.history[ID][onlineColumns.MaxAllowedPrice.value]:
                    row1[onlineColumns.SupplyPrice1.value][ID][i] = self.history[ID][onlineColumns.MaxAllowedPrice.value]
                    row1[onlineColumns.SupplyVolume1.value][ID][i] = 0
                    row1[onlineColumns.SupplyNumber1.value][ID][i] = 0
                if row1[onlineColumns.DemandPrice1.value][ID][i] < self.history[ID][onlineColumns.MinAllowedPrice.value]:
                    row1[onlineColumns.DemandPrice1.value][ID][i] = self.history[ID][onlineColumns.MinAllowedPrice.value]
                    row1[onlineColumns.DemandVolume1.value][ID][i] = 0
                    row1[onlineColumns.DemandNumber1.value][ID][i] = 0
        return row1

    def row2(self, decNum = 1, num = 0, allowedIDs: list= None) -> dict:
        allowedIDs = self.check_allowedIDs(allowedIDs)

        if num == 0:
            row2 = {onlineColumns.SupplyNumber2.value: {ID: self.history[ID][onlineColumns.SupplyNumber2.value][::-1][::decNum][::-1] for ID in allowedIDs},
                    onlineColumns.SupplyVolume2.value: {ID: self.history[ID][onlineColumns.SupplyVolume2.value][::-1][::decNum][::-1] for ID in allowedIDs},
                    onlineColumns.SupplyPrice2.value: {ID: self.history[ID][onlineColumns.SupplyPrice2.value][::-1][::decNum][::-1] for ID in allowedIDs},
                    onlineColumns.DemandPrice2.value: {ID: self.history[ID][onlineColumns.DemandPrice2.value][::-1][::decNum][::-1] for ID in allowedIDs},
                    onlineColumns.DemandVolume2.value: {ID: self.history[ID][onlineColumns.DemandVolume2.value][::-1][::decNum][::-1] for ID in allowedIDs},
                    onlineColumns.DemandNumber2.value: {ID: self.history[ID][onlineColumns.DemandNumber2.value][::-1][::decNum][::-1] for ID in allowedIDs}}
        else:
            row2 = {onlineColumns.SupplyNumber2.value: {ID: self.history[ID][onlineColumns.SupplyNumber2.value][:-decNum*num-1:-1][::decNum][:num][::-1] for ID in allowedIDs},
                onlineColumns.SupplyVolume2.value: {ID: self.history[ID][onlineColumns.SupplyVolume2.value][:-decNum*num-1:-1][::decNum][:num][::-1] for ID in allowedIDs},
                onlineColumns.SupplyPrice2.value: {ID: self.history[ID][onlineColumns.SupplyPrice2.value][:-decNum*num-1:-1][::decNum][:num][::-1] for ID in allowedIDs},
                onlineColumns.DemandPrice2.value: {ID: self.history[ID][onlineColumns.DemandPrice2.value][:-decNum*num-1:-1][::decNum][:num][::-1] for ID in allowedIDs},
                onlineColumns.DemandVolume2.value: {ID: self.history[ID][onlineColumns.DemandVolume2.value][:-decNum*num-1:-1][::decNum][:num][::-1] for ID in allowedIDs},
                onlineColumns.DemandNumber2.value: {ID: self.history[ID][onlineColumns.DemandNumber2.value][:-decNum*num-1:-1][::decNum][:num][::-1] for ID in allowedIDs}}

        for ID in allowedIDs:
            for i in range(len(row2[onlineColumns.SupplyPrice2.value][ID])):
                if row2[onlineColumns.SupplyPrice2.value][ID][i] > self.history[ID][onlineColumns.MaxAllowedPrice.value]:
                    row2[onlineColumns.SupplyPrice2.value][ID][i] = self.history[ID][onlineColumns.MaxAllowedPrice.value]
                    row2[onlineColumns.SupplyVolume2.value][ID][i] = 0
                    row2[onlineColumns.SupplyNumber2.value][ID][i] = 0
                if row2[onlineColumns.DemandPrice2.value][ID][i] < self.history[ID][onlineColumns.MinAllowedPrice.value]:
                    row2[onlineColumns.SupplyPrice2.value][ID][i] = self.history[ID][onlineColumns.MinAllowedPrice.value]
                    row2[onlineColumns.DemandVolume2.value][ID][i] = 0
                    row2[onlineColumns.DemandNumber2.value][ID][i] = 0
        return row2

    def row3(self, decNum = 1, num = 0, allowedIDs: list= None) -> dict:
        allowedIDs = self.check_allowedIDs(allowedIDs)

        if num == 0:
            row3 = {onlineColumns.SupplyNumber3.value: {ID: self.history[ID][onlineColumns.SupplyNumber3.value][::-1][::decNum][::-1] for ID in allowedIDs},
                    onlineColumns.SupplyVolume3.value: {ID: self.history[ID][onlineColumns.SupplyVolume3.value][::-1][::decNum][::-1] for ID in allowedIDs},
                    onlineColumns.SupplyPrice3.value: {ID: self.history[ID][onlineColumns.SupplyPrice3.value][::-1][::decNum][::-1] for ID in allowedIDs},
                    onlineColumns.DemandPrice3.value: {ID: self.history[ID][onlineColumns.DemandPrice3.value][::-1][::decNum][::-1] for ID in allowedIDs},
                    onlineColumns.DemandVolume3.value: {ID: self.history[ID][onlineColumns.DemandVolume3.value][::-1][::decNum][::-1] for ID in allowedIDs},
                    onlineColumns.DemandNumber3.value: {ID: self.history[ID][onlineColumns.DemandNumber3.value][::-1][::decNum][::-1] for ID in allowedIDs}}
        else:
            row3 = {onlineColumns.SupplyNumber3.value: {ID: self.history[ID][onlineColumns.SupplyNumber3.value][:-decNum*num-1:-1][::decNum][:num][::-1] for ID in allowedIDs},
                onlineColumns.SupplyVolume3.value: {ID: self.history[ID][onlineColumns.SupplyVolume3.value][:-decNum*num-1:-1][::decNum][:num][::-1] for ID in allowedIDs},
                onlineColumns.SupplyPrice3.value: {ID: self.history[ID][onlineColumns.SupplyPrice3.value][:-decNum*num-1:-1][::decNum][:num][::-1] for ID in allowedIDs},
                onlineColumns.DemandPrice3.value: {ID: self.history[ID][onlineColumns.DemandPrice3.value][:-decNum*num-1:-1][::decNum][:num][::-1] for ID in allowedIDs},
                onlineColumns.DemandVolume3.value: {ID: self.history[ID][onlineColumns.DemandVolume3.value][:-decNum*num-1:-1][::decNum][:num][::-1] for ID in allowedIDs},
                onlineColumns.DemandNumber3.value: {ID: self.history[ID][onlineColumns.DemandNumber3.value][:-decNum*num-1:-1][::decNum][:num][::-1] for ID in allowedIDs}}

        for ID in allowedIDs:
            for i in range(len(row3[onlineColumns.SupplyPrice3.value][ID])):
                if row3[onlineColumns.SupplyPrice3.value][ID][i] > self.history[ID][onlineColumns.MaxAllowedPrice.value]:
                    row3[onlineColumns.SupplyPrice3.value][ID][i] = self.history[ID][onlineColumns.MaxAllowedPrice.value]
                    row3[onlineColumns.SupplyVolume3.value][ID][i] = 0
                    row3[onlineColumns.SupplyNumber3.value][ID][i] = 0
                if row3[onlineColumns.DemandPrice3.value][ID][i] < self.history[ID][onlineColumns.MinAllowedPrice.value]:
                    row3[onlineColumns.SupplyPrice3.value][ID][i] = self.history[ID][onlineColumns.MinAllowedPrice.value]
                    row3[onlineColumns.DemandVolume3.value][ID][i] = 0
                    row3[onlineColumns.DemandNumber3.value][ID][i] = 0
        return row3

    def row4(self, decNum = 1, num = 0, allowedIDs: list= None) -> dict:
        allowedIDs = self.check_allowedIDs(allowedIDs)
        
        if num == 0:
            row4 = {onlineColumns.SupplyNumber4.value: {ID: self.history[ID][onlineColumns.SupplyNumber4.value][::-1][::decNum][::-1] for ID in allowedIDs},
                    onlineColumns.SupplyVolume4.value: {ID: self.history[ID][onlineColumns.SupplyVolume4.value][::-1][::decNum][::-1] for ID in allowedIDs},
                    onlineColumns.SupplyPrice4.value: {ID: self.history[ID][onlineColumns.SupplyPrice4.value][::-1][::decNum][::-1] for ID in allowedIDs},
                    onlineColumns.DemandPrice4.value: {ID: self.history[ID][onlineColumns.DemandPrice4.value][::-1][::decNum][::-1] for ID in allowedIDs},
                    onlineColumns.DemandVolume4.value: {ID: self.history[ID][onlineColumns.DemandVolume4.value][::-1][::decNum][::-1] for ID in allowedIDs},
                    onlineColumns.DemandNumber4.value: {ID: self.history[ID][onlineColumns.DemandNumber4.value][::-1][::decNum][::-1] for ID in allowedIDs}}
        else:
            row4 = {onlineColumns.SupplyNumber4.value: {ID: self.history[ID][onlineColumns.SupplyNumber4.value][:-decNum*num-1:-1][::decNum][:num][::-1] for ID in allowedIDs},
                onlineColumns.SupplyVolume4.value: {ID: self.history[ID][onlineColumns.SupplyVolume4.value][:-decNum*num-1:-1][::decNum][:num][::-1] for ID in allowedIDs},
                onlineColumns.SupplyPrice4.value: {ID: self.history[ID][onlineColumns.SupplyPrice4.value][:-decNum*num-1:-1][::decNum][:num][::-1] for ID in allowedIDs},
                onlineColumns.DemandPrice4.value: {ID: self.history[ID][onlineColumns.DemandPrice4.value][:-decNum*num-1:-1][::decNum][:num][::-1] for ID in allowedIDs},
                onlineColumns.DemandVolume4.value: {ID: self.history[ID][onlineColumns.DemandVolume4.value][:-decNum*num-1:-1][::decNum][:num][::-1] for ID in allowedIDs},
                onlineColumns.DemandNumber4.value: {ID: self.history[ID][onlineColumns.DemandNumber4.value][:-decNum*num-1:-1][::decNum][:num][::-1] for ID in allowedIDs}}

        for ID in allowedIDs:
            for i in range(len(row4[onlineColumns.SupplyPrice4.value][ID])):
                if row4[onlineColumns.SupplyPrice4.value][ID][i] > self.history[ID][onlineColumns.MaxAllowedPrice.value]:
                    row4[onlineColumns.SupplyPrice4.value][ID][i] = self.history[ID][onlineColumns.MaxAllowedPrice.value]
                    row4[onlineColumns.SupplyVolume4.value][ID][i] = 0
                    row4[onlineColumns.SupplyNumber4.value][ID][i] = 0
                if row4[onlineColumns.DemandPrice4.value][ID][i] < self.history[ID][onlineColumns.MinAllowedPrice.value]:
                    row4[onlineColumns.SupplyPrice4.value][ID][i] = self.history[ID][onlineColumns.MinAllowedPrice.value]
                    row4[onlineColumns.DemandVolume4.value][ID][i] = 0
                    row4[onlineColumns.DemandNumber4.value][ID][i] = 0
        return row4

    def row5(self, decNum = 1, num = 0, allowedIDs: list= None) -> dict:
        allowedIDs = self.check_allowedIDs(allowedIDs)

        if num == 0:
            row5 = {onlineColumns.SupplyNumber5.value: {ID: self.history[ID][onlineColumns.SupplyNumber5.value][::-1][::decNum][::-1] for ID in allowedIDs},
                    onlineColumns.SupplyVolume5.value: {ID: self.history[ID][onlineColumns.SupplyVolume5.value][::-1][::decNum][::-1] for ID in allowedIDs},
                    onlineColumns.SupplyPrice5.value: {ID: self.history[ID][onlineColumns.SupplyPrice5.value][::-1][::decNum][::-1] for ID in allowedIDs},
                    onlineColumns.DemandPrice5.value: {ID: self.history[ID][onlineColumns.DemandPrice5.value][::-1][::decNum][::-1] for ID in allowedIDs},
                    onlineColumns.DemandVolume5.value: {ID: self.history[ID][onlineColumns.DemandVolume5.value][::-1][::decNum][::-1] for ID in allowedIDs},
                    onlineColumns.DemandNumber5.value: {ID: self.history[ID][onlineColumns.DemandNumber5.value][::-1][::decNum][::-1] for ID in allowedIDs}}
        else:
            row5 = {onlineColumns.SupplyNumber5.value: {ID: self.history[ID][onlineColumns.SupplyNumber5.value][:-decNum*num-1:-1][::decNum][:num][::-1] for ID in allowedIDs},
                onlineColumns.SupplyVolume5.value: {ID: self.history[ID][onlineColumns.SupplyVolume5.value][:-decNum*num-1:-1][::decNum][:num][::-1] for ID in allowedIDs},
                onlineColumns.SupplyPrice5.value: {ID: self.history[ID][onlineColumns.SupplyPrice5.value][:-decNum*num-1:-1][::decNum][:num][::-1] for ID in allowedIDs},
                onlineColumns.DemandPrice5.value: {ID: self.history[ID][onlineColumns.DemandPrice5.value][:-decNum*num-1:-1][::decNum][:num][::-1] for ID in allowedIDs},
                onlineColumns.DemandVolume5.value: {ID: self.history[ID][onlineColumns.DemandVolume5.value][:-decNum*num-1:-1][::decNum][:num][::-1] for ID in allowedIDs},
                onlineColumns.DemandNumber5.value: {ID: self.history[ID][onlineColumns.DemandNumber5.value][:-decNum*num-1:-1][::decNum][:num][::-1] for ID in allowedIDs}}

        for ID in allowedIDs:
            for i in range(len(row5[onlineColumns.SupplyPrice5.value][ID])):
                if row5[onlineColumns.SupplyPrice5.value][ID][i] > self.history[ID][onlineColumns.MaxAllowedPrice.value]:
                    row5[onlineColumns.SupplyPrice5.value][ID][i] = self.history[ID][onlineColumns.MaxAllowedPrice.value]
                    row5[onlineColumns.SupplyVolume5.value][ID][i] = 0
                    row5[onlineColumns.SupplyNumber5.value][ID][i] = 0
                if row5[onlineColumns.DemandPrice5.value][ID][i] < self.history[ID][onlineColumns.MinAllowedPrice.value]:
                    row5[onlineColumns.SupplyPrice5.value][ID][i] = self.history[ID][onlineColumns.MinAllowedPrice.value]
                    row5[onlineColumns.DemandVolume5.value][ID][i] = 0
                    row5[onlineColumns.DemandNumber5.value][ID][i] = 0
        return row5

    def lastPricePRC(self, decNum = 1, num = 0, allowedIDs: list= None) -> dict:
        allowedIDs = self.check_allowedIDs(allowedIDs)
        lastPrice = self.lastPrice(decNum, num, allowedIDs)
        return {ID: [(lastPrice[ID][i]-self.history[ID][onlineColumns.YesterdayPrice.value])/self.history[ID][onlineColumns.YesterdayPrice.value]*100 for i in range(len(lastPrice[ID]))] for ID in allowedIDs}

    def todayPricePRC(self, decNum = 1, num = 0, allowedIDs: list= None) -> dict:
        allowedIDs = self.check_allowedIDs(allowedIDs)

        todayPrice = self.todayPrice(decNum, num, allowedIDs)
        return {ID: [(todayPrice[ID][i]-self.history[ID][onlineColumns.YesterdayPrice.value])/self.history[ID][onlineColumns.YesterdayPrice.value]*100 for i in range(len(todayPrice[ID]))] for ID in allowedIDs}

    def perCapitaBuy(self, decNum = 1, num = 0, allowedIDs: list= None) -> dict:
        allowedIDs = self.check_allowedIDs(allowedIDs)

        lastPrice = self.lastPrice(decNum, num, allowedIDs)
        realValues = self.realValues(decNum, num, allowedIDs)
        realBuyVolume = realValues[onlineColumns.RealBuyVolume.value]
        realBuyNumber = realValues[onlineColumns.RealBuyNumber.value]
        perCapitaBuy ={}

        for ID in allowedIDs:
            perCapitaBuy[ID] = []
            for i in range(len(lastPrice[ID])):
                try:
                    perCapitaBuy[ID].append(int(lastPrice[ID][i]*realBuyVolume[ID][i]/realBuyNumber[ID][i]/10000000))
                except:
                    perCapitaBuy[ID].append(0)

        return perCapitaBuy

    def perCapitaSell(self, decNum = 1, num = 0, allowedIDs: list= None) -> dict:
        allowedIDs = self.check_allowedIDs(allowedIDs)

        lastPrice = self.lastPrice(decNum, num, allowedIDs)
        realValues = self.realValues(decNum, num, allowedIDs)
        realSelVolume = realValues[onlineColumns.RealSellVolume.value]
        realSellNumber = realValues[onlineColumns.RealSellNumber.value]
        perCapitaSell ={}

        for ID in allowedIDs:
            perCapitaSell[ID] = []
            for i in range(len(lastPrice[ID])):
                try:
                    perCapitaSell[ID].append(int(lastPrice[ID][i]*realSelVolume[ID][i]/realSellNumber[ID][i]/10000000))
                except:
                    perCapitaSell[ID].append(0)

        return perCapitaSell

    def realPower(self, decNum = 1, num = 0, allowedIDs: list= None) -> dict:
        allowedIDs = self.check_allowedIDs(allowedIDs)

        realValues = self.realValues(decNum, num, allowedIDs)
        realBuyVolume = realValues[onlineColumns.RealBuyVolume.value]
        realBuyNumber = realValues[onlineColumns.RealBuyNumber.value]
        realSellVolume = realValues[onlineColumns.RealSellVolume.value]
        realSellNumber = realValues[onlineColumns.RealSellNumber.value]
        realPower ={}

        for ID in allowedIDs:
            realPower[ID] = []
            for i in range(len(realBuyVolume[ID])):
                try:
                    realPower[ID].append((realBuyVolume[ID][i]/realBuyNumber[ID][i])/(realSellVolume[ID][i]/realSellNumber[ID][i]))
                except:
                    realPower[ID].append(1)

        return realPower

    def demandToSupplyPower(self, decNum = 1, num = 0, allowedIDs: list= None) -> dict:
        allowedIDs = self.check_allowedIDs(allowedIDs)

        row1 = self.row1(decNum, num, allowedIDs)
        row2 = self.row2(decNum, num, allowedIDs)
        row3 = self.row3(decNum, num, allowedIDs)
        row4 = self.row4(decNum, num, allowedIDs)
        row5 = self.row5(decNum, num, allowedIDs)

        demandToSupplyPower = {}

        for ID in allowedIDs:
            demandVolumesZip = zip(row1[onlineColumns.DemandVolume1.value][ID], row2[onlineColumns.DemandVolume2.value][ID], row3[onlineColumns.DemandVolume3.value][ID], row4[onlineColumns.DemandVolume4.value][ID], row5[onlineColumns.DemandVolume5.value][ID])
            demandVolumes = [v1 + v2 + v3 + v4 + v5 for (v1, v2, v3, v4, v5) in demandVolumesZip]
            supplyVolumesZip = zip(row1[onlineColumns.SupplyVolume1.value][ID], row2[onlineColumns.SupplyVolume2.value][ID], row3[onlineColumns.SupplyVolume3.value][ID], row4[onlineColumns.SupplyVolume4.value][ID], row5[onlineColumns.SupplyVolume5.value][ID])
            supplyVolumes = [v1 + v2 + v3 + v4 + v5 for (v1, v2, v3, v4, v5) in supplyVolumesZip]

            demandToSupplyPower[ID] = []

            for i in range(len(demandVolumes)):
                if demandVolumes[i] < 0 or supplyVolumes[i] < 0:
                    demandToSupplyPower[ID].append(0)
                elif demandVolumes[i] == 0:
                    demandToSupplyPower[ID].append(0)
                elif supplyVolumes[i] == 0:
                    demandToSupplyPower[ID].append(0)
                else:
                    demandToSupplyPower[ID].append(log10(demandVolumes[i]/supplyVolumes[i]))

        return demandToSupplyPower

    def demandValue(self, decNum = 1, num = 0, allowedIDs: list= None) -> dict:
        allowedIDs = self.check_allowedIDs(allowedIDs)

        row1 = self.row1(decNum, num, allowedIDs)
        row2 = self.row2(decNum, num, allowedIDs)
        row3 = self.row3(decNum, num, allowedIDs)
        row4 = self.row4(decNum, num, allowedIDs)
        row5 = self.row5(decNum, num, allowedIDs)

        demandValue = {}

        for ID in allowedIDs:

            length = len(row1[onlineColumns.DemandVolume1.value][ID])

            value1 = [row1[onlineColumns.DemandVolume1.value][ID][i] * row1[onlineColumns.DemandPrice1.value][ID][i] for i in range(length)]
            value2 = [row2[onlineColumns.DemandVolume2.value][ID][i] * row2[onlineColumns.DemandPrice2.value][ID][i] for i in range(length)]
            value3 = [row3[onlineColumns.DemandVolume3.value][ID][i] * row3[onlineColumns.DemandPrice3.value][ID][i] for i in range(length)]
            value4 = [row4[onlineColumns.DemandVolume4.value][ID][i] * row4[onlineColumns.DemandPrice4.value][ID][i] for i in range(length)]
            value5 = [row5[onlineColumns.DemandVolume5.value][ID][i] * row5[onlineColumns.DemandPrice5.value][ID][i] for i in range(length)]

            demandValuesZip = zip(value1, value2, value3, value4, value5)
            demandValue[ID] = [(v1 + v2 + v3 + v4 + v5)/10000000 for (v1, v2, v3, v4, v5) in demandValuesZip]

        return demandValue

    def supplyValue(self, decNum = 1, num = 0, allowedIDs: list= None) -> dict:
        allowedIDs = self.check_allowedIDs(allowedIDs)

        row1 = self.row1(decNum, num, allowedIDs)
        row2 = self.row2(decNum, num, allowedIDs)
        row3 = self.row3(decNum, num, allowedIDs)
        row4 = self.row4(decNum, num, allowedIDs)
        row5 = self.row5(decNum, num, allowedIDs)

        supplyValue = {}

        for ID in allowedIDs:

            length = len(row1[onlineColumns.SupplyVolume1.value][ID])

            value1 = [row1[onlineColumns.SupplyVolume1.value][ID][i] * row1[onlineColumns.SupplyPrice1.value][ID][i] for i in range(length)]
            value2 = [row2[onlineColumns.SupplyVolume2.value][ID][i] * row2[onlineColumns.SupplyPrice2.value][ID][i] for i in range(length)]
            value3 = [row3[onlineColumns.SupplyVolume3.value][ID][i] * row3[onlineColumns.SupplyPrice3.value][ID][i] for i in range(length)]
            value4 = [row4[onlineColumns.SupplyVolume4.value][ID][i] * row4[onlineColumns.SupplyPrice4.value][ID][i] for i in range(length)]
            value5 = [row5[onlineColumns.SupplyVolume5.value][ID][i] * row5[onlineColumns.SupplyPrice5.value][ID][i] for i in range(length)]

            supplyValuesZip = zip(value1, value2, value3, value4, value5)
            supplyValue[ID] = [(v1 + v2 + v3 + v4 + v5)/10000000 for (v1, v2, v3, v4, v5) in supplyValuesZip]

        return supplyValue
                
    def demandPerCapita(self, decNum = 1, num = 0, allowedIDs: list= None) -> dict:
        allowedIDs = self.check_allowedIDs(allowedIDs)

        number1 = self.row1(decNum, num, allowedIDs)[onlineColumns.DemandNumber1.value]
        number2 = self.row2(decNum, num, allowedIDs)[onlineColumns.DemandNumber2.value]
        number3 = self.row3(decNum, num, allowedIDs)[onlineColumns.DemandNumber3.value]
        number4 = self.row4(decNum, num, allowedIDs)[onlineColumns.DemandNumber4.value]
        number5 = self.row5(decNum, num, allowedIDs)[onlineColumns.DemandNumber5.value]

        demandValue = self.demandValue(decNum, num, allowedIDs)

        demandPerCapita = {}

        for ID in allowedIDs:

            totalNumber = [number1[ID][i]+number2[ID][i]+number3[ID][i]+number4[ID][i]+number5[ID][i] for i in range(len(number1[ID]))]
            demandPerCapita[ID] = []

            for i in range(len(number1[ID])):
                totalNumber = number1[ID][i]+number2[ID][i]+number3[ID][i]+number4[ID][i]+number5[ID][i]
                try:
                    demandPerCapita[ID].append(demandValue[ID][i]/totalNumber)
                except:
                    demandPerCapita[ID].append(0)
        return demandPerCapita

    def supplyPerCapita(self, decNum = 1, num = 0, allowedIDs: list= None) -> dict:
        allowedIDs = self.check_allowedIDs(allowedIDs)

        number1 = self.row1(decNum, num, allowedIDs)[onlineColumns.SupplyNumber1.value]
        number2 = self.row2(decNum, num, allowedIDs)[onlineColumns.SupplyNumber2.value]
        number3 = self.row3(decNum, num, allowedIDs)[onlineColumns.SupplyNumber3.value]
        number4 = self.row4(decNum, num, allowedIDs)[onlineColumns.SupplyNumber4.value]
        number5 = self.row5(decNum, num, allowedIDs)[onlineColumns.SupplyNumber5.value]

        supplyValue = self.supplyValue(decNum, num, allowedIDs)

        supplyPerCapita = {}

        for ID in allowedIDs:

            totalNumber = [number1[ID][i]+number2[ID][i]+number3[ID][i]+number4[ID][i]+number5[ID][i] for i in range(len(number1[ID]))]
            supplyPerCapita[ID] = []

            for i in range(len(number1[ID])):
                totalNumber = number1[ID][i]+number2[ID][i]+number3[ID][i]+number4[ID][i]+number5[ID][i]
                try:
                    supplyPerCapita[ID].append(supplyValue[ID][i]/totalNumber)
                except:
                    supplyPerCapita[ID].append(0)
        return supplyPerCapita

    # Diff
    def volumeDif(self, decNum = 1, num = 0, length = 1, allowedIDs: list= None) -> dict:
        allowedIDs = self.check_allowedIDs(allowedIDs)
        if num == 0:
            requieredLength = 0
        else:
            requieredLength = num+length

        volume = self.volume(decNum, requieredLength, allowedIDs)
        volumeDif = {}

        for ID in allowedIDs:
            volumeDif[ID] = []
            for i in range(-1, -len(volume[ID])-1, -1):
                if abs(i) + length <= len(volume[ID]):   
                    thisVolumeDif = max(volume[ID][i]-volume[ID][i-length], 0)
                else:
                    thisVolumeDif = max(volume[ID][i], 0)
                volumeDif[ID].append(thisVolumeDif)
            if num == 0:
                volumeDif[ID] = volumeDif[ID][::-1]
            else:
                volumeDif[ID] = volumeDif[ID][::-1][-num:]

        return volumeDif

    def clientVolumeDif(self, decNum = 1, num = 0, length = 1, allowedIDs: list= None) -> dict:
        allowedIDs = self.check_allowedIDs(allowedIDs)
        if num == 0:
            requieredLength = 0
        else:
            requieredLength = num+length

        realValues = self.realValues(decNum, requieredLength, allowedIDs)
        realBuyVolume = realValues[onlineColumns.RealBuyVolume.value]
        corporateValues = self.corporateValues(decNum, requieredLength, allowedIDs)
        corporateBuyVolume = corporateValues[onlineColumns.CorporateBuyVolume.value]
        clientVolumeDif = {}

        for ID in allowedIDs:
            clientVolumeDif[ID] = []
            for i in range(-1, -len(realBuyVolume[ID])-1, -1):
                if abs(i) + length <= len(realBuyVolume[ID]):   
                    thisVolumeDif = max((realBuyVolume[ID][i]+corporateBuyVolume[ID][i])-(realBuyVolume[ID][i-length]+corporateBuyVolume[ID][i-length]), 0)
                else:
                    thisVolumeDif = max(realBuyVolume[ID][i]+corporateBuyVolume[ID][i], 0)
                clientVolumeDif[ID].append(thisVolumeDif)
            if num == 0:
                clientVolumeDif[ID] = clientVolumeDif[ID][::-1]
            else:
                clientVolumeDif[ID] = clientVolumeDif[ID][::-1][-num:]

        return clientVolumeDif

    def realPowerDif(self, decNum = 1, num = 0, length = 1, allowedIDs: list= None) -> dict:
        allowedIDs = self.check_allowedIDs(allowedIDs)
        if num == 0:
            requieredLength = 0
        else:
            requieredLength = num+length

        realValues = self.realValues(decNum, requieredLength, allowedIDs)
        realBuyVolume = realValues[onlineColumns.RealBuyVolume.value]
        realBuyNumber = realValues[onlineColumns.RealBuyNumber.value]
        realSellVolume = realValues[onlineColumns.RealSellVolume.value]
        realSellNumber = realValues[onlineColumns.RealSellNumber.value]
        realPowerDif ={}

        for ID in allowedIDs:
            realPowerDif[ID] = []
            for i in range(-1, -len(realBuyVolume[ID])-1, -1):
                try:
                    if abs(i) + length <= len(realBuyVolume[ID]):   
                        thisRealPowerDif = ((realBuyVolume[ID][i]-realBuyVolume[ID][i-length])/(realBuyNumber[ID][i]-realBuyNumber[ID][i-length]))/\
                        ((realSellVolume[ID][i]-realSellVolume[ID][i-length])/(realSellNumber[ID][i]-realSellNumber[ID][i-length]))
                    else:
                        thisRealPowerDif = (realBuyVolume[ID][i]/realBuyNumber[ID][i])/(realSellVolume[ID][i]/realSellNumber[ID][i])
                except:
                    thisRealPowerDif = 1
                if thisRealPowerDif <= 0:
                    thisRealPowerDif = 1
                realPowerDif[ID].append(thisRealPowerDif)
            if num == 0:
                realPowerDif[ID] = realPowerDif[ID][::-1]
            else:
                realPowerDif[ID] = realPowerDif[ID][::-1][-num:]

        return realPowerDif

    def rpvp(self, decNum = 1, num = 0, length = 1, allowedIDs: list= None) -> dict:
        allowedIDs = self.check_allowedIDs(allowedIDs)

        VolumeDif = self.clientVolumeDif(decNum, num, length, allowedIDs)
        RealPowerDif = self.realPowerDif(decNum, num, length, allowedIDs)

        return {ID: [VolumeDif[ID][i]*log10(RealPowerDif[ID][i]) for i in range(len(VolumeDif[ID]))] for ID in allowedIDs}

    def perCapitaBuyDif(self, decNum = 1, num = 0, length = 1, allowedIDs: list= None) -> dict:
        allowedIDs = self.check_allowedIDs(allowedIDs)
        if num == 0:
            requieredLength = 0
        else:
            requieredLength = num+length

        lastPrice = self.lastPrice(decNum, requieredLength, allowedIDs)
        realValues = self.realValues(decNum, requieredLength, allowedIDs)
        realBuyVolume = realValues[onlineColumns.RealBuyVolume.value]
        realBuyNumber = realValues[onlineColumns.RealBuyNumber.value]
        perCapitaBuyDif = {}

        for ID in allowedIDs:
            perCapitaBuyDif[ID] = []
            for i in range(-1, -len(realBuyVolume[ID])-1, -1):
                try:
                    if abs(i) + length <= len(realBuyVolume[ID]):   
                        thisPerCapitaBuyDif = max(int((realBuyVolume[ID][i]-realBuyVolume[ID][i-length])/(realBuyNumber[ID][i]-realBuyNumber[ID][i-length]) * lastPrice[ID][i] / 10**7), 0)
                    else:
                        thisPerCapitaBuyDif = max(int((realBuyVolume[ID][i]/realBuyNumber[ID][i]) * lastPrice[ID][i] / 10**7), 0)
                except:
                    thisPerCapitaBuyDif = 0
                perCapitaBuyDif[ID].append(thisPerCapitaBuyDif)
            if num == 0:
                perCapitaBuyDif[ID] = perCapitaBuyDif[ID][::-1]
            else:
                perCapitaBuyDif[ID] = perCapitaBuyDif[ID][::-1][-num:]

        return perCapitaBuyDif

    def perCapitaSellDif(self, decNum = 1, num = 0, length = 1, allowedIDs: list= None) -> dict:
        allowedIDs = self.check_allowedIDs(allowedIDs)
        if num == 0:
            requieredLength = 0
        else:
            requieredLength = num+length

        lastPrice = self.lastPrice(decNum, requieredLength, allowedIDs)
        realValues = self.realValues(decNum, requieredLength, allowedIDs)
        realSellVolume = realValues[onlineColumns.RealSellVolume.value]
        realSellNumber = realValues[onlineColumns.RealSellNumber.value]
        perCapitaSellDif = {}

        for ID in allowedIDs:
            perCapitaSellDif[ID] = []
            for i in range(-1, -len(realSellVolume[ID])-1, -1):
                try:
                    if abs(i) + length <= len(realSellVolume[ID]):   
                        thisPerCapitaSellDif = max(int((realSellVolume[ID][i]-realSellVolume[ID][i-length])/(realSellNumber[ID][i]-realSellNumber[ID][i-length]) * lastPrice[ID][i] / 10**7), 0)
                    else:
                        thisPerCapitaSellDif = max(int((realSellVolume[ID][i]/realSellNumber[ID][i]) * lastPrice[ID][i] / 10**7), 0)
                except:
                    thisPerCapitaSellDif = 0
                perCapitaSellDif[ID].append(thisPerCapitaSellDif)
            if num == 0:
                perCapitaSellDif[ID] = perCapitaSellDif[ID][::-1]
            else:
                perCapitaSellDif[ID] = perCapitaSellDif[ID][::-1][-num:]

        return perCapitaSellDif
