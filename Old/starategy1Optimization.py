from math import log10

from numpy.core.function_base import linspace
from Classes import Ticker, getTickers
from SqlServerDataBaseLib import DatabaseConnection
import matplotlib.pyplot as plt
import numpy as np

Name = 'شپنا'
TickerNames = [Name]
Tickers = getTickers(TickerNames, '1399-01-22', '1400-12-04')

# RealPower
RealPower = [10*log10(Tickers[Name].RealPower[i]) for i in range(len(Tickers[Name].RealPower))]
OpenPricePRC = [(Tickers[Name].OpenPrice[i] - Tickers[Name].YesterdayPrice[i])/Tickers[Name].YesterdayPrice[i]*100 for i in range(len(Tickers[Name].OpenPrice))]

TotalProfit = []

for PRC in np.linspace(0, 5, num=11):
    C = [0 for i in range(len(Tickers[Name].RealPower))]
    for i in range(len(Tickers[Name].RealPower)):
        if Tickers[Name].RealPower[i] > 1.2 and Tickers[Name].TodayPricePRC[i] < PRC:
            C[i] = 'lime'
        elif Tickers[Name].RealPower[i] > 1.3 and Tickers[Name].TodayPricePRC[i] >= -1*PRC:
            C[i] = 'green'
        elif i != 0 and Tickers[Name].RealPower[i]> 1.2 and Tickers[Name].RealPower[i-1] > 0:
            C[i] = 'green'
        # elif Tickers[Name].RealPower[i] < 0.5:
        #     C[i] = 'firebrick'
        elif Tickers[Name].RealPower[i] < 0.85 and Tickers[Name].TodayPricePRC[i] >= -1*PRC:
            C[i] = 'red'
        elif Tickers[Name].RealPower[i] < 0.85 and Tickers[Name].TodayPricePRC[i] < -1*PRC:
            C[i] = 'firebrick'
        else:
            C[i] = 'orange'

    status = 'OUT'
    Trades = {}
    Profit = 0
    BuyPrice = 0
    SellPrice = 0
    Danger = 0
    DangerDay = 0
    BuyDate = ''
    SellDate = ''

    for i in range(len(Tickers[Name].Date)):
        if status == 'OUT':

            if C[i] == 'lime' or C[i] == 'green':
                status = 'IN'
                BuyPrice = Tickers[Name].HighPrice[i]
                BuyDate = Tickers[Name].Date[i]

        if status == 'IN':

            if C[i] == 'firebrick':
                SellPrice = Tickers[Name].LowPrice[i]
                SellDate = Tickers[Name].Date[i]
                status = 'OUT'
                Trades[BuyDate + '\t' + SellDate] = (0.988*(SellPrice-BuyPrice)/BuyPrice*100)

            if C[i] == 'red' and Danger == 0:
                Danger = 1
                DangerDay = i

            if C[i] == 'red' and Danger == 1 and i == DangerDay + 1:
                Danger = 2

            if C[i] == 'red' and Danger == 2 and i == DangerDay + 2:
                SellPrice = Tickers[Name].LowPrice[i]
                SellDate = Tickers[Name].Date[i]
                status = 'OUT'
                Trades[BuyDate + '-' + SellDate] = (0.988*(SellPrice-BuyPrice)/BuyPrice*100)

            if C[i] != 'red' and Danger != 0:
                Danger = 0
    profit = 1
    for Date in Trades:
        profit *= (1 + Trades[Date]/100)
    TotalProfit.append((profit-1)*100)

for i in range(len(TotalProfit)):
    print(np.linspace(0, 5, num=11)[i], '\t', TotalProfit[i])

plt.plot(np.linspace(0, 5, num=11), TotalProfit)
plt.show()

        



        


        
        

    

