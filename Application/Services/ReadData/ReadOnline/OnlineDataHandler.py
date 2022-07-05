from datetime import timedelta
from Domain.ImportEnums import *
from Infrastructure.Repository.TickerRepository import ticker_repo as tr
from math import inf, log10


class onlineDataHandler():

    def __init__(self, IDList: list, cacheMaxSize: int = 200) -> None:
        self.data = {}
        self.enumColumns = [item.value for item in onlineColumns]
        self.cachMaxSize = cacheMaxSize
        if IDList != None:
            self.IDList = IDList
        else:
            self.IDList = tr().read_list_of_tickers(tickerTypes = [1])['ID']

        self.dataSize = 0

        self.isTodayFlag = {}
            
    def update(self, unModData: dict) -> None:
        self.check_unModData_columns(unModData)
        for ID in self.IDList:
            if ID in unModData:
                if self.validate_data(ID, unModData[ID]) == True:
                    self.delete_yesterday_values(ID, unModData[ID])
                    self.update_columns(ID, unModData[ID])

    def set_data(self, data: dict) -> None:

        for ID in data:
            firstValidIndex = 0
            for i in range(len(data[ID][onlineColumns.Time.value])):
                if data[ID][onlineColumns.Time.value][i].hour == 9 and data[ID][onlineColumns.Time.value][i].minute >= 2 or data[ID][onlineColumns.Time.value][i].hour > 9:
                    firstValidIndex = i
                    break
        
            for column in data[ID]:
                if type(data[ID][column]) == list:
                    data[ID][column] = data[ID][column][-(len(data[ID][column])-firstValidIndex):]

        self.data = data
        
    def check_unModData_columns(self, unModData: dict) -> None:

        # check number of IDs
        if unModData == {}:
            print('No IDs in unModData.')
            return

        # check if Time and Volume and MinPrice and MaxPrice columns exist in umModData or not
        IDs: list = list(unModData.keys())
        if onlineColumns.Time.value not in unModData[IDs[0]] or\
             onlineColumns.Volume.value not in unModData[IDs[0]] or\
                 onlineColumns.MinPrice.value not in unModData[IDs[0]] or\
                     onlineColumns.RealBuyVolume.value not in unModData[IDs[0]] or\
                         onlineColumns.CorporateBuyVolume.value not in unModData[IDs[0]] or\
                             onlineColumns.LastTradeTime.value not in unModData[IDs[0]]:
            raise Exception("unModData don't have enough columns.")

    def validate_data(self, ID: int, ID_dict: dict) -> bool:

        if ID not in self.isTodayFlag:
            self.isTodayFlag[ID] = False

        if self.isTodayFlag[ID] == False:
            if ID_dict[onlineColumns.RealBuyVolume.value]+ID_dict[onlineColumns.CorporateBuyVolume.value] <= ID_dict[onlineColumns.Volume.value] and\
                ID_dict[onlineColumns.MinPrice.value] != 0 and ID_dict[onlineColumns.Volume.value] != 0:
                self.isTodayFlag[ID] = True
        
        if ID_dict[onlineColumns.MinPrice.value] == 0 or\
            ID_dict[onlineColumns.MaxPrice.value] == 0 or\
                ID_dict[onlineColumns.TodayPrice.value] == 0 or\
                    ID_dict[onlineColumns.LastPrice.value] == 0 or\
                        ID_dict[onlineColumns.YesterdayPrice.value] == 0 or\
                            ID_dict[onlineColumns.MinAllowedPrice.value] == 0 or\
                                ID_dict[onlineColumns.MaxAllowedPrice.value] == 0:
            return False

        if self.isTodayFlag[ID] == True:
            return True
        else:
            return False

    def delete_yesterday_values(self, ID: int, ID_dict: dict) -> bool:

        if ID in self.data:
            if ID_dict[onlineColumns.Time.value]-self.data[ID][onlineColumns.Time.value][-1] > timedelta(hours= 10):
                print(ID, "yesterday values deleted.")
                for column in ID_dict:
                    self.data[ID][column] = [ID_dict[column]]
                    
    def update_columns(self, ID: int, ID_dict: dict) -> None:

        if ID not in self.data:
            self.data[ID] = {}

        for column in ID_dict:

            if column not in self.enumColumns:
                raise Exception("Column Name Error.")

            if column in [onlineColumns.YesterdayPrice.value, onlineColumns.MinAllowedPrice.value, onlineColumns.MaxAllowedPrice.value]:
                self.data[ID][column] = ID_dict[column]

            elif column not in self.data[ID]:
                self.data[ID][column] = [ID_dict[column]]

            else:
                self.data[ID][column].append(ID_dict[column])
                if self.cachMaxSize != None:
                    self.data[ID][column] = self.data[ID][column][-self.cachMaxSize:] 
                # self.dataSize = len(self.data[self.data.keys()[0]][column])

    def check_IDList(self, IDList: list) -> None:

        if IDList == None:
            newIDList = list(self.data.keys())
        else:
            tempIDList = IDList.copy()
            for ID in tempIDList:
                if ID not in self.data:
                    IDList.remove(ID)
            newIDList = IDList
        return newIDList

    def time(self, decNum = 1, num = 0, IDList: list= None) -> dict:
        IDList = self.check_IDList(IDList)
        if num == 0:
            data = {ID: self.data[ID][onlineColumns.Time.value][::-1][::decNum][::-1] for ID in IDList}
        else:
            data = {ID: self.data[ID][onlineColumns.Time.value][:-decNum*num-1:-1][::decNum][:num][::-1] for ID in IDList}
        return data

    def todayPrice(self, decNum = 1, num = 0, IDList: list= None) -> dict:
        IDList = self.check_IDList(IDList)
        if num == 0:
            data = {ID: self.data[ID][onlineColumns.TodayPrice.value][::-1][::decNum][::-1] for ID in IDList}
        else:
            data = {ID: self.data[ID][onlineColumns.TodayPrice.value][:-decNum*num-1:-1][::decNum][:num][::-1] for ID in IDList}
        return data

    def lastPrice(self, decNum = 1, num = 0, IDList: list= None) -> dict:
        IDList = self.check_IDList(IDList)
        if num == 0:
            data = {ID: self.data[ID][onlineColumns.LastPrice.value][::-1][::decNum][::-1] for ID in IDList}
        else:
            data = {ID: self.data[ID][onlineColumns.LastPrice.value][:-decNum*num-1:-1][::decNum][:num][::-1] for ID in IDList}
        return data
    
    def number(self, decNum = 1, num = 0, IDList: list= None) -> dict:
        IDList = self.check_IDList(IDList)
        if num == 0:
            data = {ID: self.data[ID][onlineColumns.Number.value][::-1][::decNum][::-1] for ID in IDList}
        else:
            data = {ID: self.data[ID][onlineColumns.Number.value][:-decNum*num-1:-1][::decNum][:num][::-1] for ID in IDList}
        return data

    def volume(self, decNum = 1, num = 0, IDList: list= None) -> dict:
        IDList = self.check_IDList(IDList)
        if num == 0:
            data = {ID: self.data[ID][onlineColumns.Volume.value][::-1][::decNum][::-1] for ID in IDList}
        else:
            data = {ID: self.data[ID][onlineColumns.Volume.value][:-decNum*num-1:-1][::decNum][:num][::-1] for ID in IDList}
        return data

    def minPrice(self, decNum = 1, num = 0, IDList: list= None) -> dict:
        IDList = self.check_IDList(IDList)
        if num == 0:
            data = {ID: self.data[ID][onlineColumns.MinPrice.value][::-1][::decNum][::-1] for ID in IDList}
        else:
            data = {ID: self.data[ID][onlineColumns.MinPrice.value][:-decNum*num-1:-1][::decNum][:num][::-1] for ID in IDList}
        return data

    def maxPrice(self, decNum = 1, num = 0, IDList: list= None) -> dict:
        IDList = self.check_IDList(IDList)
        if num == 0:
            data = {ID: self.data[ID][onlineColumns.MaxPrice.value][::-1][::decNum][::-1] for ID in IDList}
        else:
            data = {ID: self.data[ID][onlineColumns.MaxPrice.value][:-decNum*num-1:-1][::decNum][:num][::-1] for ID in IDList}
        return data

    def yesterdayPrice(self, IDList: list= None) -> dict:
        IDList = self.check_IDList(IDList)
        return {ID: self.data[ID][onlineColumns.YesterdayPrice.value] for ID in IDList}

    def minAllowedPrice(self, IDList: list= None) -> dict:
        IDList = self.check_IDList(IDList)
        return {ID: self.data[ID][onlineColumns.MinAllowedPrice.value] for ID in IDList}

    def maxAllowedPrice(self, IDList: list= None) -> dict:
        IDList = self.check_IDList(IDList)
        return {ID: self.data[ID][onlineColumns.MaxAllowedPrice.value] for ID in IDList}

    def realValues(self, decNum = 1, num = 0, IDList: list= None) -> dict:
        IDList = self.check_IDList(IDList)
        if num == 0:
            data = {onlineColumns.RealBuyNumber.value: {ID: self.data[ID][onlineColumns.RealBuyNumber.value][::-1][::decNum][::-1] for ID in IDList},
                    onlineColumns.RealBuyVolume.value: {ID: self.data[ID][onlineColumns.RealBuyVolume.value][::-1][::decNum][::-1] for ID in IDList},
                    onlineColumns.RealSellNumber.value: {ID: self.data[ID][onlineColumns.RealSellNumber.value][::-1][::decNum][::-1] for ID in IDList},
                    onlineColumns.RealSellVolume.value: {ID: self.data[ID][onlineColumns.RealSellVolume.value][::-1][::decNum][::-1] for ID in IDList}}
        else:
            data = {onlineColumns.RealBuyNumber.value: {ID: self.data[ID][onlineColumns.RealBuyNumber.value][:-decNum*num-1:-1][::decNum][:num][::-1] for ID in self.data},
                onlineColumns.RealBuyVolume.value: {ID: self.data[ID][onlineColumns.RealBuyVolume.value][:-decNum*num-1:-1][::decNum][:num][::-1] for ID in self.data},
                onlineColumns.RealSellNumber.value: {ID: self.data[ID][onlineColumns.RealSellNumber.value][:-decNum*num-1:-1][::decNum][:num][::-1] for ID in self.data},
                onlineColumns.RealSellVolume.value: {ID: self.data[ID][onlineColumns.RealSellVolume.value][:-decNum*num-1:-1][::decNum][:num][::-1] for ID in self.data}}
        return data

    def corporateValues(self, decNum = 1, num = 0, IDList: list= None) -> dict:
        IDList = self.check_IDList(IDList)
        if num == 0:
            data = {onlineColumns.CorporateBuyNumber.value: {ID: self.data[ID][onlineColumns.CorporateBuyNumber.value][::-1][::decNum][::-1] for ID in IDList},
                onlineColumns.CorporateBuyVolume.value: {ID: self.data[ID][onlineColumns.CorporateBuyVolume.value][::-1][::decNum][::-1] for ID in IDList},
                onlineColumns.CorporateSellNumber.value: {ID: self.data[ID][onlineColumns.CorporateSellNumber.value][::-1][::decNum][::-1] for ID in IDList},
                onlineColumns.CorporateSellVolume.value: {ID: self.data[ID][onlineColumns.CorporateSellVolume.value][::-1][::decNum][::-1] for ID in IDList}}
        else:
            data = {onlineColumns.CorporateBuyNumber.value: {ID: self.data[ID][onlineColumns.CorporateBuyNumber.value][:-decNum*num-1:-1][::decNum][:num][::-1] for ID in IDList},
                onlineColumns.CorporateBuyVolume.value: {ID: self.data[ID][onlineColumns.CorporateBuyVolume.value][:-decNum*num-1:-1][::decNum][:num][::-1] for ID in IDList},
                onlineColumns.CorporateSellNumber.value: {ID: self.data[ID][onlineColumns.CorporateSellNumber.value][:-decNum*num-1:-1][::decNum][:num][::-1] for ID in IDList},
                onlineColumns.CorporateSellVolume.value: {ID: self.data[ID][onlineColumns.CorporateSellVolume.value][:-decNum*num-1:-1][::decNum][:num][::-1] for ID in IDList}}
        return data

    def row1(self, decNum = 1, num = 0, IDList: list= None) -> dict:
        IDList = self.check_IDList(IDList)

        if num == 0:
            row1 = {onlineColumns.SupplyNumber1.value: {ID: self.data[ID][onlineColumns.SupplyNumber1.value][::-1][::decNum][::-1] for ID in IDList},
                    onlineColumns.SupplyVolume1.value: {ID: self.data[ID][onlineColumns.SupplyVolume1.value][::-1][::decNum][::-1] for ID in IDList},
                    onlineColumns.SupplyPrice1.value: {ID: self.data[ID][onlineColumns.SupplyPrice1.value][::-1][::decNum][::-1] for ID in IDList},
                    onlineColumns.DemandPrice1.value: {ID: self.data[ID][onlineColumns.DemandPrice1.value][::-1][::decNum][::-1] for ID in IDList},
                    onlineColumns.DemandVolume1.value: {ID: self.data[ID][onlineColumns.DemandVolume1.value][::-1][::decNum][::-1] for ID in IDList},
                    onlineColumns.DemandNumber1.value: {ID: self.data[ID][onlineColumns.DemandNumber1.value][::-1][::decNum][::-1] for ID in IDList}}
        else:
            row1 = {onlineColumns.SupplyNumber1.value: {ID: self.data[ID][onlineColumns.SupplyNumber1.value][:-decNum*num-1:-1][::decNum][:num][::-1] for ID in IDList},
                onlineColumns.SupplyVolume1.value: {ID: self.data[ID][onlineColumns.SupplyVolume1.value][:-decNum*num-1:-1][::decNum][:num][::-1] for ID in IDList},
                onlineColumns.SupplyPrice1.value: {ID: self.data[ID][onlineColumns.SupplyPrice1.value][:-decNum*num-1:-1][::decNum][:num][::-1] for ID in IDList},
                onlineColumns.DemandPrice1.value: {ID: self.data[ID][onlineColumns.DemandPrice1.value][:-decNum*num-1:-1][::decNum][:num][::-1] for ID in IDList},
                onlineColumns.DemandVolume1.value: {ID: self.data[ID][onlineColumns.DemandVolume1.value][:-decNum*num-1:-1][::decNum][:num][::-1] for ID in IDList},
                onlineColumns.DemandNumber1.value: {ID: self.data[ID][onlineColumns.DemandNumber1.value][:-decNum*num-1:-1][::decNum][:num][::-1] for ID in IDList}}

        for ID in IDList:
            for i in range(len(row1[onlineColumns.SupplyPrice1.value][ID])):
                if row1[onlineColumns.SupplyPrice1.value][ID][i] > self.data[ID][onlineColumns.MaxAllowedPrice.value]:
                    row1[onlineColumns.SupplyPrice1.value][ID][i] = self.data[ID][onlineColumns.MaxAllowedPrice.value]
                    row1[onlineColumns.SupplyVolume1.value][ID][i] = 0
                    row1[onlineColumns.SupplyNumber1.value][ID][i] = 0
                if row1[onlineColumns.DemandPrice1.value][ID][i] < self.data[ID][onlineColumns.MinAllowedPrice.value]:
                    row1[onlineColumns.DemandPrice1.value][ID][i] = self.data[ID][onlineColumns.MinAllowedPrice.value]
                    row1[onlineColumns.DemandVolume1.value][ID][i] = 0
                    row1[onlineColumns.DemandNumber1.value][ID][i] = 0
        return row1

    def row2(self, decNum = 1, num = 0, IDList: list= None) -> dict:
        IDList = self.check_IDList(IDList)

        if num == 0:
            row2 = {onlineColumns.SupplyNumber2.value: {ID: self.data[ID][onlineColumns.SupplyNumber2.value][::-1][::decNum][::-1] for ID in IDList},
                    onlineColumns.SupplyVolume2.value: {ID: self.data[ID][onlineColumns.SupplyVolume2.value][::-1][::decNum][::-1] for ID in IDList},
                    onlineColumns.SupplyPrice2.value: {ID: self.data[ID][onlineColumns.SupplyPrice2.value][::-1][::decNum][::-1] for ID in IDList},
                    onlineColumns.DemandPrice2.value: {ID: self.data[ID][onlineColumns.DemandPrice2.value][::-1][::decNum][::-1] for ID in IDList},
                    onlineColumns.DemandVolume2.value: {ID: self.data[ID][onlineColumns.DemandVolume2.value][::-1][::decNum][::-1] for ID in IDList},
                    onlineColumns.DemandNumber2.value: {ID: self.data[ID][onlineColumns.DemandNumber2.value][::-1][::decNum][::-1] for ID in IDList}}
        else:
            row2 = {onlineColumns.SupplyNumber2.value: {ID: self.data[ID][onlineColumns.SupplyNumber2.value][:-decNum*num-1:-1][::decNum][:num][::-1] for ID in IDList},
                onlineColumns.SupplyVolume2.value: {ID: self.data[ID][onlineColumns.SupplyVolume2.value][:-decNum*num-1:-1][::decNum][:num][::-1] for ID in IDList},
                onlineColumns.SupplyPrice2.value: {ID: self.data[ID][onlineColumns.SupplyPrice2.value][:-decNum*num-1:-1][::decNum][:num][::-1] for ID in IDList},
                onlineColumns.DemandPrice2.value: {ID: self.data[ID][onlineColumns.DemandPrice2.value][:-decNum*num-1:-1][::decNum][:num][::-1] for ID in IDList},
                onlineColumns.DemandVolume2.value: {ID: self.data[ID][onlineColumns.DemandVolume2.value][:-decNum*num-1:-1][::decNum][:num][::-1] for ID in IDList},
                onlineColumns.DemandNumber2.value: {ID: self.data[ID][onlineColumns.DemandNumber2.value][:-decNum*num-1:-1][::decNum][:num][::-1] for ID in IDList}}

        for ID in IDList:
            for i in range(len(row2[onlineColumns.SupplyPrice2.value][ID])):
                if row2[onlineColumns.SupplyPrice2.value][ID][i] > self.data[ID][onlineColumns.MaxAllowedPrice.value]:
                    row2[onlineColumns.SupplyPrice2.value][ID][i] = self.data[ID][onlineColumns.MaxAllowedPrice.value]
                    row2[onlineColumns.SupplyVolume2.value][ID][i] = 0
                    row2[onlineColumns.SupplyNumber2.value][ID][i] = 0
                if row2[onlineColumns.DemandPrice2.value][ID][i] < self.data[ID][onlineColumns.MinAllowedPrice.value]:
                    row2[onlineColumns.SupplyPrice2.value][ID][i] = self.data[ID][onlineColumns.MinAllowedPrice.value]
                    row2[onlineColumns.DemandVolume2.value][ID][i] = 0
                    row2[onlineColumns.DemandNumber2.value][ID][i] = 0
        return row2

    def row3(self, decNum = 1, num = 0, IDList: list= None) -> dict:
        IDList = self.check_IDList(IDList)

        if num == 0:
            row3 = {onlineColumns.SupplyNumber3.value: {ID: self.data[ID][onlineColumns.SupplyNumber3.value][::-1][::decNum][::-1] for ID in IDList},
                    onlineColumns.SupplyVolume3.value: {ID: self.data[ID][onlineColumns.SupplyVolume3.value][::-1][::decNum][::-1] for ID in IDList},
                    onlineColumns.SupplyPrice3.value: {ID: self.data[ID][onlineColumns.SupplyPrice3.value][::-1][::decNum][::-1] for ID in IDList},
                    onlineColumns.DemandPrice3.value: {ID: self.data[ID][onlineColumns.DemandPrice3.value][::-1][::decNum][::-1] for ID in IDList},
                    onlineColumns.DemandVolume3.value: {ID: self.data[ID][onlineColumns.DemandVolume3.value][::-1][::decNum][::-1] for ID in IDList},
                    onlineColumns.DemandNumber3.value: {ID: self.data[ID][onlineColumns.DemandNumber3.value][::-1][::decNum][::-1] for ID in IDList}}
        else:
            row3 = {onlineColumns.SupplyNumber3.value: {ID: self.data[ID][onlineColumns.SupplyNumber3.value][:-decNum*num-1:-1][::decNum][:num][::-1] for ID in IDList},
                onlineColumns.SupplyVolume3.value: {ID: self.data[ID][onlineColumns.SupplyVolume3.value][:-decNum*num-1:-1][::decNum][:num][::-1] for ID in IDList},
                onlineColumns.SupplyPrice3.value: {ID: self.data[ID][onlineColumns.SupplyPrice3.value][:-decNum*num-1:-1][::decNum][:num][::-1] for ID in IDList},
                onlineColumns.DemandPrice3.value: {ID: self.data[ID][onlineColumns.DemandPrice3.value][:-decNum*num-1:-1][::decNum][:num][::-1] for ID in IDList},
                onlineColumns.DemandVolume3.value: {ID: self.data[ID][onlineColumns.DemandVolume3.value][:-decNum*num-1:-1][::decNum][:num][::-1] for ID in IDList},
                onlineColumns.DemandNumber3.value: {ID: self.data[ID][onlineColumns.DemandNumber3.value][:-decNum*num-1:-1][::decNum][:num][::-1] for ID in IDList}}

        for ID in IDList:
            for i in range(len(row3[onlineColumns.SupplyPrice3.value][ID])):
                if row3[onlineColumns.SupplyPrice3.value][ID][i] > self.data[ID][onlineColumns.MaxAllowedPrice.value]:
                    row3[onlineColumns.SupplyPrice3.value][ID][i] = self.data[ID][onlineColumns.MaxAllowedPrice.value]
                    row3[onlineColumns.SupplyVolume3.value][ID][i] = 0
                    row3[onlineColumns.SupplyNumber3.value][ID][i] = 0
                if row3[onlineColumns.DemandPrice3.value][ID][i] < self.data[ID][onlineColumns.MinAllowedPrice.value]:
                    row3[onlineColumns.SupplyPrice3.value][ID][i] = self.data[ID][onlineColumns.MinAllowedPrice.value]
                    row3[onlineColumns.DemandVolume3.value][ID][i] = 0
                    row3[onlineColumns.DemandNumber3.value][ID][i] = 0
        return row3

    def row4(self, decNum = 1, num = 0, IDList: list= None) -> dict:
        IDList = self.check_IDList(IDList)
        
        if num == 0:
            row4 = {onlineColumns.SupplyNumber4.value: {ID: self.data[ID][onlineColumns.SupplyNumber4.value][::-1][::decNum][::-1] for ID in IDList},
                    onlineColumns.SupplyVolume4.value: {ID: self.data[ID][onlineColumns.SupplyVolume4.value][::-1][::decNum][::-1] for ID in IDList},
                    onlineColumns.SupplyPrice4.value: {ID: self.data[ID][onlineColumns.SupplyPrice4.value][::-1][::decNum][::-1] for ID in IDList},
                    onlineColumns.DemandPrice4.value: {ID: self.data[ID][onlineColumns.DemandPrice4.value][::-1][::decNum][::-1] for ID in IDList},
                    onlineColumns.DemandVolume4.value: {ID: self.data[ID][onlineColumns.DemandVolume4.value][::-1][::decNum][::-1] for ID in IDList},
                    onlineColumns.DemandNumber4.value: {ID: self.data[ID][onlineColumns.DemandNumber4.value][::-1][::decNum][::-1] for ID in IDList}}
        else:
            row4 = {onlineColumns.SupplyNumber4.value: {ID: self.data[ID][onlineColumns.SupplyNumber4.value][:-decNum*num-1:-1][::decNum][:num][::-1] for ID in IDList},
                onlineColumns.SupplyVolume4.value: {ID: self.data[ID][onlineColumns.SupplyVolume4.value][:-decNum*num-1:-1][::decNum][:num][::-1] for ID in IDList},
                onlineColumns.SupplyPrice4.value: {ID: self.data[ID][onlineColumns.SupplyPrice4.value][:-decNum*num-1:-1][::decNum][:num][::-1] for ID in IDList},
                onlineColumns.DemandPrice4.value: {ID: self.data[ID][onlineColumns.DemandPrice4.value][:-decNum*num-1:-1][::decNum][:num][::-1] for ID in IDList},
                onlineColumns.DemandVolume4.value: {ID: self.data[ID][onlineColumns.DemandVolume4.value][:-decNum*num-1:-1][::decNum][:num][::-1] for ID in IDList},
                onlineColumns.DemandNumber4.value: {ID: self.data[ID][onlineColumns.DemandNumber4.value][:-decNum*num-1:-1][::decNum][:num][::-1] for ID in IDList}}

        for ID in IDList:
            for i in range(len(row4[onlineColumns.SupplyPrice4.value][ID])):
                if row4[onlineColumns.SupplyPrice4.value][ID][i] > self.data[ID][onlineColumns.MaxAllowedPrice.value]:
                    row4[onlineColumns.SupplyPrice4.value][ID][i] = self.data[ID][onlineColumns.MaxAllowedPrice.value]
                    row4[onlineColumns.SupplyVolume4.value][ID][i] = 0
                    row4[onlineColumns.SupplyNumber4.value][ID][i] = 0
                if row4[onlineColumns.DemandPrice4.value][ID][i] < self.data[ID][onlineColumns.MinAllowedPrice.value]:
                    row4[onlineColumns.SupplyPrice4.value][ID][i] = self.data[ID][onlineColumns.MinAllowedPrice.value]
                    row4[onlineColumns.DemandVolume4.value][ID][i] = 0
                    row4[onlineColumns.DemandNumber4.value][ID][i] = 0
        return row4

    def row5(self, decNum = 1, num = 0, IDList: list= None) -> dict:
        IDList = self.check_IDList(IDList)

        if num == 0:
            row5 = {onlineColumns.SupplyNumber5.value: {ID: self.data[ID][onlineColumns.SupplyNumber5.value][::-1][::decNum][::-1] for ID in IDList},
                    onlineColumns.SupplyVolume5.value: {ID: self.data[ID][onlineColumns.SupplyVolume5.value][::-1][::decNum][::-1] for ID in IDList},
                    onlineColumns.SupplyPrice5.value: {ID: self.data[ID][onlineColumns.SupplyPrice5.value][::-1][::decNum][::-1] for ID in IDList},
                    onlineColumns.DemandPrice5.value: {ID: self.data[ID][onlineColumns.DemandPrice5.value][::-1][::decNum][::-1] for ID in IDList},
                    onlineColumns.DemandVolume5.value: {ID: self.data[ID][onlineColumns.DemandVolume5.value][::-1][::decNum][::-1] for ID in IDList},
                    onlineColumns.DemandNumber5.value: {ID: self.data[ID][onlineColumns.DemandNumber5.value][::-1][::decNum][::-1] for ID in IDList}}
        else:
            row5 = {onlineColumns.SupplyNumber5.value: {ID: self.data[ID][onlineColumns.SupplyNumber5.value][:-decNum*num-1:-1][::decNum][:num][::-1] for ID in IDList},
                onlineColumns.SupplyVolume5.value: {ID: self.data[ID][onlineColumns.SupplyVolume5.value][:-decNum*num-1:-1][::decNum][:num][::-1] for ID in IDList},
                onlineColumns.SupplyPrice5.value: {ID: self.data[ID][onlineColumns.SupplyPrice5.value][:-decNum*num-1:-1][::decNum][:num][::-1] for ID in IDList},
                onlineColumns.DemandPrice5.value: {ID: self.data[ID][onlineColumns.DemandPrice5.value][:-decNum*num-1:-1][::decNum][:num][::-1] for ID in IDList},
                onlineColumns.DemandVolume5.value: {ID: self.data[ID][onlineColumns.DemandVolume5.value][:-decNum*num-1:-1][::decNum][:num][::-1] for ID in IDList},
                onlineColumns.DemandNumber5.value: {ID: self.data[ID][onlineColumns.DemandNumber5.value][:-decNum*num-1:-1][::decNum][:num][::-1] for ID in IDList}}

        for ID in IDList:
            for i in range(len(row5[onlineColumns.SupplyPrice5.value][ID])):
                if row5[onlineColumns.SupplyPrice5.value][ID][i] > self.data[ID][onlineColumns.MaxAllowedPrice.value]:
                    row5[onlineColumns.SupplyPrice5.value][ID][i] = self.data[ID][onlineColumns.MaxAllowedPrice.value]
                    row5[onlineColumns.SupplyVolume5.value][ID][i] = 0
                    row5[onlineColumns.SupplyNumber5.value][ID][i] = 0
                if row5[onlineColumns.DemandPrice5.value][ID][i] < self.data[ID][onlineColumns.MinAllowedPrice.value]:
                    row5[onlineColumns.SupplyPrice5.value][ID][i] = self.data[ID][onlineColumns.MinAllowedPrice.value]
                    row5[onlineColumns.DemandVolume5.value][ID][i] = 0
                    row5[onlineColumns.DemandNumber5.value][ID][i] = 0
        return row5

    def lastPricePRC(self, decNum = 1, num = 0, IDList: list= None) -> dict:
        IDList = self.check_IDList(IDList)
        lastPrice = self.lastPrice(decNum, num, IDList)
        return {ID: [(lastPrice[ID][i]-self.data[ID][onlineColumns.YesterdayPrice.value])/self.data[ID][onlineColumns.YesterdayPrice.value]*100 for i in range(len(lastPrice[ID]))] for ID in IDList}

    def todayPricePRC(self, decNum = 1, num = 0, IDList: list= None) -> dict:
        IDList = self.check_IDList(IDList)

        todayPrice = self.todayPrice(decNum, num, IDList)
        return {ID: [(todayPrice[ID][i]-self.data[ID][onlineColumns.YesterdayPrice.value])/self.data[ID][onlineColumns.YesterdayPrice.value]*100 for i in range(len(todayPrice[ID]))] for ID in IDList}

    def perCapitaBuy(self, decNum = 1, num = 0, IDList: list= None) -> dict:
        IDList = self.check_IDList(IDList)

        lastPrice = self.lastPrice(decNum, num, IDList)
        realValues = self.realValues(decNum, num, IDList)
        realBuyVolume = realValues[onlineColumns.RealBuyVolume.value]
        realBuyNumber = realValues[onlineColumns.RealBuyNumber.value]
        perCapitaBuy ={}

        for ID in IDList:
            perCapitaBuy[ID] = []
            for i in range(len(lastPrice[ID])):
                try:
                    perCapitaBuy[ID].append(int(lastPrice[ID][i]*realBuyVolume[ID][i]/realBuyNumber[ID][i]/10000000))
                except:
                    perCapitaBuy[ID].append(0)

        return perCapitaBuy

    def perCapitaSell(self, decNum = 1, num = 0, IDList: list= None) -> dict:
        IDList = self.check_IDList(IDList)

        lastPrice = self.lastPrice(decNum, num, IDList)
        realValues = self.realValues(decNum, num, IDList)
        realSelVolume = realValues[onlineColumns.RealSellVolume.value]
        realSellNumber = realValues[onlineColumns.RealSellNumber.value]
        perCapitaSell ={}

        for ID in IDList:
            perCapitaSell[ID] = []
            for i in range(len(lastPrice[ID])):
                try:
                    perCapitaSell[ID].append(int(lastPrice[ID][i]*realSelVolume[ID][i]/realSellNumber[ID][i]/10000000))
                except:
                    perCapitaSell[ID].append(0)

        return perCapitaSell

    def realPower(self, decNum = 1, num = 0, IDList: list= None) -> dict:
        IDList = self.check_IDList(IDList)

        realValues = self.realValues(decNum, num, IDList)
        realBuyVolume = realValues[onlineColumns.RealBuyVolume.value]
        realBuyNumber = realValues[onlineColumns.RealBuyNumber.value]
        realSellVolume = realValues[onlineColumns.RealSellVolume.value]
        realSellNumber = realValues[onlineColumns.RealSellNumber.value]
        realPower ={}

        for ID in IDList:
            realPower[ID] = []
            for i in range(len(realBuyVolume[ID])):
                try:
                    realPower[ID].append((realBuyVolume[ID][i]/realBuyNumber[ID][i])/(realSellVolume[ID][i]/realSellNumber[ID][i]))
                except:
                    realPower[ID].append(1)

        return realPower

    def demandToSupplyPower(self, decNum = 1, num = 0, IDList: list= None) -> dict:
        IDList = self.check_IDList(IDList)

        row1 = self.row1(decNum, num, IDList)
        row2 = self.row2(decNum, num, IDList)
        row3 = self.row3(decNum, num, IDList)
        row4 = self.row4(decNum, num, IDList)
        row5 = self.row5(decNum, num, IDList)

        demandToSupplyPower = {}

        for ID in IDList:
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

    def demandValue(self, decNum = 1, num = 0, IDList: list= None) -> dict:
        IDList = self.check_IDList(IDList)

        row1 = self.row1(decNum, num, IDList)
        row2 = self.row2(decNum, num, IDList)
        row3 = self.row3(decNum, num, IDList)
        row4 = self.row4(decNum, num, IDList)
        row5 = self.row5(decNum, num, IDList)

        demandValue = {}

        for ID in IDList:

            length = len(row1[onlineColumns.DemandVolume1.value][ID])

            value1 = [row1[onlineColumns.DemandVolume1.value][ID][i] * row1[onlineColumns.DemandPrice1.value][ID][i] for i in range(length)]
            value2 = [row2[onlineColumns.DemandVolume2.value][ID][i] * row2[onlineColumns.DemandPrice2.value][ID][i] for i in range(length)]
            value3 = [row3[onlineColumns.DemandVolume3.value][ID][i] * row3[onlineColumns.DemandPrice3.value][ID][i] for i in range(length)]
            value4 = [row4[onlineColumns.DemandVolume4.value][ID][i] * row4[onlineColumns.DemandPrice4.value][ID][i] for i in range(length)]
            value5 = [row5[onlineColumns.DemandVolume5.value][ID][i] * row5[onlineColumns.DemandPrice5.value][ID][i] for i in range(length)]

            demandValuesZip = zip(value1, value2, value3, value4, value5)
            demandValue[ID] = [(v1 + v2 + v3 + v4 + v5)/10000000 for (v1, v2, v3, v4, v5) in demandValuesZip]

        return demandValue

    def supplyValue(self, decNum = 1, num = 0, IDList: list= None) -> dict:
        IDList = self.check_IDList(IDList)

        row1 = self.row1(decNum, num, IDList)
        row2 = self.row2(decNum, num, IDList)
        row3 = self.row3(decNum, num, IDList)
        row4 = self.row4(decNum, num, IDList)
        row5 = self.row5(decNum, num, IDList)

        supplyValue = {}

        for ID in IDList:

            length = len(row1[onlineColumns.SupplyVolume1.value][ID])

            value1 = [row1[onlineColumns.SupplyVolume1.value][ID][i] * row1[onlineColumns.SupplyPrice1.value][ID][i] for i in range(length)]
            value2 = [row2[onlineColumns.SupplyVolume2.value][ID][i] * row2[onlineColumns.SupplyPrice2.value][ID][i] for i in range(length)]
            value3 = [row3[onlineColumns.SupplyVolume3.value][ID][i] * row3[onlineColumns.SupplyPrice3.value][ID][i] for i in range(length)]
            value4 = [row4[onlineColumns.SupplyVolume4.value][ID][i] * row4[onlineColumns.SupplyPrice4.value][ID][i] for i in range(length)]
            value5 = [row5[onlineColumns.SupplyVolume5.value][ID][i] * row5[onlineColumns.SupplyPrice5.value][ID][i] for i in range(length)]

            supplyValuesZip = zip(value1, value2, value3, value4, value5)
            supplyValue[ID] = [(v1 + v2 + v3 + v4 + v5)/10000000 for (v1, v2, v3, v4, v5) in supplyValuesZip]

        return supplyValue
                
    def demandPerCapita(self, decNum = 1, num = 0, IDList: list= None) -> dict:
        IDList = self.check_IDList(IDList)

        number1 = self.row1(decNum, num, IDList)[onlineColumns.DemandNumber1.value]
        number2 = self.row2(decNum, num, IDList)[onlineColumns.DemandNumber2.value]
        number3 = self.row3(decNum, num, IDList)[onlineColumns.DemandNumber3.value]
        number4 = self.row4(decNum, num, IDList)[onlineColumns.DemandNumber4.value]
        number5 = self.row5(decNum, num, IDList)[onlineColumns.DemandNumber5.value]

        demandValue = self.demandValue(decNum, num, IDList)

        demandPerCapita = {}

        for ID in IDList:

            totalNumber = [number1[ID][i]+number2[ID][i]+number3[ID][i]+number4[ID][i]+number5[ID][i] for i in range(len(number1[ID]))]
            demandPerCapita[ID] = []

            for i in range(len(number1[ID])):
                totalNumber = number1[ID][i]+number2[ID][i]+number3[ID][i]+number4[ID][i]+number5[ID][i]
                try:
                    demandPerCapita[ID].append(demandValue[ID][i]/totalNumber)
                except:
                    demandPerCapita[ID].append(0)
        return demandPerCapita

    def supplyPerCapita(self, decNum = 1, num = 0, IDList: list= None) -> dict:
        IDList = self.check_IDList(IDList)

        number1 = self.row1(decNum, num, IDList)[onlineColumns.SupplyNumber1.value]
        number2 = self.row2(decNum, num, IDList)[onlineColumns.SupplyNumber2.value]
        number3 = self.row3(decNum, num, IDList)[onlineColumns.SupplyNumber3.value]
        number4 = self.row4(decNum, num, IDList)[onlineColumns.SupplyNumber4.value]
        number5 = self.row5(decNum, num, IDList)[onlineColumns.SupplyNumber5.value]

        supplyValue = self.supplyValue(decNum, num, IDList)

        supplyPerCapita = {}

        for ID in IDList:

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
    def volumeDif(self, decNum = 1, num = 0, length = 1, IDList: list= None) -> dict:
        IDList = self.check_IDList(IDList)
        if num == 0:
            requieredLength = 0
        else:
            requieredLength = num+length

        volume = self.volume(decNum, requieredLength, IDList)
        volumeDif = {}

        for ID in IDList:
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

    def clientVolumeDif(self, decNum = 1, num = 0, length = 1, IDList: list= None) -> dict:
        IDList = self.check_IDList(IDList)
        if num == 0:
            requieredLength = 0
        else:
            requieredLength = num+length

        realValues = self.realValues(decNum, requieredLength, IDList)
        realBuyVolume = realValues[onlineColumns.RealBuyVolume.value]
        corporateValues = self.corporateValues(decNum, requieredLength, IDList)
        corporateBuyVolume = corporateValues[onlineColumns.CorporateBuyVolume.value]
        clientVolumeDif = {}

        for ID in IDList:
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

    def realPowerDif(self, decNum = 1, num = 0, length = 1, IDList: list= None) -> dict:
        IDList = self.check_IDList(IDList)
        if num == 0:
            requieredLength = 0
        else:
            requieredLength = num+length

        realValues = self.realValues(decNum, requieredLength, IDList)
        realBuyVolume = realValues[onlineColumns.RealBuyVolume.value]
        realBuyNumber = realValues[onlineColumns.RealBuyNumber.value]
        realSellVolume = realValues[onlineColumns.RealSellVolume.value]
        realSellNumber = realValues[onlineColumns.RealSellNumber.value]
        realPowerDif ={}

        for ID in IDList:
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

    def rpvp(self, decNum = 1, num = 0, length = 1, IDList: list= None) -> dict:
        IDList = self.check_IDList(IDList)

        VolumeDif = self.clientVolumeDif(decNum, num, length, IDList)
        RealPowerDif = self.realPowerDif(decNum, num, length, IDList)

        return {ID: [VolumeDif[ID][i]*log10(RealPowerDif[ID][i]) for i in range(len(VolumeDif[ID]))] for ID in IDList}

    def perCapitaBuyDif(self, decNum = 1, num = 0, length = 1, IDList: list= None) -> dict:
        IDList = self.check_IDList(IDList)
        if num == 0:
            requieredLength = 0
        else:
            requieredLength = num+length

        lastPrice = self.lastPrice(decNum, requieredLength, IDList)
        realValues = self.realValues(decNum, requieredLength, IDList)
        realBuyVolume = realValues[onlineColumns.RealBuyVolume.value]
        realBuyNumber = realValues[onlineColumns.RealBuyNumber.value]
        perCapitaBuyDif = {}

        for ID in IDList:
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

    def perCapitaSellDif(self, decNum = 1, num = 0, length = 1, IDList: list= None) -> dict:
        IDList = self.check_IDList(IDList)
        if num == 0:
            requieredLength = 0
        else:
            requieredLength = num+length

        lastPrice = self.lastPrice(decNum, requieredLength, IDList)
        realValues = self.realValues(decNum, requieredLength, IDList)
        realSellVolume = realValues[onlineColumns.RealSellVolume.value]
        realSellNumber = realValues[onlineColumns.RealSellNumber.value]
        perCapitaSellDif = {}

        for ID in IDList:
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
