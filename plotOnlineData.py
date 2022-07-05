from math import log10
import matplotlib.pyplot as plt
from Application.Services.ReadData.ReadOnline.OnlineDataHandler import onlineDataHandler
from Application.Utility.DateConverter import jalali_to_gregorian
from Infrastructure.Repository.OfflineDataRepository import offlineData_repo
from Infrastructure.Repository.OnlineDataRepository import onlineData_repo
from Infrastructure.Repository.TickerRepository import ticker_repo
# from ta.volatility import BollingerBands
import pandas as pd
from Application.Services.ReadData.ReadOffline.ReadOfflineServices import read_offline_services
from Domain.ImportEnums import *
from Application.Utility.Indicators.IndicatorService import calculateRsi, calculateSma

date = '1400-12-11'
name = 'شپنا'

desiredPeriod = 15
timeLength = 60
showOrdersBoardData = False

ID = ticker_repo().read_by_name(name)['ID']
# ID = 1234
# name = ticker_repo().read_by_ID(ID)['FarsiTicker']
dataHandler = onlineDataHandler([ID], None)
dataHandler.set_data(onlineData_repo().read_onlineData_by_ID_and_day(ID, jalali_to_gregorian(date)))

####################### calculate sampling time #######################
time = dataHandler.time()[ID]
timeDifs = []
for i in range(1, len(time)):
    timeDifs.append((time[i]-time[i-1]).total_seconds())

samplingTime = int(sum(timeDifs)/len(timeDifs))
decNum = max(int(desiredPeriod/samplingTime), 1)
period = samplingTime * decNum
length = int(timeLength / period)
#######################################################################
# data
time = dataHandler.time(decNum)[ID]
lastPrice = dataHandler.lastPrice(decNum)[ID]
lastPricePRC = dataHandler.lastPricePRC(decNum)[ID]
realPower = dataHandler.realPower(decNum)[ID]
perCapitaBuy = dataHandler.perCapitaBuy(decNum)[ID]
perCapitaSell = dataHandler.perCapitaSell(decNum)[ID]
volumeDif = dataHandler.volumeDif(decNum, length= length)[ID]
clientVolumeDif = dataHandler.clientVolumeDif(decNum, length= length)[ID]
realPowerDif = [log10(thisRP) for thisRP in dataHandler.realPowerDif(decNum, length= length)[ID]]
realPowerDif10 = [log10(thisRP) for thisRP in dataHandler.realPowerDif(decNum, length= length*10)[ID]]
rpvp = dataHandler.rpvp(decNum, length= length)[ID]
perCapitaBuyDif = dataHandler.perCapitaBuyDif(decNum, length= length)[ID]
perCapitaSellDif = [-element for element in dataHandler.perCapitaSellDif(decNum, length= length)[ID]]
monthlyVolume = read_offline_services.average.get_averge_volume([ID], 30)[ID]

try:
    demandValue = dataHandler.demandValue(decNum)[ID]
    supplyValue = [-element for element in dataHandler.supplyValue(decNum)[ID]]
    demToSup = dataHandler.demandToSupplyPower(decNum)[ID]
    demandPerCapita = dataHandler.demandPerCapita(decNum)[ID]
    supplyPerCapita = [-element for element in dataHandler.supplyPerCapita(decNum)[ID]]
    supplyPrice1 = dataHandler.row1(decNum)[onlineColumns.SupplyPrice1.value][ID]
    demandPrice1 = dataHandler.row1(decNum)[onlineColumns.DemandPrice1.value][ID]

    # demSup
    risePower = [0 for i in range(len(lastPrice))]
    power = [0 for i in range(len(lastPrice))]
    for i in range(len(lastPrice)):
        if demandPrice1[i] <= lastPrice[i] <= supplyPrice1[i] and supplyPrice1[i] != demandPrice1[i]:
            risePower[i] = (lastPrice[i]-demandPrice1[i])/(supplyPrice1[i]-demandPrice1[i])*100
        elif lastPrice[i] < demandPrice1[i]:
            risePower[i] = 1
    for i in range(len(lastPrice)):
        tempDemToSup = risePower[max(i-int(10*15/period), 0):i+1]
        power[i] = sum(tempDemToSup)/len(tempDemToSup)

