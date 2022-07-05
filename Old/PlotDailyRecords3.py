from DateConverter import jalali_to_gregorian
from SqlServerDataBaseLib import *
import os
import matplotlib.pyplot as plt
from math import log10

import datetime

os.system('cls')

DB = DatabaseConnection()
DB.connect()

Name = 'زمگسا'
Date1 = '1400-05-05'
Date2 = '1400-05-20'

cmd = '''
select * from OnlineData 
inner join Tickers on Tickers.ID = OnlineData.ID and FarsiTicker = '{}' and time > '{} 09:03' and time < '{} 13:03' order by time asc
'''.format(Name, jalali_to_gregorian(Date1), jalali_to_gregorian(Date2))
DB.execute(cmd)

TodayPrice = []
LastPrice = []
LastPricePRC = []
time = []
timeFormat = []

#Volume
Volume = []
VolumeDif = []
lastVolume = 0
#CorporateVolume
CorporateVolume = []
CorporateVolumeDif = []
lastCorporateSellVolume = 0
lastCorporateBuyVolume = 0
# realPower
RealPower = []
RealPowerDif = []
LastRealBuyVolume = 0
LastRealBuyNumber = 0
LastRealSellVolume = 0
LastRealSellNumber = 0

RealBuyVolume = []
RealBuyNumber = []
RealSellVolume = []
RealSellNumber = []

for row in DB.cursor:

    time.append(row['Time'].strftime("%Y-%m-%d %H:%M:%S"))
    timeFormat.append(row['Time'])

    TodayPrice.append(row['TodayPrice'])
    
    LastPrice.append(row['LastPrice'])
    LastPricePRC.append(row['LastPricePRC'])

    RealPower.append(row['RealPower'])
    if len(RealPowerDif) == 0 or (timeFormat[-1] - timeFormat[-2]) > datetime.timedelta(hours=5):
        RealPowerDif.append(1)
    elif row['RealBuyNumber']-LastRealBuyNumber != 0 and\
        row['RealSellVolume']-LastRealSellVolume != 0 and\
        row['RealSellNumber']-LastRealSellNumber != 0:
        RealPowerDif.append((((row['RealBuyVolume']-LastRealBuyVolume)/(row['RealBuyNumber']-LastRealBuyNumber))/(((row['RealSellVolume']-LastRealSellVolume)/(row['RealSellNumber']-LastRealSellNumber)))))
    else:
        RealPowerDif.append(1)

    LastRealBuyVolume = row['RealBuyVolume']
    LastRealBuyNumber = row['RealBuyNumber']
    LastRealSellVolume = row['RealSellVolume']
    LastRealSellNumber = row['RealSellNumber']

    RealBuyVolume.append(row['RealBuyVolume'])
    RealBuyNumber.append(row['RealBuyNumber'])
    RealSellVolume.append(row['RealSellVolume'])
    RealSellNumber.append(row['RealSellNumber'])


    Volume.append(row['Volume'])

    if len(VolumeDif) == 0 or (timeFormat[-1] - timeFormat[-2]) > datetime.timedelta(hours=5):
        VolumeDif.append(0)
    else:
        VolumeDif.append((row['Volume']-lastVolume))
    lastVolume = row['Volume']

    CorporateVolume.append(row['CorporateSellVolume']-row['CorporateBuyVolume'])

    if len(CorporateVolumeDif) == 0  or (timeFormat[-1] - timeFormat[-2]) > datetime.timedelta(hours=5):
        CorporateVolumeDif.append(0)
    else:
        CorporateVolumeDif.append(((row['CorporateSellVolume']-lastCorporateSellVolume)-(row['CorporateBuyVolume']-lastCorporateBuyVolume)))
    lastCorporateSellVolume = row['CorporateSellVolume']
    lastCorporateBuyVolume = row['CorporateBuyVolume']

