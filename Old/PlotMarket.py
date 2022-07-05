from DateConverter import jalali_to_gregorian
import datetime
from SqlServerDataBaseLib import DatabaseConnection
import os
import matplotlib.pyplot as plt

db = DatabaseConnection()
db.connect()

Date = '1400-07-18'

cmd = '''
DECLARE @Time AS datetime
SET @Time = '{} 09:05:00'
 Select Time, TodayPrice, LastPrice, LastPricePRC, MaxAllowedPrice, MinAllowedPrice, RealBuyVolume, RealBuyNumber, RealSellVolume, RealSellNumber from onlinedata
 inner join tickers on tickers.id = onlinedata.id 
 where tickers.TickerTypeID = 1 and time > @Time and time < DATEADD(hh, 5, @Time)
 order by time asc
'''.format(jalali_to_gregorian(Date)) #DATEADD(hh, 5, @Time)
# MarketTypeID in (1, 2, 3, 4, 5, 6, 7)

db.execute(cmd)

time = []
ActiveTickersNumber = []
TotRealPower = []
SellQueueNumber = []
BuyQueueNumber = []
PosNumber = []
NegNumber = []

TempNumber = 0
TempTime = datetime.datetime(2018, 1, 1)
RealBuyValue = 0
RealBuyNumber = 0
RealSellValue = 0
RealSellNumber = 0

for row in db.cursor:

    if (row['Time'] - TempTime) > datetime.timedelta(seconds=5):

        time.append(row['Time'].strftime("%Y-%m-%d %H:%M:%S"))
        TempTime = row['Time']

        TempNumber = 1
        ActiveTickersNumber.append(0)

        RealBuyValue = row['RealBuyVolume'] * row['TodayPrice']
        RealBuyNumber = row['RealBuyNumber']
        RealSellValue = row['RealSellVolume'] * row['TodayPrice']
        RealSellNumber = row['RealSellNumber']
        TotRealPower.append(0)

        SellQueueNumber.append(0)
        BuyQueueNumber.append(0)
        PosNumber.append(0)
        NegNumber.append(0)

        if row['LastPrice'] == row['MinAllowedPrice']:
            SellQueueNumber[-1] = 1
        elif row['LastPrice'] == row['MaxAllowedPrice']:
            BuyQueueNumber[-1] = 1
        elif row['LastPricePRC'] >= 0:
            PosNumber[-1] = 1
        elif row['LastPricePRC'] < 0:
            NegNumber[-1] = 1

        
    else:
        RealBuyValue += row['RealBuyVolume'] * row['TodayPrice']
        RealBuyNumber += row['RealBuyNumber']
        RealSellValue += row['RealSellVolume'] * row['TodayPrice']
        RealSellNumber += row['RealSellNumber']
        TotRealPower[-1] = (RealBuyValue/RealBuyNumber)/(RealSellValue/RealSellNumber)

        TempNumber += 1
        ActiveTickersNumber[-1] = TempNumber

        if row['LastPrice'] == row['MinAllowedPrice']:
            SellQueueNumber[-1] += 1
        elif row['LastPrice'] == row['MaxAllowedPrice']:
            BuyQueueNumber[-1] += 1
        elif row['LastPricePRC'] >= 0:
            PosNumber[-1] += 1
        elif row['LastPricePRC'] < 0:
            NegNumber[-1] += 1

SellQueueNumber = [SellQueueNumber[i]/ActiveTickersNumber[i]*100 for i in range(len(SellQueueNumber))]
BuyQueueNumber = [BuyQueueNumber[i]/ActiveTickersNumber[i]*100 for i in range(len(BuyQueueNumber))]
PosNumber = [PosNumber[i]/ActiveTickersNumber[i]*100 for i in range(len(PosNumber))]
NegNumber = [NegNumber[i]/ActiveTickersNumber[i]*100 for i in range(len(NegNumber))]

PosTickersPRC = [(BuyQueueNumber[i]+PosNumber[i]) for i in range(len(ActiveTickersNumber))]
NegTickersPRC = [(SellQueueNumber[i]+NegNumber[i]) for i in range(len(ActiveTickersNumber))]


TotRealPowerSMAday = 60
TotRealPowerSMA = []
PosTickersSMAday = 80
PosTickersSMA = []

for i in range(len(TotRealPower)):
    if i < TotRealPowerSMAday-1:
        TotRealPowerSMA.append(sum(TotRealPower[:i+1]) / (i+1))
    else:
        TotRealPowerSMA.append(sum(TotRealPower[i-TotRealPowerSMAday+1:i+1]) / TotRealPowerSMAday)

for i in range(len(TotRealPower)):
    if i < PosTickersSMAday-1:
        PosTickersSMA.append(sum(PosTickersPRC[:i+1]) / (i+1))
    else:
        PosTickersSMA.append(sum(PosTickersPRC[i-PosTickersSMAday+1:i+1]) / PosTickersSMAday)

        
f, ax = plt.subplots(nrows=2, ncols=2, sharex=True, figsize=(14,4)) # (width, height) in inches

p1, = ax[0][0].plot(time, TotRealPower, 'blue', label= 'TotalRealPower')
ax[0][0].plot(time, TotRealPowerSMA, 'red', label= 'SMA')
par1 = ax[0][0].twinx()
p2, = par1.plot(time, [TotRealPower[i]-TotRealPowerSMA[i] for i in range(len(TotRealPower))], 'green', label= 'Diff')
par1.plot(time, [0 for i in range(len(TotRealPower))], 'black')
ax[0][0].set_ylabel("TotRealPower")
par1.set_ylabel("Diff")
ax[0][0].yaxis.label.set_color(p1.get_color())
par1.yaxis.label.set_color(p2.get_color())
ax[0][0].legend()

ax[0][1].plot(time, ActiveTickersNumber, color= 'red', label= 'ActiveTickersNumber')
ax[0][1].legend()

ax[1][0].plot(time, SellQueueNumber, color= 'firebrick', label= 'SellQueue')
ax[1][0].plot(time, BuyQueueNumber, color= 'green', label= 'BuyQueue')
ax[1][0].plot(time, PosNumber, color= 'lime', label= 'Pos')
ax[1][0].plot(time, NegNumber, color= 'red', label= 'Neg')
ax[1][0].legend()

ax[1][1].plot(time, PosTickersPRC, color= 'green', label= 'POS')
ax[1][1].plot(time, NegTickersPRC, color= 'red', label= 'NEG')
ax[1][1].plot(time, PosTickersSMA, color= 'blue', label= 'POS_SMA')

ax[1][1].legend()

f.tight_layout()

plt.title(Date)

mng = plt.get_current_fig_manager()
mng.window.state('zoomed')

plt.show()

db.close()