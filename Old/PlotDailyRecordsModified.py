from DateConverter import jalali_to_gregorian
from SqlServerDataBaseLib import *
import os
import matplotlib.pyplot as plt
from math import log10
from datetime import datetime, timedelta
from ta.volatility import BollingerBands
from ta.momentum import RSIIndicator
import pandas as pd

os.system('cls')

DB = DatabaseConnection()
DB.connect()


Name = 'تپکو'
Date = '1400-08-05'
decimateNum = 1

# find ID
cmd = f"""
select ID from tickers where farsiTicker = '{Name}'"""
DB.execute(cmd)
result = DB.fetchall()
ID = result[0]['ID'] 


cmd = f'''
select * from OnlineData 
where ID = {ID} and time > '{jalali_to_gregorian(Date)} 09:03' and
time < '{jalali_to_gregorian(Date)} 13:03' order by time asc'''
DB.execute(cmd)

# regular
time = []
TodayPrice = []
LastPrice = []
LastPricePRC = []
Volume = []
BuyVolume = []
RealPower = []
RealBuyVolume = []
RealBuyNumber = []
RealSellVolume = []
RealSellNumber = []
CorporateBuyVolume = []
CorporateSellVolume = []
perCapitaBuy = []
perCapitaSell = []
RealPowerVolumeProduct = []
DemandVolume = []
SupplyVolume = []
DemandValue = []
SupplyValue = []
DemandPerCapita = []
SupplyPerCapita = []

DemToSup = []
DemToSupV2 = []

# diff
VolumeDif = []
CorporateVolumeDif = []
RealPowerDif = []
perCapitaBuyDif = []
perCapitaSellDif = []

decimateCounter = 0

for row in DB.cursor:

    if 1:
    # if row['Time'].hour == 10 and row['Time'].minute >= 33 or row['Time'].hour > 10:

        decimateCounter += 1

        if decimateCounter == decimateNum:

            #  regualar***********************************************************


            if len(time) == 0 or row['RealBuyVolume']+row['CorporateBuyVolume'] > 0.96*row['Volume']:

                Volume.append(row['Volume'])
                BuyVolume.append(row['RealBuyVolume']+row['CorporateBuyVolume'])
                RealBuyVolume.append(row['RealBuyVolume'])
                RealBuyNumber.append(row['RealBuyNumber'])
                RealSellVolume.append(row['RealSellVolume'])
                RealSellNumber.append(row['RealSellNumber'])
                CorporateBuyVolume.append(row['CorporateBuyVolume'])
                CorporateSellVolume.append(row['CorporateSellVolume'])
            else:
                Volume.append(Volume[-1])
                BuyVolume.append(BuyVolume[-1])
                RealBuyVolume.append(RealBuyVolume[-1])
                RealBuyNumber.append(RealBuyNumber[-1])
                RealSellVolume.append(RealSellVolume[-1])
                RealSellNumber.append(RealSellNumber[-1])
                CorporateBuyVolume.append(CorporateBuyVolume[-1])
                CorporateSellVolume.append(CorporateSellVolume[-1])
                
            time.append(row['Time']) # .strftime("%Y-%m-%d %H:%M:%S")
            TodayPrice.append(row['TodayPrice']) 
            LastPrice.append(row['LastPrice'])
            LastPricePRC.append((row['LastPrice']-row['YesterdayPrice'])/row['YesterdayPrice']*100)

            perCapitaBuy.append(LastPrice[-1]*RealBuyVolume[-1]/RealBuyNumber[-1]/10000000 if RealBuyNumber[-1]!=0 else 0)
            perCapitaSell.append(LastPrice[-1]*RealSellVolume[-1]/RealSellNumber[-1]/10000000 if RealSellNumber[-1]!=0 else 0)

            RealPower.append((row['RealBuyVolume']/row['RealBuyNumber'])/(row['RealSellVolume']/row['RealSellNumber']) if row['RealBuyNumber'] !=0 or row['RealSellNumber'] != 0 else 1)

            # DemToSup
            for i in range(1, 6):
                if row[f'DemandPrice{i}'] < row['MinAllowedPrice']:
                    row[f'DemandVolume{i}'] = 0
                if row[f'SupplyPrice{i}'] > row['MaxAllowedPrice']:
                    row[f'SupplyVolume{i}'] = 0
            DemandVolume.append(row['DemandVolume1']+row['DemandVolume2']+row['DemandVolume3']+row['DemandVolume4']+row['DemandVolume5'])
            SupplyVolume.append(-row['SupplyVolume1']-row['SupplyVolume2']-row['SupplyVolume3']-row['SupplyVolume4']-row['SupplyVolume5'])
            DemandValue.append(DemandVolume[-1]*LastPrice[-1]/10000000)
            SupplyValue.append(SupplyVolume[-1]*LastPrice[-1]/10000000)

            DemandNumber = row['DemandNumber1'] + row['DemandNumber2'] + row['DemandNumber3'] + row['DemandNumber4'] + row['DemandNumber5']
            SupplyNumber = row['SupplyNumber1'] + row['SupplyNumber2'] + row['SupplyNumber3'] + row['SupplyNumber4'] + row['SupplyNumber5']

            if DemandNumber != 0:
                DemandPerCapita.append(DemandValue[-1]/DemandNumber)
            else:
                DemandPerCapita.append(0)
            
            if SupplyNumber != 0:
                SupplyPerCapita.append(SupplyValue[-1]/SupplyNumber)
            else:
                SupplyPerCapita.append(0)

            if DemandVolume[-1] == 0:
                DemToSup.append(-3)
            elif SupplyVolume[-1] == 0:
                DemToSup.append(3)
            else:
                DemToSup.append(log10(-DemandVolume[-1]/SupplyVolume[-1]))

            if DemandPerCapita[-1] == 0 and SupplyPerCapita[-1] != 0:
                DemToSupV2.append(SupplyValue[-1]*log10(-SupplyPerCapita[-1]))
            elif DemandPerCapita[-1] != 0 and SupplyPerCapita[-1] == 0:
                DemToSupV2.append(DemandValue[-1]*log10(DemandPerCapita[-1]))
            elif DemandPerCapita[-1] == 0 and SupplyPerCapita[-1] == 0:
                DemToSupV2.append(0)
            else:
                DemToSupV2.append(DemandValue[-1]*log10(DemandPerCapita[-1])+SupplyValue[-1]*log10(-SupplyPerCapita[-1]))

            # diffs**************************************************************

            if len(RealPowerDif) == 0:
                RealPowerDif.append(1)
                perCapitaBuyDif.append(0)
                perCapitaSellDif.append(0)
                VolumeDif.append(0)
                CorporateVolumeDif.append(0)
            else:
                timeDelta = time[-1]-time[-2]
                if timeDelta < timedelta(seconds = 30*decimateNum):
                    VolumeDif.append(Volume[-1]-Volume[-2])
                else:
                    VolumeDif.append((Volume[-1]-Volume[-2])*20/(timeDelta.total_seconds()))
                    print(time[-1], timeDelta.total_seconds())

                CorporateVolumeDif.append(((CorporateSellVolume[-1]-CorporateSellVolume[-2])-(CorporateBuyVolume[-1]-CorporateBuyVolume[-2])))
                if RealBuyNumber[-1]>RealBuyNumber[-2] and RealSellVolume[-1]>RealSellVolume[-2] and RealSellNumber[-1]>RealSellNumber[-2]:
                    RealPowerDif.append((((RealBuyVolume[-1]-RealBuyVolume[-2])/(RealBuyNumber[-1]-RealBuyNumber[-2]))/(((RealSellVolume[-1]-RealSellVolume[-2])/(RealSellNumber[-1]-RealSellNumber[-2])))))
                    perCapitaBuyDif.append(LastPrice[-1]*(RealBuyVolume[-1]-RealBuyVolume[-2])/(RealBuyNumber[-1]-RealBuyNumber[-2])/10000000)
                    perCapitaSellDif.append(-LastPrice[-1]*(RealSellVolume[-1]-RealSellVolume[-2])/(RealSellNumber[-1]-RealSellNumber[-2])/10000000)  
                else:
                    RealPowerDif.append(1)
                    perCapitaBuyDif.append(0)
                    perCapitaSellDif.append(0)

                
            decimateCounter = 0 


