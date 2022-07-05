from math import log10
from Application.Utility.DateConverter import *
from Application.Utility.Indicators.IndicatorService import calculateSma
from Domain.Enums.TableType import tableType
from Domain.Enums.MiddlewareOrder import middlewareOrder
from Domain.Models.MiddlewareOffline import middlewareOffline
from Domain.Models.TickerOfflineData import tickerOfflineData
from Domain.Models.TradeInfo import tradeInfo
from Infrastructure.Repository.OfflineDataRepository import offlineData_repo
from Infrastructure.Repository.TickerRepository import ticker_repo
import pandas as pd
import matplotlib.pyplot as plt
import mplfinance as mpf
import datetime
from ta.momentum import *
from ta.volatility import *


class offlineStrategy:

    def __init__(self) -> None:
        pass
    
    def set_IDs(self, IDs):
        self.IDs = IDs
    
    def set_buy_middleweres(self, buyMiddleweres):
        self.buyMiddleweres: list[middlewareOffline] = []
        self.buyWeights: list = []
        for thisTuple in buyMiddleweres:
            self.buyMiddleweres.append(thisTuple[0])
            self.buyWeights.append(thisTuple[1])

    def set_sell_middleweres(self, sellMiddleweres):
        self.sellMiddleweres: list[middlewareOffline] = []
        self.sellWeights: list = []
        for thisTuple in sellMiddleweres:
            self.sellMiddleweres.append(thisTuple[0])
            self.sellWeights.append(thisTuple[1])

    def set_min_buy_score(self, minBuyScore):
        self.minBuyScore = minBuyScore
        if minBuyScore < 1 or minBuyScore > 100:
            raise Exception

    def set_min_sell_score(self, minSellScore):
        self.minSellScore = minSellScore
        if minSellScore < 1 or minSellScore > 100:
            raise Exception

    def set_stop_loss(self, stopLoss):
        self.stopLoss = stopLoss
    
    
    def read_data(self, fromDate, toDate):

        print('Reading from database...')
        dataRepo = offlineData_repo().read_OfflineData_in_time_range(\
        'all', table= tableType.OfflineData.value, IDList= self.IDs,\
            fromDate= jalali_to_gregorian(fromDate), toDate= jalali_to_gregorian(toDate))

        print('Creating data...')
        self.tickersData: dict[tickerOfflineData] = {}

        for ID in dataRepo:
            tickerName = ticker_repo().read_by_ID(ID)['FarsiTicker']
            self.tickersData[tickerName] = tickerOfflineData(dataRepo[ID])
        
    def buy(self, trades: list[tradeInfo], tickerName, price, time):
        newTrade = tradeInfo()
        newTrade.name = tickerName
        newTrade.buyPrice = price
        newTrade.buyTime = time
        trades.append(newTrade)

    def sell(self, trades: list[tradeInfo], price, time):
        trades[-1].sellPrice = price
        trades[-1].sellTime = time
        trades[-1].profit = round((trades[-1].sellPrice-trades[-1].buyPrice)/trades[-1].buyPrice*100-1.25, 2)

    def check_stop_loss(self, lastTrade: tradeInfo, nowPrice) -> bool:
        distance = (nowPrice-lastTrade.buyPrice)/lastTrade.buyPrice*100
        if distance < -self.stopLoss:
            return True
        else: 
            return False

    def run(self):

        trades: list[tradeInfo] = []
        for tickerName in self.tickersData:
            tickerData: tickerOfflineData = self.tickersData[tickerName]
            for i in range(len(tickerData.dateTime)):
                decision = middlewareOrder.Continue
                ############################ buy middlewares run ############################
                if (len(trades) == 0 or trades[-1].sellTime != None) and i != len(tickerData.dateTime)-1:
                    scores = []
                    for middleware in self.buyMiddleweres:
                        (decision, score, price) = middleware.process(tickerData, i)
                        if decision == middlewareOrder.Delete:
                            break
                        elif decision == middlewareOrder.Buy:
                            self.buy(trades, tickerName, price, tickerData.dateTime[i])
                            break
                        elif decision == middlewareOrder.Continue:
                            scores.append(score)
                        else:
                            raise Exception('middleware Order can not be Sell')
                    else:
                        if len(scores) != len(self.buyMiddleweres):
                            raise Exception
                        scoresSOP = [scores[i]*self.buyWeights[i] for i in range(len(self.buyWeights))]
                        finalScore = sum(scoresSOP)/sum(self.buyWeights)
                        if finalScore >= self.minBuyScore:
                            self.buy(trades, tickerName, price, tickerData.dateTime[i])
                            continue
                ############################ sell middlewares run ############################
                if decision != middlewareOrder.Buy and len(trades) != 0 and trades[-1].sellTime == None:
                    scores = []
                    for middleware in self.sellMiddleweres:
                        (decision, score, price) = middleware.process(tickerData, i)
                        if decision == middlewareOrder.Delete:
                            break
                        elif decision == middlewareOrder.Sell:
                            self.sell(trades, price, tickerData.dateTime[i])
                            break
                        elif decision == middlewareOrder.Continue:
                            scores.append(score)
                        else:
                            raise Exception('middleware Order can not be Buy')
                    else:
                        if len(scores) != len(self.sellMiddleweres):
                            raise Exception
                        scoresSOP = [scores[i]*self.sellWeights[i] for i in range(len(self.sellWeights))]
                        finalScore = sum(scoresSOP)/sum(self.sellWeights)
                        if finalScore >= self.minSellScore:
                            self.sell(trades, price, tickerData.dateTime[i])
                    # check stop loss
                    if self.check_stop_loss(trades[-1], tickerData.closePrice[i]):
                        self.sell(trades, price, tickerData.dateTime[i])
            if trades != []:
                if trades[-1].sellTime == None:
                    self.sell(trades, price, tickerData.dateTime[i])   
        sortedTrades = self.sort_trades_by_date(trades)
        return sortedTrades     

    def create_excel(self, trades: list[tradeInfo], tickerTradesDict: dict[list[tradeInfo]], name: str, maxPortfolioTickerNumber: int):

        # create totalTrades sheet
        totalProfit = 1
        totalTrades = []
        for trade in trades:
            totalProfit *= (1 + trade.profit/100/maxPortfolioTickerNumber)
            if trade.profit >= 0:
                isProfitable = 1
            else:
                isProfitable = 0
            totalTrades.append([
                    trade.name, gregorian_to_jalali(trade.buyTime.strftime("%Y-%m-%d")), gregorian_to_jalali(trade.sellTime.strftime("%Y-%m-%d")), trade.profit, isProfitable, round((totalProfit-1)*100, 1)
                ])
        totalTradesDataFrame = pd.DataFrame(data= totalTrades, columns=['Ticker', 'BuyTime', 'SellTime', 'Profit', 'IsProfitable', 'PortfolioProfit'])

        # create tickerTrades sheet
        tickerTrades = []
        for tickerName in tickerTradesDict:
            totalProfit = 1
            tradeNumber = 0
            tradeList: list[tradeInfo] = tickerTradesDict[tickerName]
            for trade in tradeList:
                tradeNumber += 1
                totalProfit *= (1 + trade.profit/100)
            totalProfit = round((totalProfit-1)*100, 1)
            if totalProfit >= 0:
                tradeProfitability  = 1
            else:
                tradeProfitability = 0
            priceChange = round((self.tickersData[tickerName].todayPrice[-1]-self.tickersData[tickerName].todayPrice[0])/self.tickersData[tickerName].todayPrice[0]*100, 1)
            if totalProfit >= priceChange:
                holdCheck = 1
            else:
                holdCheck = 0
            tickerTrades.append([
                tickerName, totalProfit, tradeNumber, tradeProfitability, priceChange, holdCheck
            ])
        tickerTradesDataFrame = pd.DataFrame(data= tickerTrades, columns=['Ticker', 'TotalProfit', 'TradeNumber', 'TradeProfitability', 'PriceChange', 'HoldCheck'])

        while True:
            try:
                writer = pd.ExcelWriter(name + '.xlsx')
                totalTradesDataFrame.to_excel(writer,'Total Trades')
                tickerTradesDataFrame.to_excel(writer,'Ticker Trades')
                writer.save()
                break
            except:
                input('Trades.xlsx is open!\nclose it and press Enter...')
                continue

    def create_ticker_trades_dict(self, trades: list[tradeInfo]) -> dict[list[tradeInfo]]:

        tickerTradesDict: dict = {}
        for trade in trades:
            if trade.name not in tickerTradesDict:
                tickerTradesDict[trade.name] = [trade]
            else:
                tickerTradesDict[trade.name].append(trade)
        return tickerTradesDict

    def sort_trades_by_date(self, trades: list[tradeInfo]) -> list[tradeInfo]:
        
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

    def backTest_run(self, maxPortfolioTickerNumber):
        
        print('Running backTest...')
        trades = self.run()
        self.tickerTradesDict = self.create_ticker_trades_dict(trades)
        realTrades = self.create_real_trades(trades, maxPortfolioTickerNumber)
        self.tickerRealTradesDict = self.create_ticker_trades_dict(realTrades)

        print('Creating excel...')
        self.create_excel(trades, self.tickerTradesDict, 'Trades', maxPortfolioTickerNumber)
        self.create_excel(realTrades, self.tickerRealTradesDict, 'RealTrades', maxPortfolioTickerNumber)



    # plot lab
    def plot_ticker_trades(self, name):
        trades: list[tradeInfo] =  self.tickerTradesDict[name]
        tickerData: tickerOfflineData = self.tickersData[name]
        prices = {'Date': tickerData.dateTime, 'High': tickerData.highPrice, 'Low': tickerData.lowPrice, 'Open': tickerData.openPrice, 'Close': tickerData.closePrice, 'Volume': tickerData.volume}
        dataPd = pd.DataFrame(prices) 
        dataPd.index = pd.DatetimeIndex(dataPd['Date'])
        
        lines = []
        for trade in trades:
            lines.append([(trade.buyTime, trade.buyPrice), (trade.sellTime, trade.sellPrice)])
        
        # plot
        custom_rc = {'font.size': 10, 'lines.linewidth': 2}
        s =mpf.make_mpf_style(base_mpf_style='charles', rc=custom_rc)
        fig, axlist = mpf.plot(dataPd, type='candle', volume=True, tight_layout= True, style=s, returnfig=True, \
            alines=dict(alines=lines, colors= ['blue' for i in range(len(lines))]), mav= (10)) 
        axlist[0].set_yscale('log')
        plt.show()

    def plot_ticker_realPower(self, name):
        tickerData: tickerOfflineData = self.tickersData[name]
        realPowerLog = list(range(len(tickerData.realPower)))
        for i in range(len(tickerData.realPower)):
            if tickerData.realPower[i] > 3:
                realPowerLog[i] = log10(3)
            elif tickerData.realPower[i] < 1/3:
                realPowerLog[i] = log10(1/3)
            else:
                realPowerLog[i] = log10(tickerData.realPower[i])
        # finalRealPower = [100/(max(realPowerLog)-min(realPowerLog))*(realPower-min(realPowerLog)) for realPower in realPowerLog]
        plt.figure()
        ax = plt.gca()
        # ax.scatter(tickerData.time, tickerData.closePrice, c= realPowerLog, s= 10)
        ax.bar(tickerData.time, tickerData.realPower)
        const1 = [1 for i in range(len(tickerData.realPower))]
        ax.plot(tickerData.time, const1, color='red')

        ax.set_yscale('log')
        plt.show()

    def plot_bb(self, name):
        tickerData: tickerOfflineData = self.tickersData[name]
        time = tickerData.dateTime
        price = tickerData.closePrice

        # constants
        const0 = [0 for i in range(len(price))]
        const1 = [1 for i in range(len(price))]
        const4 = [4 for i in range(len(price))]
        const15 = [15 for i in range(len(price))]
        const20 = [20 for i in range(len(price))]
        const80 = [80 for i in range(len(price))]
        const100 = [100 for i in range(len(price))]
        constLog2 = [log10(2) for i in range(len(price))]
        constLog2M = [-log10(2) for i in range(len(price))]
        
        # plot
        rowNum = 4
        colNum = 2
        barWidth = 0.00015
        fig, ax = plt.subplots(rowNum, colNum, sharex= True, figsize=(20,20))

        ax[0][0].plot(time, price, color= 'black')
        ax[0][0].plot(time, tickerData.bbl, color= 'blue')
        ax[0][0].plot(time, tickerData.bbh, color= 'blue')
        ax[0][0].plot(time, tickerData.bbm, color= 'red')

        ax[0][1].plot(time, tickerData.pbbl, label= 'pbbl')
        ax[0][1].plot(time, tickerData.pbblma)
        ax[0][1].plot(time, const0)
        ax[0][1].plot(time, const4)
        ax[0][1].legend()

        ax[1][0].bar(time, tickerData.rpvp, label= 'rpvp')
        ax[1][0].plot(time, const0, color= 'red')
        ax[1][0].legend()

        ax[1][1].plot(time, tickerData.pbbh, label= 'pbbh')
        ax[1][1].plot(time, tickerData.pbbhma)
        ax[1][1].plot(time, const0)
        ax[1][1].plot(time, const4)
        ax[1][1].legend()

        ax[2][0].plot(time, tickerData.realPowerLog, label= 'RealPower')
        ax[2][0].plot(time, const0)
        ax[2][0].plot(time, constLog2)
        ax[2][0].plot(time, constLog2M)
        ax[2][0].legend()

        ax[2][1].plot(time, tickerData.cw, label= 'cw')
        ax[2][1].plot(time, const15)
        ax[2][1].legend()

        ax[3][1].plot(time, tickerData.pbbd, label= 'pbbd')
        ax[3][1].plot(time, const0)
        ax[3][1].plot(time, const20)
        ax[3][1].plot(time, const80)
        ax[3][1].plot(time, const100)
        ax[3][1].legend()

        
        fig.tight_layout()
        mng = plt.get_current_fig_manager()
        mng.window.state('zoomed')
        xline = [[0 for j in range(colNum)] for i in range(rowNum)]
        for i in range(rowNum):
            for j in range(colNum):
                    yMin, yMax = ax[i][j].get_ylim()
                    xline[i][j], = ax[i][j].plot([min(time), min(time)],[yMin,yMax])
        def on_click(event):
            if event.inaxes:
                for i in range(rowNum):
                    for j in range(colNum):
                        xline[i][j].set_xdata(event.xdata)
                fig.canvas.draw()
                fig.canvas.flush_events()
        fig.canvas.mpl_connect('button_press_event', on_click)
        plt.show()

    def plot(self, name):
        tickerData: tickerOfflineData = self.tickersData[name]
        price = tickerData.closePrice
        priceMa = tickerData.closePriceMa

        # plot
        rowNum = 2
        colNum = 1
        fig, ax = plt.subplots(rowNum, colNum, sharex= True, figsize=(20,20))

        ax[0].plot(tickerData.time, price, color= 'black')
        ax[0].plot(tickerData.time, priceMa, color= 'red')

        fig.tight_layout()
        mng = plt.get_current_fig_manager()
        mng.window.state('zoomed')
        xline = [0 for i in range(rowNum)]
        for i in range(rowNum):
            yMin, yMax = ax[i].get_ylim()
            xline[i], = ax[i].plot([min(tickerData.time), min(tickerData.time)],[yMin,yMax])
        def on_click(event):
            if event.inaxes:
                for i in range(rowNum):
                    xline[i].set_xdata(event.xdata)
                fig.canvas.draw()
                fig.canvas.flush_events()
        fig.canvas.mpl_connect('button_press_event', on_click)
        plt.show()

    def plot_client_index(self, name):
        tickerData: tickerOfflineData = self.tickersData[name]
        price = tickerData.closePrice


        for i in range(len(price)):
            realBuyVolume = tickerData.realBuyValue[i]/tickerData.todayPrice[i]
            realSellVolume = tickerData.realSellValue[i]/tickerData.todayPrice[i]
            if i == 0:
                realMoneyInput = [realBuyVolume-realSellVolume]
            else:
                realMoneyInput.append(realBuyVolume-realSellVolume+realMoneyInput[-1])

        # plot
        rowNum = 2
        colNum = 1
        fig, ax = plt.subplots(rowNum, colNum, sharex= True, figsize=(20,20))

        ax[0].semilogy(tickerData.time, price)
        ax[1].plot(tickerData.time, realMoneyInput, color= 'black')

        fig.tight_layout()
        mng = plt.get_current_fig_manager()
        mng.window.state('zoomed')
        xline = [0 for i in range(rowNum)]
        for i in range(rowNum):
            yMin, yMax = ax[i].get_ylim()
            xline[i], = ax[i].plot([min(tickerData.time), min(tickerData.time)],[yMin,yMax])
        def on_click(event):
            if event.inaxes:
                for i in range(rowNum):
                    xline[i].set_xdata(event.xdata)
                fig.canvas.draw()
                fig.canvas.flush_events()
        fig.canvas.mpl_connect('button_press_event', on_click)
        plt.show()

    def plot_shareHolder_composition(self, name):
        tickerData: tickerOfflineData = self.tickersData[name]
        price = tickerData.closePrice


        for i in range(len(price)):
            realBuyVolume = tickerData.realBuyValue[i]/tickerData.todayPrice[i]
            realSellVolume = tickerData.realSellValue[i]/tickerData.todayPrice[i]
            if i == 0:
                realMoneyInput = [realBuyVolume-realSellVolume]
            else:
                realMoneyInput.append(realBuyVolume-realSellVolume+realMoneyInput[-1])

        # plot
        rowNum = 2
        colNum = 1
        fig, ax = plt.subplots(rowNum, colNum, sharex= True, figsize=(20,20))

        ax[0].semilogy(tickerData.time, price)
        ax[1].plot(tickerData.time, realMoneyInput, color= 'black')

        fig.tight_layout()
        mng = plt.get_current_fig_manager()
        mng.window.state('zoomed')
        xline = [0 for i in range(rowNum)]
        for i in range(rowNum):
            yMin, yMax = ax[i].get_ylim()
            xline[i], = ax[i].plot([min(tickerData.time), min(tickerData.time)],[yMin,yMax])
        def on_click(event):
            if event.inaxes:
                for i in range(rowNum):
                    xline[i].set_xdata(event.xdata)
                fig.canvas.draw()
                fig.canvas.flush_events()
        fig.canvas.mpl_connect('button_press_event', on_click)
        plt.show()

    
