from Classes import Ticker, getTickers
import matplotlib.pyplot as plt

Name = 'زمگسا'
TickerNames = [Name]
Tickers = getTickers(TickerNames, '1399-05-21', '1400-12-04')

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

status = 'OUT'
Trades = {}
Profit = 0
BuyPrice = 0
SellPrice = 0
BuyDate = ''
SellDate = ''

for i in range(len(Tickers[Name].Date)):

    if status == 'OUT':
        
        if EMA[i] > SMA[i] and SMA[i] != 0 and EMA[i] != 0 :
            status = 'IN'
            BuyPrice = Tickers[Name].HighPrice[i]
            BuyDate = Tickers[Name].Date[i]
            # print('Buy in', Tickers[Name].Date[i], 'with color', C[i], 'and real power', Tickers[Name].RealPower[i])

    if status == 'IN':

        if EMA[i] < SMA[i]:
            SellPrice = Tickers[Name].LowPrice[i]
            SellDate = Tickers[Name].Date[i]
            status = 'OUT'
            Trades[BuyDate + '\t' + SellDate] = (0.988*(SellPrice-BuyPrice)/BuyPrice*100)

        
profit = 1
for Date in Trades:
    print(Date, '\t', Trades[Date])
    profit *= (1 + Trades[Date]/100)

print('Profit:', (profit-1)*100)


plt.plot(Tickers[Name].Date, Tickers[Name].TodayPrice, 'green')
plt.plot(Tickers[Name].Date, SMA, 'red')
plt.plot(Tickers[Name].Date, EMA, 'blue')
plt.show()


    



    


    
    



