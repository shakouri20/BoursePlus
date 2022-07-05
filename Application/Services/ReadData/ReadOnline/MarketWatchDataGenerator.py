from  datetime import datetime
from math import log10
from Domain.Enums.MarketGroups import marketGroupType
from Infrastructure.Repository.TickerRepository import ticker_repo
from Domain.ImportEnums import *

class marketWatchDataGenerator():

    def __init__(self) -> None:
        
        tr = ticker_repo()

        self.marketWatchGroups = {
            
            marketGroupType.TotalMarket.value: marketWatchGroup(tr.read_list_of_tickers(tickerTypes = [1], IPO= 0)['ID']), 
            # marketGroupType.Bourse.value: marketWatchGroup(tr.read_list_of_tickers(tickerTypes = [1], marketTypes= [1, 2, 3, 4], IPO= 0)['ID']), 
            # marketGroupType.FaraBourse.value: marketWatchGroup(tr.read_list_of_tickers(tickerTypes = [1], marketTypes= [5, 6, 7, 8, 9, 10, 11, 12], IPO= 0)['ID']), 
            # marketGroupType.Zeraat.value: marketWatchGroup(tr.read_list_of_tickers(tickerTypes = [1], industryTypes= [1], IPO= 0)['ID']), 
            # marketGroupType.EstekhrajFelezat.value: marketWatchGroup(tr.read_list_of_tickers(tickerTypes = [1], industryTypes= [4], IPO= 0)['ID']), 
            # marketGroupType.Nafti.value: marketWatchGroup(tr.read_list_of_tickers(tickerTypes = [1], industryTypes= [11], IPO= 0)['ID']),
            # marketGroupType.Lastik.value: marketWatchGroup(tr.read_list_of_tickers(tickerTypes = [1], industryTypes= [12], IPO= 0)['ID']),
            # marketGroupType.Felezat.value: marketWatchGroup(tr.read_list_of_tickers(tickerTypes = [1], industryTypes= [14], IPO= 0)['ID']), 
            # marketGroupType.SakhtFelezi.value: marketWatchGroup(tr.read_list_of_tickers(tickerTypes = [1], industryTypes= [15], IPO= 0)['ID']),   
            # marketGroupType.DastgaheBarghi.value: marketWatchGroup(tr.read_list_of_tickers(tickerTypes = [1], industryTypes= [17], IPO= 0)['ID']), 
            # marketGroupType.Khodroei.value: marketWatchGroup(tr.read_list_of_tickers(tickerTypes = [1], industryTypes= [19], IPO= 0)['ID']),
            # marketGroupType.Ghandi.value: marketWatchGroup(tr.read_list_of_tickers(tickerTypes = [1], industryTypes= [20], IPO= 0)['ID']), 
            # marketGroupType.TolidBargh.value: marketWatchGroup(tr.read_list_of_tickers(tickerTypes = [1], industryTypes= [22], IPO= 0)['ID']) 
            # marketGroupType.Ghazaei.value: marketWatchGroup(tr.read_list_of_tickers(tickerTypes = [1], industryTypes= [23], IPO= 0)['ID']), 
            # marketGroupType.Daroei.value: marketWatchGroup(tr.read_list_of_tickers(tickerTypes = [1], industryTypes= [24], IPO= 0)['ID']), 
            # marketGroupType.Shimiaei.value: marketWatchGroup(tr.read_list_of_tickers(tickerTypes = [1], industryTypes= [25], IPO= 0)['ID']), 
            # marketGroupType.Peymankari.value: marketWatchGroup(tr.read_list_of_tickers(tickerTypes = [1], industryTypes= [26], IPO= 0)['ID']),
            # marketGroupType.Kashi.value: marketWatchGroup(tr.read_list_of_tickers(tickerTypes = [1], industryTypes= [29], IPO= 0)['ID']),
            # marketGroupType.Simani.value: marketWatchGroup(tr.read_list_of_tickers(tickerTypes = [1], industryTypes= [30], IPO= 0)['ID']), 
            # marketGroupType.KaniNaFelezi.value: marketWatchGroup(tr.read_list_of_tickers(tickerTypes = [1], industryTypes= [31], IPO= 0)['ID']), 
            # marketGroupType.SarmayeGhozari.value: marketWatchGroup(tr.read_list_of_tickers(tickerTypes = [1], industryTypes= [33], IPO= 0)['ID']),  
            # marketGroupType.Banki.value: marketWatchGroup(tr.read_list_of_tickers(tickerTypes = [1], industryTypes= [34], IPO= 0)['ID']), 
            # marketGroupType.HamloNaghl.value: marketWatchGroup(tr.read_list_of_tickers(tickerTypes = [1], industryTypes= [36], IPO= 0)['ID']), 
            # marketGroupType.VaseteghariMali.value: marketWatchGroup(tr.read_list_of_tickers(tickerTypes = [1], industryTypes= [39], IPO= 0)['ID']), 
            # marketGroupType.Bime.value: marketWatchGroup(tr.read_list_of_tickers(tickerTypes = [1], industryTypes= [40], IPO= 0)['ID']), 
            # marketGroupType.Sakhtoman.value: marketWatchGroup(tr.read_list_of_tickers(tickerTypes = [1], industryTypes= [43], IPO= 0)['ID']), 
            # marketGroupType.Rayane.value: marketWatchGroup(tr.read_list_of_tickers(tickerTypes = [1], industryTypes= [45], IPO= 0)['ID']), 
        }

        bigTickersIDList = [35366681030756042, 7745894403636165, 51617145873056483, 
            35425587644337450, 46348559193224090, 63917421733088077, 
            778253364357513, 28320293733348826, 25244329144808274, 
            65883838195688438, 44891482026867833, 2400322364771558, 
            26014913469567886, 22560050433388046, 19040514831923530, 
            22811176775480091, 60610861509165508, 48990026850202503, 
            48753732042176709, 28864540805361867, 20562694899904339]

        self.marketWatchGroups[marketGroupType.BigTickers.value] = marketWatchGroup(bigTickersIDList)


    def get_marketWatchInfo(self, data: dict):

        for thisMarketWatchGroup in self.marketWatchGroups:
            self.marketWatchGroups[thisMarketWatchGroup].reset_values()

        for ID in data:
            for thisMarketWatchGroup in self.marketWatchGroups:
                self.marketWatchGroups[thisMarketWatchGroup].calc_parameters(data, ID)

        marketWatchDict = {}

        for thisMarketWatchGroup in self.marketWatchGroups:
            marketWatchDict[thisMarketWatchGroup] = self.marketWatchGroups[thisMarketWatchGroup].get_marketWatchGroupDict()

        return marketWatchDict
    