# moving Averages***********************************************************

LastPricePRCSMAday = int(10/decimateNum)
LastPricePRCSMA = []
for i in range(len(time)):
    if i < LastPricePRCSMAday-1:
        LastPricePRCSMA.append(sum(LastPricePRC[:i+1]) / (i+1))
    else:
        LastPricePRCSMA.append(sum(LastPricePRC[i-LastPricePRCSMAday+1:i+1]) / LastPricePRCSMAday)

RealPowerSMAday = int(30/decimateNum)
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
    if RealPowerSMA[-1] <= 0:
        RealPowerSMA[-1] = RealPowerSMA[-2]

RealPowerDif = [log10(RealPowerDif[i]) for i in range(len(RealPowerDif))]
RealPowerSMA = [log10(RealPowerSMA[i]) for i in range(len(RealPowerSMA))]

RealPowerVolumeProduct = [RealPowerDif[i]*VolumeDif[i] for i in range(len(RealPowerDif))]

# indicators

bb = BollingerBands(pd.Series(LastPrice), fillna= True, window= 20)

bbh = bb.bollinger_hband().to_list()
bbl = bb.bollinger_lband().to_list()
bbma = bb.bollinger_mavg().to_list()

rsi = RSIIndicator(pd.Series(LastPrice), fillna = True).rsi().to_list()

# rowNum = 3
# colNum = 1

# # plot
# fig, ax = plt.subplots(rowNum, colNum, sharex=True, figsize=(20,20), num= Name +'      '+ Date) # (width, height) in inchese)

# ax[0].plot(time, LastPrice, color='green', label= 'LastPrice')
# # ax[0][0].plot(time, LastPricePRCSMA, color='lime')
# ax[0].plot(time, bbh, color='blue')
# ax[0].plot(time, bbma, color='lime')
# ax[0].plot(time, bbl, color='blue')
# ax[0].legend()

