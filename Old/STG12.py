from math import log10
from Classes import Ticker, getTickers
import matplotlib.pyplot as plt

Name = 'شپنا'
TickerNames = [Name]
Tickers = getTickers(TickerNames, '1397-09-22', '1398-12-07')

# RealPower
RealPower = [10*log10(Tickers[Name].RealPower[i]) for i in range(len(Tickers[Name].RealPower))]
OpenPricePRC = [(Tickers[Name].OpenPrice[i] - Tickers[Name].YesterdayPrice[i])/Tickers[Name].YesterdayPrice[i]*100 for i in range(len(Tickers[Name].OpenPrice))]

# Color Set
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

# EMA and SMA
SMAday = 10
EMAday = 5
EMAMultiplier = 2/(EMAday + 1)

SMA = [0 for i in range(len(Tickers[Name].Date))]
EMA = [0 for i in range(len(Tickers[Name].Date))]


for i in range(SMAday - 1, len(Tickers[Name].Date)):
    SMA[i] = sum(Tickers[Name].TodayPrice[i-SMAday+1:i+1]) / SMAday
for i in range(EMAday - 1, len(Tickers[Name].Date)):
    if i == EMAday - 1:
        EMA[i] = sum(Tickers[Name].TodayPrice[i-EMAday+1:i+1]) / EMAday
    else:
        EMA[i] = EMA[i - 1] + (Tickers[Name].TodayPrice[i] - EMA[i - 1]) * EMAMultiplier

# STG1 results
status = 'OUT'
Trades = {}
Profit = 0
BuyPrice = 0
SellPrice = 0
Danger = 0
DangerDay = 0
BuyDate = ''
SellDate = ''

P1 = [0 for i in range(len(Tickers[Name].Date))]

for i in range(len(Tickers[Name].Date)):

    if status == 'OUT':
        P1[i] = 0
        if C[i] == 'lime' or C[i] == 'green':
            P1[i] = 10
            status = 'IN'
            BuyPrice = Tickers[Name].HighPrice[i]
            BuyDate = Tickers[Name].Date[i]
            # print('Buy in', Tickers[Name].Date[i], 'with color', C[i], 'and real power', Tickers[Name].RealPower[i])

    if status == 'IN':
        P1[i] = 10
        if C[i] == 'firebrick':
            P1[i] = 0
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
            P1[i] = 0
            SellPrice = Tickers[Name].LowPrice[i]
            SellDate = Tickers[Name].Date[i]
            status = 'OUT'
            Trades[BuyDate + '\t' + SellDate + '\t' + '%10s'%('Red')] = (0.988*(SellPrice-BuyPrice)/BuyPrice*100)

        if C[i] != 'red' and Danger != 0:
            Danger = 0
            
# Calculate STG1 total Profit
profit = 1
for Date in Trades:
    print(Date, '\t', Trades[Date])
    profit *= (1 + Trades[Date]/100)

print('Profit:', (profit-1)*100, '\n')

# STG2 results
status = 'OUT'
Trades = {}
Profit = 0
BuyPrice = 0
SellPrice = 0
BuyDate = ''
SellDate = ''

P2 = [0 for i in range(len(Tickers[Name].Date))]

for i in range(len(Tickers[Name].Date)):

    if status == 'OUT':
        P2[i] = 0
        if EMA[i] > SMA[i] and SMA[i] != 0 and EMA[i] != 0 :
            P2[i] = 10
            status = 'IN'
            BuyPrice = Tickers[Name].TodayPrice[i]
            BuyDate = Tickers[Name].Date[i]
            # print('Buy in', Tickers[Name].Date[i], 'with color', C[i], 'and real power', Tickers[Name].RealPower[i])

    if status == 'IN':
        P2[i] = 10
        if (EMA[i] - SMA[i]) / SMA[i] < 0:
            P2[i] = 0
            SellPrice = Tickers[Name].TodayPrice[i]
            SellDate = Tickers[Name].Date[i]
            status = 'OUT'
            Trades[BuyDate + '\t' + SellDate] = (0.988*(SellPrice-BuyPrice)/BuyPrice*100)


# Calculate STG2 total Profit
profit = 1
for Date in Trades:
    print(Date, '\t', Trades[Date])
    profit *= (1 + Trades[Date]/100)

print('Profit:', (profit-1)*100)


ax1 = plt.subplot(311)
plt.plot(Tickers[Name].Date, Tickers[Name].TodayPricePRC, color= 'blue')
plt.scatter(Tickers[Name].Date, RealPower, c= C, linewidths=0, s= 20)
plt.plot(Tickers[Name].Date, P1, color= 'black')
plt.plot(Tickers[Name].Date, P2, color= 'pink')

plt.plot([0 for i in range(len(Tickers[Name].Date))], color= 'black')

plt.subplot(312, sharex= ax1)
plt.plot([0 for i in range(len(Tickers[Name].Date))], color= 'green')
plt.bar(Tickers[Name].Date, Tickers[Name].Volume, color='black')
plt.bar(Tickers[Name].Date, [Tickers[Name].CorporateSellVolume[i] - Tickers[Name].CorporateBuyVolume[i] for i in range(len(Tickers[Name].Date))], color= 'red')

plt.subplot(313, sharex= ax1)
plt.plot(Tickers[Name].Date, [EMA[i] - SMA[i] for i in range(len(Tickers[Name].Date))])
plt.plot([0 for i in range(len(Tickers[Name].Date))], color= 'black')

plt.show()

    



    


    
    