except:
    pass

averageVolume = monthlyVolume / (3.5*60*60) * timeLength
normalVolume = [log10(thisVolume/averageVolume) if thisVolume > 0 else -1 for thisVolume in volumeDif]

oneConstant = [1 for i in range(len(time))]
Constant07 = [0.7 for i in range(len(time))]
Constant05 = [-0.5 for i in range(len(time))]
zeroConstant = [0 for i in range(len(time))]
Constant15 = [15 for i in range(len(time))]

rpnvs = [normalVolume[i] + realPower[i] for i in range(len(time))]

# price moving average
pricesMA = calculateSma(lastPricePRC, 12, True)


# # powerMA
# minAllowedPrice = dataHandler.minAllowedPrice()[ID]
# powerMA = []
# firstindex = -1
# lastIndex = -1
# for i in range(len(lastPrice)):
#     if lastPrice[i] == minAllowedPrice:
#         if firstindex != -1:
#             powerMA += calculateSma(power[firstindex:lastIndex+1], 20, True)
#             firstindex = -1
#         powerMA.append(0)
#     elif firstindex == -1:
#         firstindex = i
#         lastIndex = i
#     else:
#         lastIndex = i

# if firstindex != -1:
#     powerMA += calculateSma(power[firstindex:], 20, True)


# indicators

# # rsi
# minAllowedPrice = dataHandler.minAllowedPrice()[ID]
# rsi = []
# firstindex = -1
# lastIndex = -1
# for i in range(len(lastPrice)):
#     if lastPrice[i] == minAllowedPrice:
#         if firstindex != -1:
#             rsi += calculateRsi(lastPrice[firstindex:lastIndex+1], fillna= True, length= 14*3)
#             firstindex = -1
#         rsi.append(0)
#     elif firstindex == -1:
#         firstindex = i
#         lastIndex = i
#     else:
#         lastIndex = i

# if firstindex != -1:
#     rsi += calculateRsi(lastPrice[firstindex:], fillna= True, length= 14)

# # bollinger
# yesterdayprice = dataHandler.yesterdayPrice()[ID]
# bb = BollingerBands(pd.Series(lastPrice), fillna= True, window= 20)

# bbh = bb.bollinger_hband().to_list()
# bbl = bb.bollinger_lband().to_list()
# bbm = bb.bollinger_mavg().to_list()

# bbh = [(bbh[i]-yesterdayprice)/yesterdayprice*100 for i in range(len(bbh))]
# bbm = [(bbm[i]-yesterdayprice)/yesterdayprice*100 for i in range(len(bbm))]
# bbl = [(bbl[i]-yesterdayprice)/yesterdayprice*100 for i in range(len(bbl))]

# cloudWidth = [(bbh[i]-bbl[i]) for i in range(len(bbl))]
# # bbhDemandPriceDistance = [(demandPrice1[i]-bbh[i])/demandPrice1[i]*100 for i in range(len(bbh))]
# bbhLastPriceDistance = [(lastPrice[i]-bbh[i])/lastPrice[i]*100 for i in range(len(bbh))]

# plot
rowNum = 6
colNum = 2
barWidth = 0.00001 * period

fig, ax = plt.subplots(rowNum, colNum, sharex=True, figsize=(20,20), num= name +'      '+ date) # (width, height) in inchese)

ax[0][0].plot(time, lastPrice, color='blue', label= 'LastPrice')
ax[0][0].legend()
ax[0][0].grid()

