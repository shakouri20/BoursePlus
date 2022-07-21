from  datetime import datetime
from math import log10
from Application.Services.ReadData.ReadOnline.OnlineDataHandler import presentData
from Domain.Enums.MarketGroups import marketGroupType
from Infrastructure.Repository.TickerRepository import ticker_repo
from Domain.ImportEnums import *

class marketWatchDataGenerator():

    def __init__(self) -> None:
        
        tr = ticker_repo()

        self.groups = {
            
            marketGroupType.TotalMarket.value: marketGroup(tr.read_list_of_tickers(tickerTypes = [1], IPO= 0)['ID']), 
            # marketGroupType.Bourse.value: marketGroup(tr.read_list_of_tickers(tickerTypes = [1], marketTypes= [1, 2, 3, 4], IPO= 0)['ID']), 
            # marketGroupType.FaraBourse.value: marketGroup(tr.read_list_of_tickers(tickerTypes = [1], marketTypes= [5, 6, 7, 8, 9, 10, 11, 12], IPO= 0)['ID']), 
            # marketGroupType.Zeraat.value: marketGroup(tr.read_list_of_tickers(tickerTypes = [1], industryTypes= [1], IPO= 0)['ID']), 
            # marketGroupType.EstekhrajFelezat.value: marketGroup(tr.read_list_of_tickers(tickerTypes = [1], industryTypes= [4], IPO= 0)['ID']), 
            # marketGroupType.Nafti.value: marketGroup(tr.read_list_of_tickers(tickerTypes = [1], industryTypes= [11], IPO= 0)['ID']),
            # marketGroupType.Lastik.value: marketGroup(tr.read_list_of_tickers(tickerTypes = [1], industryTypes= [12], IPO= 0)['ID']),
            # marketGroupType.Felezat.value: marketGroup(tr.read_list_of_tickers(tickerTypes = [1], industryTypes= [14], IPO= 0)['ID']), 
            # marketGroupType.SakhtFelezi.value: marketGroup(tr.read_list_of_tickers(tickerTypes = [1], industryTypes= [15], IPO= 0)['ID']),   
            # marketGroupType.DastgaheBarghi.value: marketGroup(tr.read_list_of_tickers(tickerTypes = [1], industryTypes= [17], IPO= 0)['ID']), 
            # marketGroupType.Khodroei.value: marketGroup(tr.read_list_of_tickers(tickerTypes = [1], industryTypes= [19], IPO= 0)['ID']),
            # marketGroupType.Ghandi.value: marketGroup(tr.read_list_of_tickers(tickerTypes = [1], industryTypes= [20], IPO= 0)['ID']), 
            # marketGroupType.TolidBargh.value: marketGroup(tr.read_list_of_tickers(tickerTypes = [1], industryTypes= [22], IPO= 0)['ID']) 
            # marketGroupType.Ghazaei.value: marketGroup(tr.read_list_of_tickers(tickerTypes = [1], industryTypes= [23], IPO= 0)['ID']), 
            # marketGroupType.Daroei.value: marketGroup(tr.read_list_of_tickers(tickerTypes = [1], industryTypes= [24], IPO= 0)['ID']), 
            # marketGroupType.Shimiaei.value: marketGroup(tr.read_list_of_tickers(tickerTypes = [1], industryTypes= [25], IPO= 0)['ID']), 
            # marketGroupType.Peymankari.value: marketGroup(tr.read_list_of_tickers(tickerTypes = [1], industryTypes= [26], IPO= 0)['ID']),
            # marketGroupType.Kashi.value: marketGroup(tr.read_list_of_tickers(tickerTypes = [1], industryTypes= [29], IPO= 0)['ID']),
            # marketGroupType.Simani.value: marketGroup(tr.read_list_of_tickers(tickerTypes = [1], industryTypes= [30], IPO= 0)['ID']), 
            # marketGroupType.KaniNaFelezi.value: marketGroup(tr.read_list_of_tickers(tickerTypes = [1], industryTypes= [31], IPO= 0)['ID']), 
            # marketGroupType.SarmayeGhozari.value: marketGroup(tr.read_list_of_tickers(tickerTypes = [1], industryTypes= [33], IPO= 0)['ID']),  
            # marketGroupType.Banki.value: marketGroup(tr.read_list_of_tickers(tickerTypes = [1], industryTypes= [34], IPO= 0)['ID']), 
            # marketGroupType.HamloNaghl.value: marketGroup(tr.read_list_of_tickers(tickerTypes = [1], industryTypes= [36], IPO= 0)['ID']), 
            # marketGroupType.VaseteghariMali.value: marketGroup(tr.read_list_of_tickers(tickerTypes = [1], industryTypes= [39], IPO= 0)['ID']), 
            # marketGroupType.Bime.value: marketGroup(tr.read_list_of_tickers(tickerTypes = [1], industryTypes= [40], IPO= 0)['ID']), 
            # marketGroupType.Sakhtoman.value: marketGroup(tr.read_list_of_tickers(tickerTypes = [1], industryTypes= [43], IPO= 0)['ID']), 
            # marketGroupType.Rayane.value: marketGroup(tr.read_list_of_tickers(tickerTypes = [1], industryTypes= [45], IPO= 0)['ID']), 
        }

        bigTickersIDList = [35366681030756042, 7745894403636165, 51617145873056483, 
            35425587644337450, 46348559193224090, 63917421733088077, 
            778253364357513, 28320293733348826, 25244329144808274, 
            65883838195688438, 44891482026867833, 2400322364771558, 
            26014913469567886, 22560050433388046, 19040514831923530, 
            22811176775480091, 60610861509165508, 48990026850202503, 
            48753732042176709, 28864540805361867, 20562694899904339]

        self.groups[marketGroupType.BigTickers.value] = marketGroup(bigTickersIDList)


    def get_marketWatchInfo(self, data: dict):

        for thisMarketWatchGroup in self.groups:
            self.groups[thisMarketWatchGroup].reset_values()

        for ID in data:
            for thisMarketWatchGroup in self.groups:
                self.groups[thisMarketWatchGroup].calc_parameters(data, ID)

        marketWatchDict = {}

        for thisMarketWatchGroup in self.groups:
            marketWatchDict[thisMarketWatchGroup] = self.groups[thisMarketWatchGroup].get_marketWatchGroupDict()

        return marketWatchDict
    