LastPricePRCSMAday = 70
LastPricePRCSMA = []
SMACounter = 0
NewDay = False
NewDayI = 0
for i in range(len(time)):
    if (timeFormat[-1] - timeFormat[-2]) > datetime.timedelta(hours=5):
        SMACounter = 0
        NewDay = True
        NewDayI = i
    if i < LastPricePRCSMAday-1:
        LastPricePRCSMA.append(sum(LastPricePRC[:i+1]) / (i+1))
    elif NewDay == True:
        LastPricePRCSMA.append(sum(LastPricePRC[NewDayI:i+1]) / (i+1-NewDayI))
        SMACounter += 1
        if SMACounter == LastPricePRCSMAday:
            NewDay = False  
    else:
        LastPricePRCSMA.append(sum(LastPricePRC[i-LastPricePRCSMAday+1:i+1]) / LastPricePRCSMAday)

RealPowerSMAday = 100
RealPowerSMA = []
SMACounter = 0
NewDay = False
NewDayI = 0
for i in range(len(time)):
    if (timeFormat[-1] - timeFormat[-2]) > datetime.timedelta(hours=5):
        SMACounter = 0
        NewDay = True
        NewDayI = i
    if i < RealPowerSMAday:
        RealPowerSMA.append(RealPower[i])
    elif NewDay == True:
        LastPricePRCSMA.append(RealPower[i])
        SMACounter += 1
        if SMACounter == LastPricePRCSMAday:
            NewDay = False
    elif RealBuyNumber[i]-RealBuyNumber[i-RealPowerSMAday] != 0 and\
        RealSellVolume[i]-RealSellVolume[i-RealPowerSMAday] != 0 and\
        RealSellNumber[i]-RealSellNumber[i-RealPowerSMAday] != 0:
        RealPowerSMA.append(((RealBuyVolume[i]-RealBuyVolume[i-RealPowerSMAday])/(RealBuyNumber[i]-RealBuyNumber[i-RealPowerSMAday]))/((RealSellVolume[i]-RealSellVolume[i-RealPowerSMAday])/(RealSellNumber[i]-RealSellNumber[i-RealPowerSMAday])))
    else:
        RealPowerSMA.append(RealPowerSMA[-1])

RealPowerDif = [log10(RealPowerDif[i]) for i in range(len(RealPowerDif))]
RealPowerSMA = [log10(RealPowerSMA[i]) for i in range(len(RealPowerSMA))]



fig, ax = plt.subplots(4, sharex=True, figsize=(14,14)) # (width, height) in inchese)

# par1 = ax[0].twinx()

ax[0].set_ylabel("LastPricePRC")
# par1.set_ylabel("RealPower")
ax[0].plot(time, LastPricePRC, color='green', label= Name[::-1] +'      '+ Date1)
ax[0].plot(time, LastPricePRCSMA, color='lime')
ax[0].plot(time, [0 for i in range(len(LastPricePRC))], color='red')
ax[0].legend()

# p2, = par1.plot(time, RealPower, color='blue')
# par1.plot(time, RealPowerSMA, color='purple')
# par1.plot(time, [1 for i in range(len(RealPower))], color='black')

ax[1].set_ylabel("RealPower")
ax[1].plot(time, RealPower, color='blue')
ax[1].plot(time, [1 for i in range(len(RealPower))], color='black')

# lns = [p1, p2, p3, p4]
# host.legend(handles=lns, loc='best')

# right, left, top, bottom
# par2.spines['right'].set_position(('outward', 50))
# par3.spines['right'].set_position(('outward', 120))

# ax[0].yaxis.label.set_color(p1.get_color())
# par1.yaxis.label.set_color(p2.get_color())

ax[2].set_ylabel("VolumeDif")
ax[2].bar(time, VolumeDif, color='blue')
ax[2].bar(time, CorporateVolumeDif, color='red')

ax[3].set_ylabel("RealPowerDif")
ax[3].bar(time, RealPowerDif, color='green')
ax[3].plot(time, RealPowerSMA, color='purple')
ax[3].plot(time, [0 for i in range(len(RealPowerDif))], color='black')

fig.tight_layout()

mng = plt.get_current_fig_manager()
mng.window.state('zoomed')

plt.show()

DB.close()