ax[0][1].plot(time, lastPricePRC, color='blue', label= 'LastPricePRC')
ax[0][1].plot(time, pricesMA, color='red', label= 'MA')
# ax[0][1].plot(time, [-2.75 for i in range(len(lastPricePRC))], color='red')

# ax[0][1].plot(time, bbh, color='black')
# ax[0][1].plot(time, bbl, color='black')
# ax[0][1].plot(time, bbm, color='orange')
ax[0][1].legend()
ax[0][1].grid()

# ax[1][0].plot(time, realPower, color='blue', label= 'RP')
# ax[1][0].plot(time, powerMA, color='red')
ax[1][0].plot(time, Constant15 , color='black')
# ax[1][0].plot(time, Constant07 , color='black')
ax[1][0].legend()
ax[1][0].grid()

ax[1][1].plot(time, realPowerDif, color='green', label= 'RPDifLog')
ax[1][1].plot(time, realPowerDif10, color='blue', label= 'RPDifLog10')
ax[1][1].plot(time, zeroConstant, color='black')
ax[1][1].plot(time, [log10(2) for i in range(len(realPowerDif))], color='red')
ax[1][1].plot(time, [log10(0.5) for i in range(len(realPowerDif))], color='red')
ax[1][1].legend()
ax[1][1].grid()

ax[2][0].plot(time, perCapitaBuy, color='green', label= 'PCB')
ax[2][0].plot(time, perCapitaSell, color='red', label= 'PCS')
# ax[2][0].plot(time, bbhLastPriceDistance, color='blue', label= 'bbhDPD')
# ax[2][0].plot(time, rsi, color='blue', label= 'RSI')
# ax[2][0].plot(time, Constant05 , color='black')
ax[2][0].legend()
ax[2][0].grid()

# ax[2][1].plot(time, volumeDif, color='blue', label= 'VolumeDif')
ax[2][1].plot(time, realPower, color='blue', label= 'realPower')
ax[2][1].legend()
ax[2][1].grid()

ax[3][0].plot(time, perCapitaBuyDif, color='green', label= 'PCBDif')
ax[3][0].plot(time, perCapitaSellDif, color='red', label= 'PCSDif')
ax[3][0].plot(time, zeroConstant, color='black')
ax[3][0].legend()
ax[3][0].grid()

# ax[3][1].plot(time,  volumeDif, color='blue', label= 'VolumeDif')
ax[3][1].plot(time,  normalVolume, color='blue', label= 'normalVolume')
ax[3][1].plot(time, zeroConstant, color='black')
ax[3][1].legend()
ax[3][1].grid()

ax[4][0].plot(time, zeroConstant, color='black')
ax[4][0].legend()
ax[4][0].grid()

ax[4][1].plot(time, rpvp, color='green', label= 'rpvp')
ax[4][1].plot(time, zeroConstant, color='black')
ax[4][1].legend()
ax[4][1].grid()

ax[5][0].plot(time, zeroConstant, color='black')
ax[5][0].grid()

# ax[5][1].plot(time, rpnvs, color='red', label= 'rpnvs')
ax[5][1].plot(time, zeroConstant, color='black')
ax[5][1].legend()
ax[5][1].grid()

try:
    ax[1][0].plot(time, power, color='blue', label= 'demandPower')
    ax[4][0].plot(time, demandValue, color='green', label= 'DemandValue')
    ax[4][0].plot(time, supplyValue, color='red', label= 'SupplyValue')
    ax[5][0].plot(time, demandPerCapita, color='green', label= 'demPerCapita')
    ax[5][0].plot(time, supplyPerCapita, color='red', label= 'SupplyPerCapita')
    ax[5][1].bar(time, demToSup, color='red', label= 'DemToSup', width= barWidth)
    ax[0][0].plot(time, supplyPrice1, color='red')
    ax[0][0].plot(time, demandPrice1, color='green')
except:
    pass

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

fig.canvas.mpl_connect('button_press_event', on_click)

plt.show()
