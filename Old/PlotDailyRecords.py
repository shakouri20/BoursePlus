from DateConverter import jalali_to_gregorian
from SqlServerDataBaseLib import *
import os
import matplotlib.pyplot as plt
from math import log10

import datetime

os.system('cls')

DB = DatabaseConnection()
DB.connect()

Name = 'تکشا'
Date = '1400-06-23'
decimateNum = 3

# find ID
cmd = f"""
select ID from tickers where farsiTicker = '{Name}'"""
DB.execute(cmd)
result = DB.fetchall()
ID = result[0]['ID'] 

ID = 66210395067138534

cmd = f'''
select * from OnlineData 
where ID = {ID} and time > '{jalali_to_gregorian(Date)} 09:03' and
time < '{jalali_to_gregorian(Date)} 13:03' order by time asc'''
DB.execute(cmd)

TodayPrice = []
LastPrice = []
LastPricePRC = []
time = []

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

RealPowerVolumeProduct = []

RealBuyVolume = []
RealBuyNumber = []
RealSellVolume = []
RealSellNumber = []

decimateCounter = 0

perCapitaBuy = []
perCapitaSell = []

perCapitaBuyDif = []
perCapitaSellDif = []

for row in DB.cursor:

    decimateCounter += 1

    if decimateCounter == decimateNum:

        time.append(row['Time'].strftime("%Y-%m-%d %H:%M:%S"))
        # time.append(row['Time'])

        TodayPrice.append(row['TodayPrice'])
        
        LastPrice.append(row['LastPrice'])
        LastPricePRC.append(row['LastPricePRC'])

        
        if row['RealBuyNumber']!=0 and row['RealSellNumber']!=0:
            perCapitaBuy.append(row['LastPrice']*row['RealBuyVolume']/row['RealBuyNumber']/10000000)
            perCapitaSell.append(row['LastPrice']*row['RealSellVolume']/row['RealSellNumber']/10000000)

        RealPower.append(row['RealPower'])
        if(len(RealPowerDif) == 0):
            RealPowerDif.append(1)
            perCapitaBuyDif.append(0)
            perCapitaSellDif.append(0)
        elif row['RealBuyNumber']!=LastRealBuyNumber  and row['RealSellVolume']!=LastRealSellVolume and row['RealSellNumber']!=LastRealSellNumber:
            RealPowerDif.append((((row['RealBuyVolume']-LastRealBuyVolume)/(row['RealBuyNumber']-LastRealBuyNumber))/(((row['RealSellVolume']-LastRealSellVolume)/(row['RealSellNumber']-LastRealSellNumber)))))
            perCapitaBuyDif.append(row['LastPrice']*(row['RealBuyVolume']-LastRealBuyVolume)/(row['RealBuyNumber']-LastRealBuyNumber)/10000000)
            perCapitaSellDif.append(row['LastPrice']*(row['RealSellVolume']-LastRealSellVolume)/(row['RealSellNumber']-LastRealSellNumber)/10000000)        
        else:
            RealPowerDif.append(1)
            perCapitaBuyDif.append(0)
            perCapitaSellDif.append(0)

        LastRealBuyVolume = row['RealBuyVolume']
        LastRealBuyNumber = row['RealBuyNumber']
        LastRealSellVolume = row['RealSellVolume']
        LastRealSellNumber = row['RealSellNumber']

        RealBuyVolume.append(row['RealBuyVolume'])
        RealBuyNumber.append(row['RealBuyNumber'])
        RealSellVolume.append(row['RealSellVolume'])
        RealSellNumber.append(row['RealSellNumber'])


        Volume.append(row['Volume'])

        if(len(VolumeDif) == 0):
            VolumeDif.append(0)
        else:
            VolumeDif.append((row['Volume']-lastVolume))
        lastVolume = row['Volume']

        CorporateVolume.append(row['CorporateSellVolume']-row['CorporateBuyVolume'])

        if(len(CorporateVolumeDif) == 0):
            CorporateVolumeDif.append(0)
        else:
            CorporateVolumeDif.append(((row['CorporateSellVolume']-lastCorporateSellVolume)-(row['CorporateBuyVolume']-lastCorporateBuyVolume)))
        lastCorporateSellVolume = row['CorporateSellVolume']
        lastCorporateBuyVolume = row['CorporateBuyVolume']

        decimateCounter = 0 