class marketWatchGroup():

    def __init__(self, IDList: list) -> None:
        self.IDList = IDList
        self.isTodayFlag = {}


    def reset_values(self) -> None:

        self.Time = 0
        self.tickersNumber = 0
        self.positiveTickersNumber = 0
        self.buyQueueTickersNumber = 0
        self.sellQueueTickersNumber = 0
        self.lastPricePRCsSum = 0
        self.todayPricePECsSum = 0
        self.totalValue = 0
        self.buyQueuesValue = 0
        self.sellQueuesValue = 0
        self.realMoneyEntryValue = 0
        self.demandValue = 0
        self.supplyValue = 0
        self.realPowerLogSum = 0
        self.realBuyValue = 0
        self.realBuyNumber = 0
        self.realSellValue = 0
        self.realSellNumber = 0

    def decimal_cut(self, a) -> float:
        return float('%.2f'%a)


    def calc_parameters(self, data: dict, ID: int) -> None:
        
        if ID in self.IDList:
            
            thisTime: datetime = data[ID][onlineColumns.Time.value]

            if thisTime.hour == 9 and thisTime.minute < 2:
                return

            if ID not in self.isTodayFlag:
                self.isTodayFlag[ID] = False

            if self.isTodayFlag[ID] == False:
                if data[ID][onlineColumns.RealBuyVolume.value]+data[ID][onlineColumns.CorporateBuyVolume.value] <= data[ID][onlineColumns.Volume.value] and\
                    data[ID][onlineColumns.MinPrice.value] != 0 and data[ID][onlineColumns.Volume.value] != 0:
                    self.isTodayFlag[ID] = True

            if self.isTodayFlag[ID] == True:

                if data[ID][onlineColumns.YesterdayPrice.value] == 0:
                    return

                # requaired params
                lastPricePRC = (data[ID][onlineColumns.LastPrice.value]-data[ID][onlineColumns.YesterdayPrice.value])/data[ID][onlineColumns.YesterdayPrice.value] * 100
                todayPricePRC = (data[ID][onlineColumns.TodayPrice.value]-data[ID][onlineColumns.YesterdayPrice.value])/data[ID][onlineColumns.YesterdayPrice.value] * 100
                maxAllowedPRC = (data[ID][onlineColumns.MaxAllowedPrice.value]-data[ID][onlineColumns.YesterdayPrice.value])/data[ID][onlineColumns.YesterdayPrice.value] * 100
                minAllowedPRC = (data[ID][onlineColumns.MinAllowedPrice.value]-data[ID][onlineColumns.YesterdayPrice.value])/data[ID][onlineColumns.YesterdayPrice.value] * 100

                self.tickersNumber += 1

                self.Time = data[ID][onlineColumns.Time.value]

                if lastPricePRC >= 0:
                    self.positiveTickersNumber += 1

                try:
                    if data[ID][onlineColumns.LastPrice.value] == data[ID][onlineColumns.MaxAllowedPrice.value]:
                        self.buyQueueTickersNumber += 1
                        self.buyQueuesValue += data[ID][onlineColumns.DemandPrice1.value] * data[ID][onlineColumns.DemandVolume1.value]
                    
                    elif data[ID][onlineColumns.LastPrice.value] == data[ID][onlineColumns.MinAllowedPrice.value]:
                        self.sellQueueTickersNumber += 1
                        self.sellQueuesValue += data[ID][onlineColumns.SupplyPrice1.value] * data[ID][onlineColumns.SupplyVolume1.value]
                except:
                    pass

                self.lastPricePRCsSum += lastPricePRC / maxAllowedPRC if lastPricePRC >= 0 else -lastPricePRC / minAllowedPRC
                self.todayPricePECsSum += todayPricePRC / maxAllowedPRC if todayPricePRC >= 0 else -todayPricePRC / minAllowedPRC


                self.totalValue += data[ID][onlineColumns.LastPrice.value] * data[ID][onlineColumns.Volume.value]

                try:
                    for i in range(1, 6):
                        if data[ID][f'SupplyPrice{i}'] <= data[ID][onlineColumns.MaxAllowedPrice.value] and data[ID][f'SupplyPrice{i}'] != data[ID][onlineColumns.MinAllowedPrice.value]:
                            self.supplyValue += data[ID][f'SupplyPrice{i}'] * data[ID][f'SupplyVolume{i}']
                        if data[ID][f'DemandPrice{i}'] >= data[ID][onlineColumns.MinAllowedPrice.value] and data[ID][f'DemandPrice{i}'] != data[ID][onlineColumns.MaxAllowedPrice.value]:
                            self.demandValue += data[ID][f'DemandPrice{i}'] * data[ID][f'DemandVolume{i}']
                except:
                    pass

                try:
                    self.realPowerLogSum += log10((data[ID][onlineColumns.RealBuyVolume.value]/data[ID][onlineColumns.RealBuyNumber.value])/(data[ID][onlineColumns.RealSellVolume.value]/data[ID][onlineColumns.RealSellNumber.value]))
                except:
                    pass
                
                self.realBuyValue += data[ID][onlineColumns.RealBuyVolume.value] * data[ID][onlineColumns.LastPrice.value]
                self.realBuyNumber += data[ID][onlineColumns.RealBuyNumber.value]
                self.realSellValue += data[ID][onlineColumns.RealSellVolume.value] * data[ID][onlineColumns.LastPrice.value]
                self.realSellNumber += data[ID][onlineColumns.RealSellNumber.value]

    def get_marketWatchGroupDict(self) -> dict:
        
        if self.tickersNumber == 0:
            return None

        marketWatchGroupDict = {}

        marketWatchGroupDict[onlineColumns.Time.value] = self.Time
        marketWatchGroupDict[onlineColumns.TickersNumber.value] = self.tickersNumber
        marketWatchGroupDict[onlineColumns.PositiveTickersPRC.value] = self.decimal_cut(self.positiveTickersNumber / self.tickersNumber * 100)
        marketWatchGroupDict[onlineColumns.BuyQueueTickersPRC.value] = self.decimal_cut(self.buyQueueTickersNumber / self.tickersNumber * 100)
        marketWatchGroupDict[onlineColumns.SellQueueTickersPRC.value] = self.decimal_cut(self.sellQueueTickersNumber / self.tickersNumber * 100)
        marketWatchGroupDict[onlineColumns.LastPricePRCAverge.value] = self.decimal_cut(self.lastPricePRCsSum / self.tickersNumber * 100)
        marketWatchGroupDict[onlineColumns.TodayPricePRCAverage.value] = self.decimal_cut(self.todayPricePECsSum / self.tickersNumber * 100)
        marketWatchGroupDict[onlineColumns.TotalValue.value] = self.decimal_cut(self.totalValue / 10**10)
        marketWatchGroupDict[onlineColumns.BuyQueuesValue.value] = self.decimal_cut(self.buyQueuesValue / 10**10)
        marketWatchGroupDict[onlineColumns.SellQueuesValue.value] = self.decimal_cut(self.sellQueuesValue / 10**10)
        marketWatchGroupDict[onlineColumns.DemandValue.value] = self.decimal_cut(self.demandValue / 10**10)
        marketWatchGroupDict[onlineColumns.SupplyValue.value] = self.decimal_cut(self.supplyValue / 10**10)
        marketWatchGroupDict[onlineColumns.RealPowerLog.value] = self.realPowerLogSum / self.tickersNumber
        marketWatchGroupDict[onlineColumns.RealBuyValue.value] = self.decimal_cut(self.realBuyValue / 10**10)
        marketWatchGroupDict[onlineColumns.RealBuyNumber.value] = self.realBuyNumber
        marketWatchGroupDict[onlineColumns.RealSellValue.value] = self.decimal_cut(self.realSellValue / 10**10)
        marketWatchGroupDict[onlineColumns.RealSellNumber.value] = self.realSellNumber
    
        return marketWatchGroupDict

            



