from math import log10
from Application.Services.OfflineLab.ResistanceSupport import calc_resistance_support
from Application.Utility.AdvancedPlot import advancedPlot
from Application.Utility.DateConverter import *
from Application.Utility.Indicators.IndicatorService import *
from Domain.Enums.QueryOutPutType import queryOutPutType
from Domain.Enums.TableType import tableType
from Domain.Enums.MiddlewareOrder import middlewareOrder
from Domain.Models.MiddlewareOffline import middlewareOffline
from Domain.Models.TickerOfflineData import tickersGroupData, tickerOfflineData
from Domain.Models.TradeInfo import tradeInfo
from Infrastructure.Repository.OfflineDataRepository import offlineData_repo
from Infrastructure.Repository.TickerRepository import ticker_repo
import pandas as pd
import matplotlib.pyplot as plt
import datetime
from ta.momentum import *
from ta.volatility import *
import requests, json, time
import itertools
import mplfinance as mpf
import subprocess, os

transactionFee = 1.25

class offlineLab:

    def __init__(self, IDs) -> None:
        self.trades = []
        self.IDs = IDs

    def set_buy_middleweres(self, buyMiddlewares):
        self.buyMiddlewares: list[middlewareOffline] = []
        self.buyWeights: list = []
        for thisTuple in buyMiddlewares:
            self.buyMiddlewares.append(thisTuple[0])
            self.buyWeights.append(thisTuple[1])

    def set_sell_middleweres(self, sellMiddlewares):
        self.sellMiddlewares: list[middlewareOffline] = []
        self.sellWeights: list = []
        for thisTuple in sellMiddlewares:
            self.sellMiddlewares.append(thisTuple[0])
            self.sellWeights.append(thisTuple[1])

    def set_min_buy_score(self, minBuyScore):
        self.minBuyScore = minBuyScore
        if minBuyScore < 1 or minBuyScore > 100:
            raise Exception

    def set_min_sell_score(self, minSellScore):
        self.minSellScore = minSellScore
        if minSellScore < 1 or minSellScore > 100:
            raise Exception

    def read_data(self, fromDate, toDate, timeFrame, pastDataNumber, getPriceRange= True, getOrdersBoard= True, getTickersGroupData= True):

        self.timeFrame = timeFrame

        print('Reading tickers data from db...', end= '')
        finalData = offlineData_repo().read_OfflineData_in_time_range(
            'all', table= tableType.OfflineData.value, IDList= self.IDs,
                fromDate= jalali_to_gregorian(fromDate), toDate= jalali_to_gregorian(toDate))

        pastData = offlineData_repo().read_last_N_OfflineData_by_date(
            pastDataNumber, self.IDs, jalali_to_gregorian(fromDate), outPutType= queryOutPutType.DictDict) 
        print(' Done.')

        self.tickersData: dict[tickerOfflineData] = {}

        if self.timeFrame == '1D':
            for ID in finalData:
                if ID in pastData:
                    for column in finalData[ID]:
                        finalData[ID][column] = pastData[ID][column] + finalData[ID][column]
                self.tickersData[ID] = tickerOfflineData(finalData[ID], pastDataNumber)

        elif self.timeFrame in ['1','5','10','15','30','60','180']:

            for ID in finalData:
                print(ID)
                days: list[datetime.date] = finalData[ID]['Time']

                webPricesData: dict = self.get_prices_data(ticker_repo().read_by_ID(ID)['IR1'], days, self.timeFrame)

                self.apply_intersection(finalData[ID], webPricesData)

                for column in finalData[ID]:
                    if ID in pastData:
                        finalData[ID][column] = pastData[ID][column] + finalData[ID][column]
                        pastDataNumber = len(pastData[ID][column])
                    else:
                        pastDataNumber = 0

                self.tickersData[ID] = tickerOfflineData(finalData[ID], pastDataNumber)
                tickerData: tickerOfflineData = self.tickersData[ID]

                tickerData.onlineData.time = webPricesData['t']
                tickerData.onlineData.openPrice = webPricesData['o']
                tickerData.onlineData.closePrice = webPricesData['c']
                tickerData.onlineData.highPrice = webPricesData['h']
                tickerData.onlineData.lowPrice = webPricesData['l']
                tickerData.onlineData.volume = webPricesData['v']

                if len(tickerData.dateTime) != len(tickerData.onlineData.time):
                    raise Exception('len(days) != len(webTime)')

                for m in range(len(tickerData.onlineData.time)):
                    today = tickerData.onlineData.time[m][0].date()
                    # print('', gregorian_to_jalali(today.strftime("%Y-%m-%d")), end= '\r')
                    # price range
                    if getPriceRange:
                        if tickerData.priceData.minAllowedPrice[m] == None:
                            allowedPrice = self.get_daily_allowed_price(ID, today)
                            offlineData_repo().write_price_range(ID, today.strftime("%Y-%m-%d"), allowedPrice['Min'], allowedPrice['Max'])
                            tickerData.priceData.minAllowedPrice[m] = allowedPrice['Min']
                            tickerData.priceData.maxAllowedPrice[m] = allowedPrice['Max']
                    # orders board
                    if getOrdersBoard:
                        obData: list = self.get_ordersBoard_data(ID, today)
                        lastRowNumber = 0
                        row1Items = vars(tickerData.onlineData.ordersBoard.row1)
                        row2Items = vars(tickerData.onlineData.ordersBoard.row2)
                        row3Items = vars(tickerData.onlineData.ordersBoard.row3)
                        for item in row1Items:
                            row1Items[item].append([])
                        for item in row2Items:
                            row2Items[item].append([])
                        for item in row3Items:
                            row3Items[item].append([])
                        
                        for thisTime in tickerData.onlineData.time[m]:
                            for i in range(lastRowNumber, len(obData)):
                                thisTimeInt = int(thisTime.strftime('%H%M%S'))
                                if thisTimeInt < obData[i]['hEven'] or i == len(obData)-1:
                                    rowsCheck = []
                                    for k in range(1, 4):
                                        for j in range(i-1, -1, -1):
                                            if obData[j]['number'] == k:
                                                rowsCheck.append(k)
                                                if k == 1:
                                                    tickerData.onlineData.ordersBoard.row1.demandPrice[m].append(obData[j]['pMeDem'])
                                                    tickerData.onlineData.ordersBoard.row1.supplyPrice[m].append(obData[j]['pMeOf'])
                                                    tickerData.onlineData.ordersBoard.row1.demandNumber[m].append(obData[j]['zOrdMeDem'])
                                                    tickerData.onlineData.ordersBoard.row1.supplyNumber[m].append(obData[j]['zOrdMeOf'])
                                                    tickerData.onlineData.ordersBoard.row1.demandVolume[m].append(obData[j]['qTitMeDem'])
                                                    tickerData.onlineData.ordersBoard.row1.supplyVolume[m].append(obData[j]['qTitMeOf'])
                                                    break
                                                elif k == 2:
                                                    tickerData.onlineData.ordersBoard.row2.demandPrice[m].append(obData[j]['pMeDem'])
                                                    tickerData.onlineData.ordersBoard.row2.supplyPrice[m].append(obData[j]['pMeOf'])
                                                    tickerData.onlineData.ordersBoard.row2.demandNumber[m].append(obData[j]['zOrdMeDem'])
                                                    tickerData.onlineData.ordersBoard.row2.supplyNumber[m].append(obData[j]['zOrdMeOf'])
                                                    tickerData.onlineData.ordersBoard.row2.demandVolume[m].append(obData[j]['qTitMeDem'])
                                                    tickerData.onlineData.ordersBoard.row2.supplyVolume[m].append(obData[j]['qTitMeOf'])
                                                    break
                                                elif k == 3:
                                                    tickerData.onlineData.ordersBoard.row3.demandPrice[m].append(obData[j]['pMeDem'])
                                                    tickerData.onlineData.ordersBoard.row3.supplyPrice[m].append(obData[j]['pMeOf'])
                                                    tickerData.onlineData.ordersBoard.row3.demandNumber[m].append(obData[j]['zOrdMeDem'])
                                                    tickerData.onlineData.ordersBoard.row3.supplyNumber[m].append(obData[j]['zOrdMeOf'])
                                                    tickerData.onlineData.ordersBoard.row3.demandVolume[m].append(obData[j]['qTitMeDem'])
                                                    tickerData.onlineData.ordersBoard.row3.supplyVolume[m].append(obData[j]['qTitMeOf'])
                                                    break
                                    if sum(rowsCheck) != 6:
                                        raise Exception
                                    lastRowNumber = i
                                    break
                            else:
                                raise Exception
                        if len(tickerData.onlineData.ordersBoard.row1.demandVolume[m]) != len(tickerData.onlineData.time[m]):
                            raise Exception
                        
                    tickerData.onlineData.create_new_variables()

            self.tickersGroupData = {}
            print('Reading market data...', end= '')
            allDays: list[datetime.date] = []
            for ID in self.tickersData:
                tickerData: tickerOfflineData = self.tickersData[ID]
                for day in tickerData.dateTime:
                    if day not in allDays:
                        allDays.append(day)
            for day in allDays:
                if getTickersGroupData:
                        self.tickersGroupData[day] = tickersGroupData(1234, day)
                else:
                    self.tickersGroupData[day] = 0


            print(' Done.')

        else:
            raise Exception
        x = 1
  
    def m_run(self):

            trades: list[tradeInfo] = []

            for ID in self.tickersData:

                tickerData: tickerOfflineData = self.tickersData[ID]
                tickerName = ticker_repo().read_by_ID(ID)['FarsiTicker']

                for i in range(len(tickerData.dateTime)):
                    todaytickersGroupData: tickersGroupData = self.tickersGroupData[tickerData.dateTime[i]]
                    for j in range(len(tickerData.onlineData.time[i])):
                        ############################ buy middlewares run ############################
                        if (len(trades) == 0 or trades[-1].sellTime != None): #  and i != len(tickerData.dateTime)-1
                            scores = []

                            for middleware in self.buyMiddlewares:
                                (decision, score, price, buyType) = middleware.process(ID, tickerData, i, tickerData.onlineData, j, todaytickersGroupData)
                                if decision == middlewareOrder.Delete:
                                    break
                                elif decision == middlewareOrder.Buy:
                                    self.buy(trades, ID, tickerName, price, tickerData.onlineData.time[i][j], middleware.name, buyType)
                                    break
                                elif decision == middlewareOrder.Continue:
                                    scores.append(score)
                                else:
                                    raise Exception('middleware Order can not be Sell')

                            if decision == middlewareOrder.Continue:
                                if len(scores) != len(self.buyMiddlewares):
                                    raise Exception
                                scoresSOP = [scores[i]*self.buyWeights[i] for i in range(len(self.buyWeights))]
                                finalScore = sum(scoresSOP)/sum(self.buyWeights)
                                if finalScore >= self.minBuyScore:
                                    self.buy(trades, ID, tickerName, price, tickerData.onlineData.time[i][j], 'None', 'None')
                        ############################ sell middlewares run ############################
                        else:
                            
                            scores = []

                            for middleware in self.sellMiddlewares:
                                (decision, score, price, sellType) = middleware.process(ID, tickerData, i, tickerData.onlineData, j, todaytickersGroupData)
                                if decision == middlewareOrder.Delete:
                                    break
                                elif decision == middlewareOrder.Sell:
                                    self.sell(trades[-1], price, tickerData.onlineData.time[i][j], self.sellMiddlewares, middleware.name, sellType)
                                    break
                                elif decision == middlewareOrder.Continue:
                                    scores.append(score)
                                else:
                                    raise Exception('middleware Order can not be Buy')

                            if decision == middlewareOrder.Continue:
                                if len(scores) != len(self.sellMiddlewares):
                                    raise Exception
                                scoresSOP = [scores[i]*self.sellWeights[i] for i in range(len(self.sellWeights))]
                                finalScore = sum(scoresSOP)/sum(self.sellWeights)
                                if finalScore >= self.minSellScore:
                                    self.sell(trades[-1], price, tickerData.onlineData.time[i][j], self.sellMiddlewares, 'None', 'None')

                if trades != [] and trades[-1].sellTime == None:
                    self.sell(trades[-1], price, tickerData.onlineData.time[i][j], self.sellMiddlewares, 'None', 'None')

            sortedTrades = self.sort_trades_by_date(trades)
            return sortedTrades 
    
    def d_run(self):

            trades: list[tradeInfo] = []

            for ID in self.tickersData:

                tickerData: tickerOfflineData = self.tickersData[ID]
                tickerName = ticker_repo().read_by_ID(ID)['FarsiTicker']

                for i in range(len(tickerData.dateTime)):
                    ############################ buy middlewares run ############################
                    if (len(trades) == 0 or trades[-1].sellTime != None):
                        if i != len(tickerData.dateTime)-1:
                            scores = []

                            for middleware in self.buyMiddlewares:
                                (decision, score, price) = middleware.process(ID, tickerData, i)
                                if decision == middlewareOrder.Delete:
                                    break
                                elif decision == middlewareOrder.Buy:
                                    self.buy(trades, ID, tickerName, price, tickerData.dateTime[i])
                                    break
                                elif decision == middlewareOrder.Continue:
                                    scores.append(score)
                                else:
                                    raise Exception('middleware Order can not be Sell')

                            if decision == middlewareOrder.Continue:
                                if len(scores) != len(self.buyMiddlewares):
                                    raise Exception
                                scoresSOP = [scores[i]*self.buyWeights[i] for i in range(len(self.buyWeights))]
                                finalScore = sum(scoresSOP)/sum(self.buyWeights)
                                if finalScore >= self.minBuyScore:
                                    self.buy(trades, ID, tickerName, price, tickerData.dateTime[i])
                    ############################ sell middlewares run ############################
                    else:
                        scores = []

                        for middleware in self.sellMiddlewares:
                            (decision, score, price) = middleware.process(ID, tickerData, i)
                            if decision == middlewareOrder.Delete:
                                break
                            elif decision == middlewareOrder.Sell:
                                self.sell(trades[-1], price, tickerData.dateTime[i], self.sellMiddlewares)
                                break
                            elif decision == middlewareOrder.Continue:
                                scores.append(score)
                            else:
                                raise Exception('middleware Order can not be Buy')

                        if decision == middlewareOrder.Continue:
                            if len(scores) != len(self.sellMiddlewares):
                                raise Exception
                            scoresSOP = [scores[i]*self.sellWeights[i] for i in range(len(self.sellWeights))]
                            finalScore = sum(scoresSOP)/sum(self.sellWeights)
                            if finalScore >= self.minSellScore:
                                self.sell(trades[-1], price, tickerData.dateTime[i], self.sellMiddlewares)

                if trades != [] and trades[-1].sellTime == None:
                    self.sell(trades[-1], price, tickerData.dateTime[i], self.sellMiddlewares)
            sortedTrades = self.sort_trades_by_date(trades)
            return sortedTrades 

    def strategy_backTest(self, buyMiddlewares, sellMiddlewares, minBuyScore, minSellScore, maxPortfolioTickerNumber):

        self.set_buy_middleweres(buyMiddlewares)
        self.set_sell_middleweres(sellMiddlewares)
        self.set_min_buy_score(minBuyScore)
        self.set_min_sell_score(minSellScore)
        
        print('Running backTest...',  end= ' ')
        if self.timeFrame == '1D':
            self.trades = self.d_run()
        else:
            self.trades = self.m_run()
        print('Done.')
        tickerTradesDict = self.create_ticker_trades_dict(self.trades)
        realTrades = self.create_real_trades(self.trades, maxPortfolioTickerNumber)
        self.tickerRealTradesDict = self.create_ticker_trades_dict(realTrades)

        print('Creating excel...',  end= ' ')
        self.create_excel(self.trades, tickerTradesDict, 'Trades', 1)
        self.create_excel(realTrades, self.tickerRealTradesDict, 'RealTrades', maxPortfolioTickerNumber)
        subprocess.Popen(["C:\\Program Files\\Microsoft Office\\Root\\Office16\\EXCEL.EXE", "/t", os.getcwd()+'\Trades.xlsx'])
        # subprocess.Popen(["C:\\Program Files\\Microsoft Office\\Root\\Office16\\EXCEL.EXE", "/t", os.getcwd()+'\RealTrades.xlsx'])


        print('Done.')

    def get_prices_data(self, IR, days: list[datetime.date], timeFrame: str) -> dict:
        startTime = int(time.mktime(days[0].timetuple()))
        now = int(time.mktime(datetime.datetime.now().timetuple()))
        endTime = min(now, int(time.mktime(days[-1].timetuple())) + 82800)
        url = f"https://rlcchartapi.tadbirrlc.com/ChartData/history?symbol={IR}_0&resolution={timeFrame}&from={startTime}&to={endTime}"
        while True:
            try:
                headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36'}
                response = requests.get(url, timeout=1, headers= headers)
                break
            except:
                time.sleep(2)
                pass
        data = json.loads(response.text) 
        
        for i in range(len(data['t'])):
            data['t'][i] =  datetime.datetime.fromtimestamp(data['t'][i])

        self.classify_web_data(data)

        for i in range(len(data['t'])):
            number = 0
            for j in range(len(data['t'][i])):
                if j == 0:
                    if data['t'][i][j].hour == 8 and data['t'][i][j].minute < 30:
                        addedMinutes = 60
                    else:
                        addedMinutes = 0
                else:
                    if data['v'][i][j] < data['v'][i][j-1]:
                        number += 1
                data['t'][i][j] += datetime.timedelta(minutes= addedMinutes)

            if number / len(data['t'][i]) < 0.5:
                volume = [0 for _ in range(len(data['t'][i]))]
                for j in range(1, len(data['t'][i])):
                    volume[j] = data['v'][i][j]-data['v'][i][j-1]
                data['v'][i] = volume
        return data

    @staticmethod  
    def get_ordersBoard_data(ID, day: datetime.date):
        day = day.strftime("%Y%m%d")
        url = f"http://cdn.tsetmc.com/api/BestLimits/{ID}/{day}"
        while True:
            try:
                headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36'}
                response = requests.get(url, timeout=1, headers= headers)
                break
            except:
                pass
                # print(f'OrdersBoard Web Error')
                # time.sleep(0.5)
        return json.loads(response.text)['bestLimitsHistory']

    @staticmethod
    def get_daily_allowed_price(ID, day: datetime.date):
        day = day.strftime("%Y%m%d")
        url = f"http://cdn.tsetmc.com/api/MarketData/GetStaticThreshold/{ID}/{day}"
        while True:
            try:
                headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36'}
                response = requests.get(url, timeout=1, headers= headers)
                break
            except:
                pass
        try:
            data = json.loads(response.text)['staticThreshold'][-1] 
            return {'Min': data['psGelStaMin'], 'Max': data['psGelStaMax']}
        except:
            return None

    @staticmethod
    def get_daily_prices(ID, day: datetime.date):
        day = day.strftime("%Y%m%d")
        url = f"http://cdn.tsetmc.com/api/ClosingPrice/GetClosingPriceDaily/{ID}/{day}"
        while True:
            try:
                headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36'}
                response = requests.get(url, timeout=1, headers= headers)
                break
            except:
                pass
        try:
            data = json.loads(response.text)['closingPriceDaily']
            return {'YesterdayPrice': data['priceYesterday'], 'TodayPrice': data['pClosing']}
        except:
            return None

    @staticmethod
    def buy(trades: list[tradeInfo], ID, name, price, time, middlewareName, buyType):
        trade = tradeInfo()
        trade.ID = ID
        trade.name = name
        trade.buyPrice = price
        trade.buyTime = time
        trade.buyMiddleware = middlewareName
        trade.buyType = buyType
        trades.append(trade)
    
    @staticmethod
    def sell(lastTrade: tradeInfo, price, time, sellMiddlewares: list[middlewareOffline], middlewareName, sellType):
        lastTrade.sellPrice = price
        lastTrade.sellTime = time
        lastTrade.sellMiddleware = middlewareName
        lastTrade.sellType = sellType
        lastTrade.profit = round((lastTrade.sellPrice-lastTrade.buyPrice)/lastTrade.buyPrice*100-transactionFee, 2)
        for middleware in sellMiddlewares:
            middleware.history[lastTrade.ID] = {}

    @staticmethod
    def sort_trades_by_date(trades: list[tradeInfo]) -> list[tradeInfo]:
        
        sortedTrades: list[tradeInfo] = []
        for trade in trades:
            if len(sortedTrades) == 0:
                sortedTrades.append(trade)
            else:
                if trade.buyTime >= sortedTrades[-1].buyTime:
                    sortedTrades.append(trade)
                else:
                    for i in range(-1, -len(sortedTrades), -1):
                        if trade.buyTime >= sortedTrades[i-1].buyTime:
                            sortedTrades.insert(i, trade)
                            break
                    else:
                        sortedTrades.insert(0, trade)
        return sortedTrades  

    def create_real_trades(self, trades: list[tradeInfo], maxPortfolioTickerNumber: int) -> list[tradeInfo]:

        portfolio: list[tradeInfo] = []
        realTrades: list[tradeInfo] = []

        for trade in trades:
            # check sell
            tempPortfolio = portfolio
            for portfolioTrade in tempPortfolio:
                if portfolioTrade.sellTime <= trade.buyTime:
                    portfolio.remove(portfolioTrade)
            # check buy
            if len(portfolio) < maxPortfolioTickerNumber:
                realTrades.append(trade)
                portfolio.append(trade)

        return realTrades  

    def create_excel(self, trades: list[tradeInfo], tickerTradesDict: dict[list[tradeInfo]], excellName: str, maxPortfolioTickerNumber: int):

        # create totalTrades sheet
        totalProfit = 1
        totalTrades = []

        for trade in trades:

            totalProfit *= (1 + trade.profit/100/maxPortfolioTickerNumber)
            if trade.profit >= 0:
                isProfitable = 1
            else:
                isProfitable = 0

            tickerData: tickerOfflineData = self.tickersData[trade.ID]
            dayIndice = tickerData.dateTime.index(trade.buyTime.date())
            realPower = round(tickerData.clientData.realPower[dayIndice], 1)
            normalVolume = round(tickerData.volumeData.volume[dayIndice]/tickerData.volumeData.volumeAvg[dayIndice], 1)


            totalTrades.append([
                    trade.name, gregorian_to_jalali(trade.buyTime.strftime("%Y-%m-%d")), trade.buyTime.strftime("%H:%M:%S"),\
                        gregorian_to_jalali(trade.sellTime.strftime("%Y-%m-%d")), trade.sellTime.strftime("%H:%M:%S"),\
                            trade.buyPrice, trade.sellPrice,  
                            trade.profit, isProfitable, round((totalProfit-1)*100, 1), realPower, normalVolume, trade.buyMiddleware, trade.buyType, trade.sellMiddleware, trade.sellType
                ])
        totalTradesDataFrame = pd.DataFrame(data= totalTrades, columns=['Ticker', ' Buy Day ', ' Buy Time ', ' Sell Day ', ' Sell Time ', 'Buy Price', 'Sell Price', 'Profit', 'Is Profitable', 'Portfolio Profit', 'Real Power', 'Normal Volume', 'Buy Middleware', 'Buy Type', 'Sell Middleware', 'Sell Type'])

        # create tickerTrades sheet
        tickerTrades = []
        for ID in tickerTradesDict:
            totalProfit = 1
            tradeNumber = 0
            profitableTradesNumber = 0
            tradeList: list[tradeInfo] = tickerTradesDict[ID]
            for trade in tradeList:
                tradeNumber += 1
                if trade.profit >= 0:
                    profitableTradesNumber += 1
                totalProfit *= (1 + trade.profit/100)
            totalProfit = round((totalProfit-1)*100, 1)
            winRate = int(profitableTradesNumber/tradeNumber*100)
            if totalProfit >= 0:
                tradeProfitability = 1
            else:
                tradeProfitability = 0
            tickerData: tickerOfflineData = self.tickersData[ID]

            if self.timeFrame == '1D':
                priceChange = round((tickerData.priceData.closePrice[-1]-tickerData.priceData.closePrice[0])/tickerData.priceData.closePrice[0]*100-transactionFee, 1)
            else:
                priceChange = round((tickerData.onlineData.closePriceAdj[-1][-1]-tickerData.onlineData.closePriceAdj[0][0])/tickerData.onlineData.closePriceAdj[0][0]*100-transactionFee, 1)
            
            if totalProfit >= priceChange:
                holdCheck = 1
            else:
                holdCheck = 0
            tickerTrades.append([
                tradeList[0].name, totalProfit, tradeNumber, winRate, tradeProfitability, priceChange, holdCheck
            ])
        tickerTradesDataFrame = pd.DataFrame(data= tickerTrades, columns=['Ticker', 'TotalProfit', 'TradeNumber', 'WinRate', 'TradeProfitability', 'PriceChange', 'HoldCheck'])

        while True:
            try:
                writer = pd.ExcelWriter(excellName + '.xlsx')
                totalTradesDataFrame.to_excel(writer,'Total Trades')
                tickerTradesDataFrame.to_excel(writer,'Ticker Trades')
                writer.save()
                break
            except:
                input('Trades.xlsx is open!\nclose it and press Enter...')
                continue
    
    @staticmethod
    def create_ticker_trades_dict(trades: list[tradeInfo]) -> dict[list[tradeInfo]]:

        tickerTradesDict: dict = {}
        for trade in trades:
            if trade.ID not in tickerTradesDict:
                tickerTradesDict[trade.ID] = [trade]
            else:
                tickerTradesDict[trade.ID].append(trade)
        return tickerTradesDict

    @staticmethod
    def classify_web_data(data: dict) -> dict:
        
        data['t'] = [list(group) for k, group in itertools.groupby(data['t'],
                                                   key=datetime.datetime.toordinal)]

        sublistsLength = [len(sublist) for sublist in data['t']]
        data['c'] = [data['c'][sum(sublistsLength[:i+1])-sublistsLength[i]:sum(sublistsLength[:i+1])] for i in range(len(sublistsLength))]
        data['o'] = [data['o'][sum(sublistsLength[:i+1])-sublistsLength[i]:sum(sublistsLength[:i+1])] for i in range(len(sublistsLength))]
        data['h'] = [data['h'][sum(sublistsLength[:i+1])-sublistsLength[i]:sum(sublistsLength[:i+1])] for i in range(len(sublistsLength))]
        data['l'] = [data['l'][sum(sublistsLength[:i+1])-sublistsLength[i]:sum(sublistsLength[:i+1])] for i in range(len(sublistsLength))]
        data['v'] = [data['v'][sum(sublistsLength[:i+1])-sublistsLength[i]:sum(sublistsLength[:i+1])] for i in range(len(sublistsLength))]

    @staticmethod
    def apply_intersection(dbData, webPricesData):

        dbDays: list[datetime.date] = dbData['Time'] 
        webDays: list[datetime.date] = [item[0].date() for item in webPricesData['t']]
        commonDays: list[datetime.date] = [day for day in dbDays if day in webDays]
        
        # dbData revise
        dbDaysToRemove = []
        for day in dbData['Time']:
            if day not in commonDays:
                dbDaysToRemove.append(day)
        for day in dbDaysToRemove:
            index = dbData['Time'].index(day)
            for column in dbData:
                del dbData[column][index]

        # dbData revise
        webDaysToRemove = []
        for day in webDays:
            if day not in commonDays:
                webDaysToRemove.append(day)
        for day in webDaysToRemove:
            for i in range(len(webPricesData['t'])):
                if day == webPricesData['t'][i][0].date():
                    for column in webPricesData:
                        if column != 's':
                            del webPricesData[column][i]
                    break


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
    
    @staticmethod
    def adjust_Volume(volume, adjustedClosePrice, unAdjustedClosePrice):
        dif = (unAdjustedClosePrice-adjustedClosePrice)/adjustedClosePrice*100
        if abs(dif) < 1:
            return volume
        else:
            if type(volume) == list:
                tempVolume = volume.copy()
                return [int(thisVolume * unAdjustedClosePrice / adjustedClosePrice) for thisVolume in tempVolume]
            else:
                return int(volume * unAdjustedClosePrice / adjustedClosePrice)

    def plot_offline_data(self):
        
        ID = list(self.tickersData.keys())[0]
        tickerData: tickerOfflineData = self.tickersData[ID]
        time = tickerData.time
        realPower = tickerData.clientData.realPower
        realPower = [log10(item) for item in realPower]
        buyPerCapita = [int(tickerData.clientData.realBuyValue[i]/tickerData.clientData.realBuyNumber[i]/10**7)+1 if tickerData.clientData.realBuyNumber[i]!=0 else 1 for i in range(len(time))]
        sellPerCapita = [int(tickerData.clientData.realSellValue[i]/tickerData.clientData.realSellNumber[i]/10**7)+1 if tickerData.clientData.realSellNumber[i]!=0 else 1 for i in range(len(time))]
        realValueInput = tickerData.realValueInput

        buyPercapitaLog = [log10(item) for item in buyPerCapita]
        sellPercapitaLog = [log10(item) for item in sellPerCapita]
        
        buyPercapitaAvg = [10**(sum(buyPercapitaLog[max(0, i-30):i])/len((buyPercapitaLog[max(0, i-30):i]))) if i != 0 else buyPerCapita[i] for i in range(len(sellPerCapita))]
        sellPercapitaAvg = [10**(sum(sellPercapitaLog[max(0, i-30):i])/len((sellPercapitaLog[max(0, i-30):i]))) if i != 0 else sellPerCapita[i] for i in range(len(sellPerCapita))]

        buyPerCapitaRatio = [log10(buyPerCapita[i])-log10(buyPercapitaAvg[i]) for i in range(len(buyPerCapita))]
        sellPerCapitaRatio = [log10(sellPerCapita[i])-log10(sellPercapitaAvg[i]) for i in range(len(sellPerCapita))]

        normalVolume = [log10(tickerData.volumeData.realVolume[i]/tickerData.volumeData.realVolumeAvg[i-1]) if i!=0 else 0 for i in range(len(time))]

        corporateBuyNumber = tickerData.clientData.corporateBuyNumber
        corporateSellNumber = tickerData.clientData.corporateSellNumber

        rpvp = [normalVolume[i]+realPower[i] for i in range(len(time))]
        realMoneyInputSum = [sum(realValueInput[:i+1]) for i in range(len(realValueInput))]
        realMoneyInputSumMa = calculateSma(realMoneyInputSum)

        ap = advancedPlot(5, 2, ticker_repo().read_by_ID(ID)['FarsiTicker'])

        custom_rc = {'font.size': 8, 'figure.titlesize': 'x-large', 'figure.titleweight': 'normal'}
        s =mpf.make_mpf_style(base_mpf_style='charles', rc=custom_rc) #
        prices = {'Date': tickerData.dateTime, 'High': tickerData.priceData.highPrice, 'Low': tickerData.priceData.lowPrice, 'Open': tickerData.priceData.openPrice, 'Close': tickerData.priceData.closePrice}
        dataPd = pd.DataFrame(prices)
        dataPd.index = pd.DatetimeIndex(dataPd['Date'])
        mpf.plot(dataPd, ax= ap.ax[0][0], axisoff = True, type= 'candle', tight_layout= True, returnfig= False, style=s, ylabel= '')
        ap.ax[0][0].yaxis.tick_left()
        ap.ax[0][0].yaxis.set_label_position("left")
        ap.ax[0][0].set_yscale('log')

        clrs = ['red' if (x < 0) else 'green' for x in realPower]
        ap.ax[0][1].bar(time, realPower, color= clrs)
        ap.ax[0][1].plot(time, [0 for _ in range(len(time))], color= 'black', linewidth= 0.7, label= 'RealPower')
        ap.ax[0][1].plot(time, [log10(2) for _ in range(len(time))], color= 'blue', linewidth= 0.7)
        ap.ax[0][1].plot(time, [-log10(2) for _ in range(len(time))], color= 'blue', linewidth= 0.7)
        ap.ax[0][1].legend()

        ap.ax[1][0].plot(time, realMoneyInputSum, label= 'RealMoney')
        ap.ax[1][0].plot(time, realMoneyInputSumMa, color= 'black')
        ap.ax[1][0].legend()


        clrs = ['red' if (x < 0) else 'green' for x in normalVolume]
        ap.ax[1][1].bar(time, normalVolume, color= clrs)
        ap.ax[1][1].plot(time, [0 for _ in range(len(time))], color= 'black', linewidth= 0.7, label= 'Volume')
        ap.ax[1][1].legend()

        clrs = ['red' if (x < 0) else 'green' for x in realValueInput]
        ap.ax[2][0].bar(time, realValueInput, color= clrs)
        ap.ax[2][0].plot(time, [0 for _ in range(len(time))], color= 'black', linewidth= 0.7, label= 'RealMoney')
        ap.ax[2][0].legend()

        clrs = ['red' if (x < 0) else 'green' for x in rpvp]
        ap.ax[2][1].bar(time, rpvp, color= clrs)
        ap.ax[2][1].plot(time, [0 for _ in range(len(time))], color= 'black', linewidth= 0.7, label= 'RPVP')
        ap.ax[2][1].legend()

        ap.ax[3][0].plot(time, corporateBuyNumber, color= 'green', label= 'Corporate')
        ap.ax[3][0].plot(time, corporateSellNumber, color= 'red')
        ap.ax[3][0].legend()
        
        ap.ax[3][1].plot(time, buyPerCapita, color= 'green', label= 'percapita')
        ap.ax[3][1].plot(time, sellPerCapita, color= 'red')
        ap.ax[3][1].legend()

        ap.ax[4][1].plot(time, buyPerCapitaRatio, color= 'green')
        ap.ax[4][1].plot(time, sellPerCapitaRatio, color= 'red')
        ap.ax[4][1].plot(time, [log10(3) for _ in range(len(time))], color= 'blue', linewidth= 0.7)
        ap.ax[4][1].plot(time, [-log10(3) for _ in range(len(time))], color= 'blue', linewidth= 0.7)
        ap.ax[4][1].plot(time, [0 for _ in range(len(time))], color= 'black', linewidth= 0.7, label= 'Percapita Ratio')
        ap.ax[4][1].legend()

        ap.run()

    def plot_online_data(self):
        
        for ID in self.tickersData:
            tickerData: tickerOfflineData = self.tickersData[ID]
            # time = []
            price = []
            # volume = []
            # realPower = []
            for i in range(len(tickerData.priceData.highPrice)):
                # time = time + [gregorian_to_jalali(time.strftime("%Y-%m-%d"))+' '+time.strftime("%H:%M:%S") for time in tickerData.onlineData.time[i]]
                # price = price + [(tickerData.onlineData.highPrice[i][j] + tickerData.onlineData.lowPrice[i][j])/2 for j in range(len(tickerData.onlineData.highPrice[i]))]
                # price = price + tickerData.onlineData.closePrice[i]
                price  = price + self.adjust_price(tickerData.onlineData.closePrice[i], tickerData.priceData.closePrice[i], tickerData.onlineData.closePrice[i][-1])
                # volume = volume + tickerData.onlineData.volume[i]
                # realPower = realPower + [tickerData.clientData.realPower[i] for _ in range(len(dayLength))]
            # priceMa = calculateSma(price, 5, True)

            
            bb = calculateBB(price, 240, 2, True)
            bbl = bb[2]
            bbh = bb[1]

            bbPRC = [(price[k]-bbl[k])/(bbh[k]-bbl[k])*100 if bbh[k] != bbl[k] else 50 for k in range(len(price))]   
            # bbPRCMa = calculateSma(bbPRC, 10, True)
            break
            
        ap = advancedPlot(2, 1)

        ap.ax[0].plot(price)
        ap.ax[0].plot(bbl)
        ap.ax[0].plot(bbh)
        
        ap.ax[1].plot(bbPRC)
        # ap.ax[1].plot(bbPRCMa)
        ap.ax[1].plot([0 for _ in range(len(price))], color= 'red')
        ap.ax[1].plot([100 for _ in range(len(price))], color= 'red')
        ap.ax[1].plot([10 for _ in range(len(price))], color= 'red')

        ap.plot()

    def realPower_check(self):

        for ID in self.tickersData:
            tickerData: tickerOfflineData = self.tickersData[ID]
            realPower = tickerData.clientData.realPower
            realPower = [realPower[i] if realPower[i]>=1 else -1/realPower[i] for i in range(len(realPower))]
            closePrice = tickerData.priceData.closePrice

        realPowerGroups = [-5, -3, -2.8, -2.4, -2, -1.8, -1.6, -1.4, -1.2, 1, 1.2, 1.4, 1.6, 1.8, 2, 2.4, 2.8, 3, 5]
        data = {}
        for realPowerNumber in realPowerGroups:
            data[realPowerNumber] = {'OpenPrice': 0, 'ClosePrice': 0, 'HighPrice': 0, 'LowPrice': 0, 'Number': 0}
            
        for i in range(len(realPower)-1):
            for realPowerNumber in data:
                if realPower[i] < realPowerNumber:
                    data[realPowerNumber]['Number'] += 1
                    data[realPowerNumber]['OpenPrice'] += tickerData.priceData.openPricePRC[i+1]
                    data[realPowerNumber]['ClosePrice'] += tickerData.priceData.closePricePRC[i+1]
                    data[realPowerNumber]['HighPrice'] += tickerData.priceData.highPricePRC[i+1]
                    data[realPowerNumber]['LowPrice'] += tickerData.priceData.lowPricePRC[i+1]
                    break

        for realPowerNumber in data:
            if data[realPowerNumber]['Number'] != 0:
                data[realPowerNumber]['OpenPrice'] /= data[realPowerNumber]['Number']
                data[realPowerNumber]['ClosePrice'] /= data[realPowerNumber]['Number']
                data[realPowerNumber]['HighPrice'] /= data[realPowerNumber]['Number']
                data[realPowerNumber]['LowPrice'] /= data[realPowerNumber]['Number']

        realPowerGroups = [str(realPowerNumber) for realPowerNumber in data]
        numbers = [data[realPowerNumber]['Number'] for realPowerNumber in data]
        highPrices = [data[realPowerNumber]['HighPrice'] for realPowerNumber in data]

        ap = advancedPlot(2, 1)

        ap.ax[0].bar(realPowerGroups, numbers)
        ap.ax[1].bar(realPowerGroups, highPrices)

        ap.run()

    def plot_chart(self, decNum, plothlines= True, plotvlines= True):

        if len(self.tickersData.keys()) != 1:
            return
            
        ID = list(self.tickersData.keys())[0]
        tickerData: tickerOfflineData = self.tickersData[ID]
        timeVec = []
        highPriceVec = []
        lowPriceVec = []
        openPriceVec = []
        closePriceVec = []
        volumeVec = []

        def set_vecs(start, end):
            timeVec.append(tickerData.onlineData.time[i][end-1])
            highPriceVec.append(self.adjust_price(max(tickerData.onlineData.highPrice[i][start:end]), tickerData.priceData.closePrice[i], tickerData.onlineData.closePrice[i][-1]))
            lowPriceVec.append(self.adjust_price(min(tickerData.onlineData.lowPrice[i][start:end]), tickerData.priceData.closePrice[i], tickerData.onlineData.closePrice[i][-1]))
            openPriceVec.append(self.adjust_price(tickerData.onlineData.openPrice[i][start], tickerData.priceData.closePrice[i], tickerData.onlineData.closePrice[i][-1]))
            closePriceVec.append(self.adjust_price(tickerData.onlineData.closePrice[i][end-1], tickerData.priceData.closePrice[i], tickerData.onlineData.closePrice[i][-1]))
            volumeVec.append(sum(tickerData.onlineData.volume[i][start:end]))
        
        vlines = []
        for i in range(len(tickerData.onlineData.time)):
            for j in range(decNum, len(tickerData.onlineData.time[i]), decNum):
                set_vecs(j-decNum, j)
            if decNum < len(tickerData.onlineData.time[i]):
                if tickerData.onlineData.time[i][-1]-timeVec[-1] > datetime.timedelta(minutes= 0.5*int(self.timeFrame)*decNum):
                    set_vecs(j, len(tickerData.onlineData.time[i]))
            else:
                set_vecs(0, len(tickerData.onlineData.time[i]))
            if plotvlines:
                vlines.append(timeVec[-1] + datetime.timedelta(hours= 0.5))  

        prices = {'Date': timeVec, 'High': highPriceVec, 'Low': lowPriceVec, 'Open': openPriceVec, 'Close': closePriceVec, 'Volume': volumeVec}
        dataPd = pd.DataFrame(prices) 
        dataPd.index = pd.DatetimeIndex(dataPd['Date'])
        
        minTimeVec = min(timeVec)
        maxTimeVec = max(timeVec)

        for i in range(len(vlines)):
            vlines[i] = max(min(vlines[i], maxTimeVec), minTimeVec)

        tradeLines = []
        for trade in self.trades:
            buyTime = max(min(trade.buyTime, maxTimeVec), minTimeVec)
            sellTime = max(min(trade.sellTime, maxTimeVec), minTimeVec)
            tradeLines.append([(buyTime, trade.buyPrice), (sellTime, trade.sellPrice)])

        if plothlines:
            # calc res sup 
            hlines = calc_resistance_support(tickerData.priceData.highPrice,tickerData.priceData.lowPrice)
        else:
            hlines = []

        # plot
        custom_rc = {'font.size': 8, 'figure.titlesize': 'x-large', 'figure.titleweight': 'normal'}
        s =mpf.make_mpf_style(base_mpf_style='charles', rc=custom_rc) #
         
        fig, axlist = mpf.plot(dataPd, axisoff = True, type='candle', volume= True, tight_layout= True, returnfig=True, style=s,
            alines=dict(alines=tradeLines, colors= ['blue' for i in range(len(tradeLines))], linewidths= [1.3 for i in range(len(tradeLines))]),
            hlines= dict(hlines=hlines, colors= ['0.8' for i in range(len(hlines))], linewidths= [0.4 for i in range(len(hlines))]), 
            vlines= dict(vlines=vlines, colors= ['0.8' for i in range(len(vlines))], linewidths= [0.4 for i in range(len(vlines))])) # , mav= (30)

        # ich = calculateIchimoko(highPriceVec, lowPriceVec, 9, 36, 52, True, False)

        # axlist[0].plot(ich[0])
        # axlist[0].plot(ich[1])

        # fig = mpf.figure(style='yahoo',figsize=(7,8))
        # ax1 = fig.add_subplot(4,1,1)
        # ax2 = fig.add_subplot(4,1,2, sharex=ax1)
        # ax3 = fig.add_subplot(4,1,3, sharex=ax1)
        # ax4 = fig.add_subplot(4,1,4, sharex=ax1)
        # mpf.plot(dataPd, ax= ax1, axisoff = True, type='candle', volume= ax2, tight_layout= True, returnfig=True, style=s,
        #     alines=dict(alines=tradeLines, colors= ['blue' for i in range(len(tradeLines))], linewidths= [1.3 for i in range(len(tradeLines))]),
        #     hlines= dict(hlines=hlines, colors= ['0.8' for i in range(len(hlines))], linewidths= [0.4 for i in range(len(hlines))]), 
        #     vlines= dict(vlines=vlines, colors= ['0.8' for i in range(len(vlines))], linewidths= [0.4 for i in range(len(vlines))]))

        # demandVolume = []
        # demandPercapita = []
        # for i in range(len(tickerData.onlineData.time)):
        #     todayDemandVolume = self.adjust_Volume(tickerData.onlineData.ordersBoard.row1.demandVolume[i], tickerData.priceData.closePrice[i], tickerData.onlineData.closePrice[i][-1])
        #     demandVolume = demandVolume + [todayDemandVolume[j]/tickerData.volumeData.volumeAvg[i] if tickerData.onlineData.closePrice[i][j] == tickerData.priceData.maxAllowedPrice[i] else 0 for j in range(len(todayDemandVolume))]
        #     demandPercapita = demandPercapita + [int(tickerData.onlineData.ordersBoard.row1.demandVolume[i][j]/tickerData.onlineData.ordersBoard.row1.demandNumber[i][j]*tickerData.onlineData.closePrice[i][j]/10**7) if tickerData.onlineData.ordersBoard.row1.demandNumber[i][j] != 0 and tickerData.onlineData.closePrice[i][j] == tickerData.priceData.maxAllowedPrice[i] else 0 for j in range(len(tickerData.onlineData.ordersBoard.row1.demandNumber[i]))]
        
        # ax3.plot(demandVolume)
        # ax4.plot(demandPercapita)

        # # trend line
        # price = [(highPriceVec[i]+lowPriceVec[i])/2 for i in range(len(timeVec))]
        # priceMa = calculateSma(price, 34, True)
        # priceMaSlope = [priceMa[i]-priceMa[i-10] if i >= 10 else 0 for i in range(len(priceMa))]
        # m = 0.02
        # priceMa = [float(int(priceMa[i]*(1-m))) if priceMaSlope[i] >= 0 else float(int(priceMa[i]*(1+m))) for i in range(len(priceMa))]
        # axlist[0].plot(priceMa)

        x = 1


        def on_click(event):
            if event.inaxes:
                indice = int(min(max(0, event.xdata), len(timeVec)-1))
                date = timeVec[indice].date()
                indice = tickerData.dateTime.index(date)
                normalVolume = str(round(tickerData.volumeData.volume[indice]/tickerData.volumeData.volumeAvg[indice], 1))
                realPower = str(round(tickerData.clientData.realPower[indice], 2))
                realPerCaptitaBuy = str(tickerData.clientData.realPercapitaBuy[indice])
                realPerCaptitaSell = str(tickerData.clientData.realPercapitaSell[indice])
                realBuyPrc = str(100-tickerData.clientData.realBuyPrc[indice])
                realSellPrc = str(100-tickerData.clientData.realSellPrc[indice])

                text = 'RP: '+ realPower + '  NV: '+ normalVolume\
                            + '     PCB: '+ realPerCaptitaBuy + '  PCS: '+ realPerCaptitaSell+ '\n\n'\
                            + 'CB: '+ realBuyPrc + '  CS: '+ realSellPrc+ '\n\n'
                fig.suptitle(text, x= 0.5, y= 0.1)
                fig.canvas.draw()
                fig.canvas.flush_events()

        fig.canvas.mpl_connect('button_press_event', on_click)
        axlist[0].set_yscale('log')
        # ax1.set_yscale('log')
        # fig.tight_layout()
        mng = plt.get_current_fig_manager()
        mng.window.state('zoomed')
        plt.show()

    def print_smart_money_data(self):

        ID = list(self.tickersData.keys())[0]
        tickerData: tickerOfflineData = self.tickersData[ID]

        normalVolume = [round(tickerData.volumeData.volume[i]/tickerData.volumeData.volumeAvg[i-1], 2) if i!=0 else 1 for i in range(len(tickerData.time))]
        realPower = tickerData.clientData.realPower

        lenght = len(tickerData.priceData.todayPrice)-1
        for i in range(len(tickerData.time)):
            beforePriceChange = round((tickerData.priceData.todayPrice[i]-tickerData.priceData.todayPrice[max(0, i-5)])/tickerData.priceData.todayPrice[max(0, i-5)]*100, 2)
            afterPriceChange = round((tickerData.priceData.todayPrice[min(lenght, i+3)]-tickerData.priceData.todayPrice[i])/tickerData.priceData.todayPrice[i]*100, 2)
            if normalVolume[i] > 1.5 and realPower[i] > 1.5:
                print('In:', tickerData.time[i], 'NormalVolume:', normalVolume[i], 'RealPower:', round(realPower[i], 2), 'before:', beforePriceChange, 'after:', afterPriceChange)
            # if normalVolume[i] > 1.5 and realPower[i] < 0.66:
            #     print('Out:', tickerData.time[i], 'NormalVolume:', normalVolume[i], 'RealPower', round(realPower[i], 2), 'priceGrow:', priceGrow)
    
    def print_ichimoko_data(self):

        ID = list(self.tickersData.keys())[0]
        tickerData: tickerOfflineData = self.tickersData[ID]
        
        normalVolume = [round(tickerData.volumeData.volume[i]/tickerData.volumeData.volumeAvg[i-1], 2) if i!=0 else 1 for i in range(len(tickerData.time))]
        realPower = tickerData.clientData.realPower

        ich = calculateIchimoko(tickerData.priceData.highPrice, tickerData.priceData.lowPrice, 9, 26, 52, True, False)

        tenkansen = ich[0]
        kijunsen = ich[1]
        spanA = ich[2]
        spanB = ich[3]

        for i in range(1, len(tickerData.time)):
            
            # if tickerData.priceData.closePrice[i] > tenkansen[i] and tickerData.priceData.closePrice[i-1] < tenkansen[i]:
            # if tickerData.priceData.closePrice[i] > kijunsen[i] and tickerData.priceData.closePrice[i-1] < kijunsen[i]:
            # if tickerData.priceData.closePrice[i] > tenkansen[i] and tickerData.priceData.closePrice[i-1] < tenkansen[i] and tickerData.priceData.closePrice[i] > kijunsen[i] and tickerData.priceData.closePrice[i-1] < kijunsen[i]:
            # if spanA[i] < spanB[i] and tickerData.priceData.closePrice[i] > spanA[i] and tickerData.priceData.closePrice[i-1] < spanA[i-1]:
            if spanA[i] > spanB[i] and tickerData.priceData.closePrice[i] > spanA[i] and tickerData.priceData.closePrice[i-1] < spanA[i-1] or \
                spanB[i] > spanA[i] and tickerData.priceData.closePrice[i] > spanB[i] and tickerData.priceData.closePrice[i-1] < spanA[i-1]:
                print(tickerData.time[i], 'NormalVolume:', normalVolume[i], 'RealPower:', round(realPower[i], 2))
