from math import log10
from Classes import Ticker, getTickers
import matplotlib.pyplot as plt

Name = 'شپنا'
TickerNames = [Name]
Tickers = getTickers(TickerNames, '1399-05-21', '1400-12-04')

# RealPower
RealPower = [10*log10(Tickers[Name].RealPower[i]) for i in range(len(Tickers[Name].RealPower))]
OpenPricePRC = [(Tickers[Name].OpenPrice[i] - Tickers[Name].YesterdayPrice[i])/Tickers[Name].YesterdayPrice[i]*100 for i in range(len(Tickers[Name].OpenPrice))]

C = [0 for i in range(len(Tickers[Name].RealPower))]
PRC = 1

for i in range(len(Tickers[Name].RealPower)):
    if Tickers[Name].RealPower[i] > 1.2 and Tickers[Name].TodayPricePRC[i] < PRC:
        C[i] = 'lime'
    elif Tickers[Name].RealPower[i] > 1.3 and Tickers[Name].TodayPricePRC[i] >= -1*PRC:
        C[i] = 'green'
    elif i != 0 and Tickers[Name].RealPower[i]> 1.2 and Tickers[Name].RealPower[i-1] > 0:
        C[i] = 'green'
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
            # print('Buy in', Tickers[Name].Date[i], 'with color', C[i], 'and real power', Tickers[Name].RealPower[i])

    if status == 'IN':

        if C[i] == 'firebrick':
            SellPrice = Tickers[Name].LowPrice[i]
            SellDate = Tickers[Name].Date[i]
            status = 'OUT'
            Trades[BuyDate + '\t' + SellDate + '\t' + '%10s'%('Firebrick')] = (0.988*(SellPrice-BuyPrice)/BuyPrice*100)

        if C[i] == 'red' and Danger == 0:
            Danger = 1
            DangerDay = i

        if C[i] == 'red' and Danger == 1 and i == DangerDay + 1:
            Danger = 2

        if C[i] == 'red' and Danger == 2 and i == DangerDay + 2:
            SellPrice = Tickers[Name].LowPrice[i]
            SellDate = Tickers[Name].Date[i]
            status = 'OUT'
            Trades[BuyDate + '\t' + SellDate + '\t' + '%10s'%('Red')] = (0.988*(SellPrice-BuyPrice)/BuyPrice*100)

        if C[i] != 'red' and Danger != 0:
            Danger = 0
profit = 1
for Date in Trades:
    print(Date, '\t', Trades[Date])
    profit *= (1 + Trades[Date]/100)

print('Profit:', (profit-1)*100)


    



    


    
    