class marketGroup():

    def __init__(self, IDList: list) -> None:
        self.IDList = IDList

    def update(self, presentDataDict: dict[presentData]) -> None:

        tickersNumber = 0
        positiveTickersNumber = 0
        buyQueueTickersNumber = 0
        sellQueueTickersNumber = 0
        lastPricePrcSum = 0
        todayPricePrcSum = 0
        totalValue = 0
        buyQueuesValue = 0
        sellQueuesValue = 0
        realMoneyEntryValue = 0
        demandValue = 0
        supplyValue = 0
        realPowerLogSum = 0
        realBuyValue = 0
        realBuyNumber = 0
        realSellValue = 0
        realSellNumber = 0

        for ID in presentDataDict:

            if ID in self.IDList:

                try:
                
                    tickerPresentData: presentData = presentDataDict[ID]

                    lastPricePRC = (tickerPresentData.LastPrice-tickerPresentData.YesterdayPrice)/tickerPresentData.YesterdayPrice * 100
                    todayPricePRC = (tickerPresentData.TodayPrice-tickerPresentData.YesterdayPrice)/tickerPresentData.YesterdayPrice * 100


                    if lastPricePRC >= 0:
                        positiveTickersNumber += 1

                    if tickerPresentData.LastPrice == tickerPresentData.MaxAllowedPrice:
                        buyQueueTickersNumber += 1
                        buyQueuesValue += tickerPresentData.DemandPrice1 * tickerPresentData.DemandVolume1
                    
                    elif tickerPresentData.LastPrice == tickerPresentData.MinAllowedPrice:
                        sellQueueTickersNumber += 1
                        sellQueuesValue += tickerPresentData.SupplyPrice1 * tickerPresentData.SupplyVolume1

                    lastPricePrcSum += lastPricePRC
                    todayPricePrcSum += todayPricePRC

                    totalValue += tickerPresentData.TodayPrice * tickerPresentData.Volume
                    
                    tickersNumber += 1

                    for i in range(1, 6):
                        try:
                            if getattr(tickerPresentData, f'SupplyPrice{i}') <= tickerPresentData.MaxAllowedPrice and getattr(tickerPresentData, f'SupplyPrice{i}') != tickerPresentData.MinAllowedPrice:
                                supplyValue += getattr(tickerPresentData, f'SupplyPrice{i}') * getattr(tickerPresentData, f'SupplyVolume{i}')
                            if getattr(tickerPresentData, f'DemandPrice{i}') >= tickerPresentData.MinAllowedPrice and getattr(tickerPresentData, f'DemandPrice{i}') != tickerPresentData.MaxAllowedPrice:
                                demandValue += getattr(tickerPresentData, f'DemandPrice{i}') * getattr(tickerPresentData, f'DemandVolume{i}')
                        except:
                            pass

                    try:
                        realPowerLogSum += log10((tickerPresentData.RealBuyVolume/tickerPresentData.RealBuyNumber)/(tickerPresentData.RealSellVolume/tickerPresentData.RealSellNumber))
                    except:
                        pass
                    
                    realBuyValue += tickerPresentData.RealBuyVolume * tickerPresentData.TodayPrice
                    realBuyNumber += tickerPresentData.RealBuyNumber
                    realSellValue += tickerPresentData.RealSellVolume * tickerPresentData.TodayPrice
                    realSellNumber += tickerPresentData.RealSellNumber
                
                except:
                    pass

        marketWatchGroupDict = {}

        marketWatchGroupDict.TickersNumber = self.tickersNumber
        marketWatchGroupDict.PositiveTickersPRC = round(self.positiveTickersNumber / self.tickersNumber * 100, 2)
        marketWatchGroupDict.BuyQueueTickersPRC = round(self.buyQueueTickersNumber / self.tickersNumber * 100, 2)
        marketWatchGroupDict.SellQueueTickersPRC = round(self.sellQueueTickersNumber / self.tickersNumber * 100, 2)
        marketWatchGroupDict.LastPricePRCAverge = round(self.lastPricePrcSum / self.tickersNumber * 100, 2)
        marketWatchGroupDict.TodayPricePRCAverage = round(self.todayPricePrcSum / self.tickersNumber * 100, 2)
        marketWatchGroupDict.TotalValue = round(self.totalValue / 10**10, 2)
        marketWatchGroupDict.BuyQueuesValue = round(self.buyQueuesValue / 10**10, 2)
        marketWatchGroupDict.SellQueuesValue = round(self.sellQueuesValue / 10**10, 2)
        marketWatchGroupDict.DemandValue = round(self.demandValue / 10**10, 2)
        marketWatchGroupDict.SupplyValue = round(self.supplyValue / 10**10, 2)
        marketWatchGroupDict.RealPowerLog = self.realPowerLogSum / self.tickersNumber
        marketWatchGroupDict.RealBuyValue = round(self.realBuyValue / 10**10, 2)
        marketWatchGroupDict.RealBuyNumber = self.realBuyNumber
        marketWatchGroupDict.RealSellValue = round(self.realSellValue / 10**10, 2)
        marketWatchGroupDict.RealSellNumber = self.realSellNumber
    
            