# ax[1].plot(time, rsi, color='black', label= 'rsi')
# ax[1].legend()

# ax[2].plot(time, LastPricePRC, color='green', label= 'LastPricePRC')
# ax[2].legend()

# fig.tight_layout()
# mng = plt.get_current_fig_manager()
# mng.window.state('zoomed')

rowNum = 6
colNum = 2

fig, ax = plt.subplots(rowNum, colNum, sharex=True, figsize=(20,20), num= Name +'      '+ Date) # (width, height) in inchese)

ax[0][0].plot(time, LastPricePRC, color='green', label= 'LastPricePRC')
# ax[0][0].plot(time, LastPricePRCSMA, color='lime')
ax[0][0].plot(time, bbh, color='black')
ax[0][0].plot(time, bbl, color='black')
ax[0][0].plot(time, bbma, color='black')
ax[0][0].legend()

ax[0][1].plot(time, LastPricePRC, color='green', label= 'LastPricePRC')
ax[0][1].plot(time, LastPricePRCSMA, color='lime')
ax[0][1].legend()

ax[1][0].plot(time, RealPower, color='blue', label= 'RealPower')
ax[1][0].plot(time, [1 for i in range(len(RealPower))], color='black')
ax[1][0].legend()

ax[1][1].bar(time, RealPowerDif, color='green', label= 'RealPowerDif', width= 0.00015)
ax[1][1].plot(time, RealPowerSMA, color='purple')
ax[1][1].plot(time, [0 for i in range(len(RealPowerDif))], color='black')
ax[1][1].plot(time, [log10(2) for i in range(len(RealPowerDif))], color='red')
ax[1][1].plot(time, [log10(0.5) for i in range(len(RealPowerDif))], color='red')
ax[1][1].legend()

ax[2][0].plot(time, perCapitaBuy, color='green', label= 'perCapitaBuy')
ax[2][0].plot(time, perCapitaSell, color='red', label= 'perCapitaSell')
ax[2][0].legend()

ax[2][1].bar(time, perCapitaBuyDif, color='green', label= 'perCapitaBuyDif', width= 0.00015)
ax[2][1].bar(time, perCapitaSellDif, color='red', label= 'perCapitaSellDif', width= 0.00015)
ax[2][1].legend()

ax[3][0].bar(time, RealPowerVolumeProduct, color='blue', label= 'RealPowerVolumeProduct', width= 0.00015)
ax[3][0].plot(time, [0 for i in range(len(RealPowerVolumeProduct))], color='black')
ax[3][0].legend()

ax[3][1].bar(time,  VolumeDif, color='blue', label= 'VolumeDif', width= 0.00015)
ax[3][1].bar(time, CorporateVolumeDif, color='red', label= 'CorporateVolumeDif', width= 0.00015)
ax[3][1].legend()

ax[4][0].bar(time, DemandValue, color='green', label= 'DemandValue', width= 0.00015)
ax[4][0].bar(time, SupplyValue, color='red', label= 'SupplyValue', width= 0.00015)
ax[4][0].legend()

ax[4][1].bar(time, DemToSup, color='red', label= 'DemToSup', width= 0.00015)
ax[4][1].plot(time, [0 for i in range(len(DemToSup))], color='black')
ax[4][1].plot(time, [-0.6 for i in range(len(DemToSup))], color='black')
ax[4][1].legend()

ax[5][0].bar(time, DemandPerCapita, color='green', label= 'DemandPerCapita', width= 0.00015)
ax[5][0].bar(time, SupplyPerCapita, color='red', label= 'SupplyPerCapita', width= 0.00015)
ax[5][0].plot(time, [0 for i in range(len(DemToSup))], color='black')
ax[5][0].legend()

ax[5][1].bar(time, DemToSupV2, color='green', label= 'DemToSupV2', width= 0.00015)
ax[5][1].plot(time, [0 for i in range(len(DemToSup))], color='black')
ax[5][1].legend()

fig.tight_layout()
mng = plt.get_current_fig_manager()
mng.window.state('zoomed')

xline = [[0 for i in range(colNum)] for j in range(rowNum)]
for i in range(rowNum):
    for j in range(colNum):
        yMin, yMax = ax[i][j].get_ylim()
        xline[i][j], = ax[i][j].plot([min(time), min(time)],[yMin,yMax])

def on_click(event):
    # get the x and y pixel coords
    if event.inaxes:
        for i in range(rowNum):
            for j in range(colNum):
                xline[i][j].set_xdata(event.xdata)
        fig.canvas.draw()
        fig.canvas.flush_events()

# xline = [0 for j in range(rowNum)]

# for j in range(rowNum):
#     yMin, yMax = ax[j].get_ylim()
#     xline[j], = ax[j].plot([min(time), min(time)],[yMin,yMax])

# def on_click(event):
#     # get the x and y pixel coords
#     if event.inaxes:
#         for j in range(rowNum):
#             xline[j].set_xdata(event.xdata)
#     fig.canvas.draw()
#     fig.canvas.flush_events()


fig.canvas.mpl_connect('button_press_event', on_click)

plt.show()
DB.close()

