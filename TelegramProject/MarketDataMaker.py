from matplotlib.pyplot import legend
from Application.Utility.Indicators.IndicatorService import calculateSma
from Domain.ImportEnums import *
from Infrastructure.Repository.TickerRepository import ticker_repo as tr
from math import inf, log10

class marketWatchDataHandler():

    def __init__(self, marketGroupsList: list, cacheMaxSize= None) -> None:
        self.data = {}
        self.enumColumns = [item.value for item in onlineColumns]
        self.cachMaxSize = cacheMaxSize
        self.marketGroupsList = marketGroupsList
        self.dataSize = 0
      
    def update(self, marketWatchData: dict) -> None:

        for marketGroup in self.marketGroupsList:
            
            if marketGroup not in marketWatchData:
                raise Exception (str(marketGroup) + ' is not in generated marketWatch data')

            if marketWatchData[marketGroup] != None:
                self.update_columns(marketGroup, marketWatchData[marketGroup])

    def update_columns(self, marketGroup: marketGroupType, marketGroup_dict: dict) -> None:

        if marketGroup not in self.data:
            self.data[marketGroup] = {}

        for column in marketGroup_dict:

            if column not in self.enumColumns:
                raise Exception("Column Name Error.")

            if column not in self.data[marketGroup]:
                self.data[marketGroup][column] = [marketGroup_dict[column]]

            else:
                self.data[marketGroup][column].append(marketGroup_dict[column])
                if self.cachMaxSize != None:
                    self.data[marketGroup][column] = self.data[marketGroup][column][-self.cachMaxSize:] 
                # self.dataSize = len(self.data[self.data.keys()[0]][column])

    def time(self, decNum = 1, num= 0) -> dict:
        if num == 0:
            return {marketGroup: self.data[marketGroup][onlineColumns.Time.value][::-1][::decNum][::-1] for marketGroup in self.data}
        else:
            return {marketGroup: self.data[marketGroup][onlineColumns.Time.value][:-decNum*num-1:-1][::decNum][:num][::-1] for marketGroup in self.data}

    def tickersNumber(self, decNum = 1, num= 0) -> dict:
        if num == 0:
            return {marketGroup: self.data[marketGroup][onlineColumns.TickersNumber.value][::-1][::decNum][::-1] for marketGroup in self.data}
        else:
            return {marketGroup: self.data[marketGroup][onlineColumns.TickersNumber.value][:-decNum*num-1:-1][::decNum][:num][::-1] for marketGroup in self.data}

    def positiveTickersPRC(self, decNum = 1, num= 0) -> dict:
        if num == 0:
            return {marketGroup: self.data[marketGroup][onlineColumns.PositiveTickersPRC.value][::-1][::decNum][::-1] for marketGroup in self.data}
        else:
            return {marketGroup: self.data[marketGroup][onlineColumns.PositiveTickersPRC.value][:-decNum*num-1:-1][::decNum][:num][::-1] for marketGroup in self.data}

    
    def buyQueueTickersPRC(self, decNum = 1, num= 0) -> dict:
        if num == 0:
            return {marketGroup: self.data[marketGroup][onlineColumns.BuyQueueTickersPRC.value][::-1][::decNum][::-1] for marketGroup in self.data}
        else:
            return {marketGroup: self.data[marketGroup][onlineColumns.BuyQueueTickersPRC.value][:-decNum*num-1:-1][::decNum][:num][::-1] for marketGroup in self.data}

    def sellQueueTickersPRC(self, decNum = 1, num= 0) -> dict:
        if num == 0:
            return {marketGroup: self.data[marketGroup][onlineColumns.SellQueueTickersPRC.value][::-1][::decNum][::-1] for marketGroup in self.data}
        else:
            return {marketGroup: self.data[marketGroup][onlineColumns.SellQueueTickersPRC.value][:-decNum*num-1:-1][::decNum][:num][::-1] for marketGroup in self.data}

    def lastPricePRCAverge(self, decNum = 1, num= 0) -> dict:
        if num == 0:
            return {marketGroup: self.data[marketGroup][onlineColumns.LastPricePRCAverge.value][::-1][::decNum][::-1] for marketGroup in self.data}
        else:
            return {marketGroup: self.data[marketGroup][onlineColumns.LastPricePRCAverge.value][:-decNum*num-1:-1][::decNum][:num][::-1] for marketGroup in self.data}

    def todayPricePRCAverage(self, decNum = 1, num= 0) -> dict:
        if num == 0:
            return {marketGroup: self.data[marketGroup][onlineColumns.TodayPricePRCAverage.value][::-1][::decNum][::-1] for marketGroup in self.data}
        else:
            return {marketGroup: self.data[marketGroup][onlineColumns.TodayPricePRCAverage.value][:-decNum*num-1:-1][::decNum][:num][::-1] for marketGroup in self.data}

    def totalValue(self, decNum = 1, num= 0) -> dict:
        if num == 0:
            return {marketGroup: self.data[marketGroup][onlineColumns.TotalValue.value][::-1][::decNum][::-1] for marketGroup in self.data}
        else:
            return {marketGroup: self.data[marketGroup][onlineColumns.TotalValue.value][:-decNum*num-1:-1][::decNum][:num][::-1] for marketGroup in self.data}

    def buyQueuesValue(self, decNum = 1, num= 0) -> dict:
        if num == 0:
            return {marketGroup: self.data[marketGroup][onlineColumns.BuyQueuesValue.value][::-1][::decNum][::-1] for marketGroup in self.data}
        else:
            return {marketGroup: self.data[marketGroup][onlineColumns.BuyQueuesValue.value][:-decNum*num-1:-1][::decNum][:num][::-1] for marketGroup in self.data}

    def sellQueuesValue(self, decNum = 1, num= 0) -> dict:
        if num == 0:
            return {marketGroup: self.data[marketGroup][onlineColumns.SellQueuesValue.value][::-1][::decNum][::-1] for marketGroup in self.data}
        else:
            return {marketGroup: self.data[marketGroup][onlineColumns.SellQueuesValue.value][:-decNum*num-1:-1][::decNum][:num][::-1] for marketGroup in self.data}

    def demandValue(self, decNum = 1, num= 0) -> dict:
        if num == 0:
            return {marketGroup: self.data[marketGroup][onlineColumns.DemandValue.value][::-1][::decNum][::-1] for marketGroup in self.data}
        else:
            return {marketGroup: self.data[marketGroup][onlineColumns.DemandValue.value][:-decNum*num-1:-1][::decNum][:num][::-1] for marketGroup in self.data}

    def supplyValue(self, decNum = 1, num= 0) -> dict:
        if num == 0:
            return {marketGroup: self.data[marketGroup][onlineColumns.SupplyValue.value][::-1][::decNum][::-1] for marketGroup in self.data}
        else:
            return {marketGroup: self.data[marketGroup][onlineColumns.SupplyValue.value][:-decNum*num-1:-1][::decNum][:num][::-1] for marketGroup in self.data}

    def realBuyValue(self, decNum = 1, num= 0) -> dict:
        if num == 0:
            return {marketGroup: self.data[marketGroup][onlineColumns.RealBuyValue.value][::-1][::decNum][::-1] for marketGroup in self.data}
        else:
            return {marketGroup: self.data[marketGroup][onlineColumns.RealBuyValue.value][:-decNum*num-1:-1][::decNum][:num][::-1] for marketGroup in self.data}

    def realBuyNumber(self, decNum = 1, num= 0) -> dict:
        if num == 0:
            return {marketGroup: self.data[marketGroup][onlineColumns.RealBuyNumber.value][::-1][::decNum][::-1] for marketGroup in self.data}
        else:
            return {marketGroup: self.data[marketGroup][onlineColumns.RealBuyNumber.value][:-decNum*num-1:-1][::decNum][:num][::-1] for marketGroup in self.data}

    def realSellValue(self, decNum = 1, num= 0) -> dict:
        if num == 0:
            return {marketGroup: self.data[marketGroup][onlineColumns.RealSellValue.value][::-1][::decNum][::-1] for marketGroup in self.data}
        else:
            return {marketGroup: self.data[marketGroup][onlineColumns.RealSellValue.value][:-decNum*num-1:-1][::decNum][:num][::-1] for marketGroup in self.data}

    def realSellNumber(self, decNum = 1, num= 0) -> dict:
        if num == 0:
            return {marketGroup: self.data[marketGroup][onlineColumns.RealSellNumber.value][::-1][::decNum][::-1] for marketGroup in self.data}
        else:
            return {marketGroup: self.data[marketGroup][onlineColumns.RealSellNumber.value][:-decNum*num-1:-1][::decNum][:num][::-1] for marketGroup in self.data}

    def realPowerLog(self, decNum = 1, num= 0) -> dict:

        realpowerlog = {}
        for marketGroup in self.data:
            if num == 0:
                thisRealPowerLog = self.data[marketGroup][onlineColumns.RealPowerLog.value][::-1][::decNum][::-1]
            else:
                thisRealPowerLog = self.data[marketGroup][onlineColumns.RealPowerLog.value][:-decNum*num-1:-1][::decNum][:num][::-1]
            realpowerlog[marketGroup] = [10**thisRealPowerLog[i] for i in range(len(thisRealPowerLog))]
        return realpowerlog

    def realPower(self, decNum = 1, num= 0) -> dict:
        
        realBuyValue = self.realBuyValue(decNum, num)
        realBuyNumber = self.realBuyNumber(decNum, num)
        realSellValue = self.realSellValue(decNum, num)
        realSellNumber = self.realSellNumber(decNum, num)

        realPower = {}

        for marketGroup in realBuyValue:
            realPower[marketGroup] = []
            for i in range(len(realBuyValue[marketGroup])):
                try:
                    thisRealPower = (realBuyValue[marketGroup][i]/realBuyNumber[marketGroup][i])/(realSellValue[marketGroup][i]/realSellNumber[marketGroup][i])
                except:
                    thisRealPower = 1
                realPower[marketGroup].append(thisRealPower)

        return realPower

    # Moving Averges
    def lastPricePRCAverge_MA(self, decNum = 1, num= 0, maLength= 50) -> dict:

        lastPricePRCAverge = self.lastPricePRCAverge(decNum, num)

        lastPricePRCAvergeMA = {}
        for marketGroup in lastPricePRCAverge:
            lastPricePRCAvergeMA[marketGroup] = calculateSma(lastPricePRCAverge[marketGroup], maLength, True)

        return lastPricePRCAvergeMA

    def lastPricePRCAverge_MA_dif(self, decNum = 1, num= 0, maLength: int = 50) -> dict:

        if num == 0:
            requieredLength = 0
        else:
            requieredLength = num+maLength-1

        lastPricePRCAverge = self.lastPricePRCAverge(decNum, requieredLength)
        lastPricePRCAvergeMA = self.lastPricePRCAverge_MA(decNum, requieredLength, maLength)

        lastPricePRCAvergeMADif = {}
        for marketGroup in lastPricePRCAverge: 
            if num == 0:
                lastPricePRCAvergeMADif[marketGroup] = [lastPricePRCAverge[marketGroup][i]-lastPricePRCAvergeMA[marketGroup][i] for i in range(len(lastPricePRCAverge[marketGroup]))]
            else:
                lastPricePRCAvergeMADif[marketGroup] = [lastPricePRCAverge[marketGroup][i]-lastPricePRCAvergeMA[marketGroup][i] for i in range(-1, -min(num, len(lastPricePRCAverge[marketGroup]))-1, -1)][::-1]

        return lastPricePRCAvergeMADif

    # Dif
    def get_TimeDif(self, decNum = 1, num= 0) -> dict:
        '''returns TimeDif in seconds'''

        time = self.time(decNum, num)
        timeDif = {}

        for marketGroup in time:
            timeDif[marketGroup] = []
            for i in range(-1, -len(time[marketGroup])-1, -1):
                if abs(i) + 1 <= len(time[marketGroup]):   
                    thistimeDif = max((time[marketGroup][i]-time[marketGroup][i-1]).total_seconds(), 0)
                else:
                    thistimeDif = 0
                timeDif[marketGroup].append(thistimeDif)
            if num == 0:
                timeDif[marketGroup] = timeDif[marketGroup][::-1]
            else:
                timeDif[marketGroup] = timeDif[marketGroup][::-1][-num:]

        return timeDif

    def totalValueDif(self, decNum = 1, num= 0, length = 1) -> dict:

        if num == 0:
            requieredLength = 0
        else:
            requieredLength = num+length

        totalValue = self.totalValue(decNum, requieredLength)
        totalValueDif = {}
        
        for marketGroup in totalValue:
            totalValueDif[marketGroup] = []
            for i in range(-1, -len(totalValue[marketGroup])-1, -1):
                if abs(i) + length <= len(totalValue[marketGroup]):   
                    thistotalValueDif = max(totalValue[marketGroup][i]-totalValue[marketGroup][i-length], 0)
                else:
                    thistotalValueDif = 0
                totalValueDif[marketGroup].append(thistotalValueDif)
            if num == 0:
                totalValueDif[marketGroup] = totalValueDif[marketGroup][::-1]
            else:
                totalValueDif[marketGroup] = totalValueDif[marketGroup][::-1][-num:]

        return totalValueDif

    # def totalValueDif_MA(self, decNum = 1, num= 0, maLength= 50) -> dict:

    #     lastPricePRCAverge = self.totalValue(decNum, num)

    #     lastPricePRCAvergeMA = {}
    #     for marketGroup in lastPricePRCAverge:
    #         lastPricePRCAvergeMA[marketGroup] = calculateSma(lastPricePRCAverge[marketGroup], maLength, True)

    #     return lastPricePRCAvergeMA

    def realPowerDif(self, decNum = 1, num= 0, length: int = 1) -> dict:
        
        if num == 0:
            requieredLength = 0
        else:
            requieredLength = num+length

        realBuyValue = self.realBuyValue(decNum, requieredLength)
        realBuyNumber = self.realBuyNumber(decNum, requieredLength)
        realSellValue = self.realSellValue(decNum, requieredLength)
        realSellNumber = self.realSellNumber(decNum, requieredLength)

        realPowerDif = {}

        for marketGroup in realBuyValue:
            realPowerDif[marketGroup] = []
            for i in range(-1, -len(realBuyValue[marketGroup])-1, -1):
                if abs(i) + length <= len(realBuyValue[marketGroup]):
                    try:        
                        thisRealPowerDif = \
                        ((realBuyValue[marketGroup][i]-realBuyValue[marketGroup][i-length])/
                        (realBuyNumber[marketGroup][i]-realBuyNumber[marketGroup][i-length]))/\
                        ((realSellValue[marketGroup][i]-realSellValue[marketGroup][i-length])/
                        (realSellNumber[marketGroup][i]-realSellNumber[marketGroup][i-length]))
                    except:
                        thisRealPowerDif = 1
                else:
                    try:        
                        thisRealPowerDif = \
                        (realBuyValue[marketGroup][i]/realBuyNumber[marketGroup][i])/\
                        (realSellValue[marketGroup][i]/realSellNumber[marketGroup][i])
                    except:
                        thisRealPowerDif = 1
                if thisRealPowerDif <= 0:
                    thisRealPowerDif = 1
                realPowerDif[marketGroup].append(thisRealPowerDif)
            if num == 0:
                realPowerDif[marketGroup] = realPowerDif[marketGroup][::-1]
            else:
                realPowerDif[marketGroup] = realPowerDif[marketGroup][::-1][-num:]
        return realPowerDif