LastPricePRCSMAday = int(70/decimateNum)
LastPricePRCSMA = []
for i in range(len(time)):
    if i < LastPricePRCSMAday-1:
        LastPricePRCSMA.append(sum(LastPricePRC[:i+1]) / (i+1))
    else:
        LastPricePRCSMA.append(sum(LastPricePRC[i-LastPricePRCSMAday+1:i+1]) / LastPricePRCSMAday)

RealPowerSMAday = int(60/decimateNum)
RealPowerSMA = []
for i in range(len(time)):
    if i < RealPowerSMAday:
        RealPowerSMA.append(RealPower[i])
    elif RealBuyNumber[i]-RealBuyNumber[i-RealPowerSMAday] != 0 and\
        RealSellVolume[i]-RealSellVolume[i-RealPowerSMAday] != 0 and\
        RealSellNumber[i]-RealSellNumber[i-RealPowerSMAday] != 0:
        RealPowerSMA.append(((RealBuyVolume[i]-RealBuyVolume[i-RealPowerSMAday])/(RealBuyNumber[i]-RealBuyNumber[i-RealPowerSMAday]))/((RealSellVolume[i]-RealSellVolume[i-RealPowerSMAday])/(RealSellNumber[i]-RealSellNumber[i-RealPowerSMAday])))
    else:
        RealPowerSMA.append(RealPowerSMA[-1])

RealPowerDif = [log10(RealPowerDif[i]) for i in range(len(RealPowerDif))]
RealPowerSMA = [log10(RealPowerSMA[i]) for i in range(len(RealPowerSMA))]

RealPowerVolumeProduct = [RealPowerDif[i]*VolumeDif[i] for i in range(len(RealPowerDif))]

rowNum = 4
colNum = 2

fig, ax = plt.subplots(rowNum, colNum, sharex=True, figsize=(20,20), num= Name +'      '+ Date) # (width, height) in inchese)

ax[0][0].set_ylabel("LastPricePRC")
ax[0][0].plot(LastPricePRC, color='green')
ax[0][0].plot(LastPricePRCSMA, color='lime')

ax[0][1].set_ylabel("LastPricePRC")
ax[0][1].plot(LastPricePRC, color='green')
ax[0][1].plot(LastPricePRCSMA, color='lime')

ax[1][0].set_ylabel("RealPower")
ax[1][0].plot(RealPower, color='blue')
ax[1][0].plot([1 for i in range(len(RealPower))], color='black')

ax[1][1].set_ylabel("RealPowerDif")
ax[1][1].bar(time, RealPowerDif, color='green')
ax[1][1].plot(RealPowerSMA, color='purple')
ax[1][1].plot([0 for i in range(len(RealPowerDif))], color='black')
ax[1][1].plot([log10(2) for i in range(len(RealPowerDif))], color='red')
ax[1][1].plot([log10(0.5) for i in range(len(RealPowerDif))], color='red')

ax[2][0].set_ylabel("perCapitaValues")
ax[2][0].plot(time, perCapitaBuy, color='green')
ax[2][0].plot(time, perCapitaSell, color='red')

ax[2][1].set_ylabel("perCapitaDifValues")
ax[2][1].plot(time, perCapitaBuyDif, color='green')
ax[2][1].plot(time, perCapitaSellDif, color='red')


ax[3][0].set_ylabel("RealPowerVolumeProduct")
ax[3][0].bar(time, RealPowerVolumeProduct, color='blue')
ax[3][0].plot([0 for i in range(len(RealPowerVolumeProduct))], color='black')

ax[3][1].set_ylabel("VolumeDif")
ax[3][1].bar(time, VolumeDif, color='blue')
ax[3][1].bar(time, CorporateVolumeDif, color='red')

xline = [[0 for i in range(colNum)] for j in range(rowNum)]

for i in range(rowNum):
    for j in range(colNum):
        yMin, yMax = ax[i][j].get_ylim()
        xline[i][j], = ax[i][j].plot([min(time), min(time)],[yMin,yMax])


fig.tight_layout()
mng = plt.get_current_fig_manager()
mng.window.state('zoomed')

def on_move(event):
    # get the x and y pixel coords
    x, y = event.x, event.y
    if event.inaxes:
        for i in range(rowNum):
            for j in range(colNum):
                xline[i][j].set_xdata(event.xdata)

        fig.canvas.draw()
        fig.canvas.flush_events()

binding_id = plt.connect('motion_notify_event', on_move)

plt.show()

DB.close()

