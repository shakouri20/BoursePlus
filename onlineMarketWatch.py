
import datetime
import matplotlib.pyplot as plt
from Application.Services.DataProcess import get_data_from_web
from Application.Services.ReadData.ReadOnline.MarketWatchDataGenerator import marketWatchDataGenerator
from Application.Services.ReadData.ReadOnline.MarketWatchDataHandler import marketWatchDataHandler
from Application.Utility.AdvancedPlot import advancedPlot
from Application.Utility.DateConverter import gregorian_to_jalali
from Application.Utility.Indicators.IndicatorService import calculateSma
from Domain.Enums.MarketGroups import marketGroupType

marketWatchGen = marketWatchDataGenerator()
groups = [marketGroupType.TotalMarket.value]
marketWatchHand = marketWatchDataHandler(groups, None)

ap = advancedPlot(4, 1, gregorian_to_jalali(datetime.datetime.now().date().strftime('%Y-%m-%d')))
plt.ion()
plt.show()

while True:

    now = datetime.datetime.now()
    startTime = now.replace(hour= 9, minute= 3)
    stopTime = now.replace(hour= 12, minute= 30)
    
    if startTime < now < stopTime:

        print('', now, end= '\r')
        try:
            (onlineDataList, cacheDataDict) = get_data_from_web()
        except:
            continue

        if len(list(cacheDataDict.keys())) == 0:
            print('Data Error... Continiuing...')
            continue

        marketWatchData = marketWatchGen.get_marketWatchInfo(cacheDataDict)
        marketWatchHand.update(marketWatchData)

        times = marketWatchHand.time()[groups[0]]

        if len(times) == 0:
            continue

        lastPrices = marketWatchHand.lastPricePRCAverge()[groups[0]]
        realPowerDif = marketWatchHand.realPowerDif(length = 2)[groups[0]]
        valueDif = marketWatchHand.totalValueDif(length = 2)[groups[0]]

        slope = [0 for _ in range(len(times))]
        for i in range(5, len(times)):
            slope[i] = lastPrices[i] - lastPrices[max(i-5, 0)] # 15
            slope[i] /= ((times[i]-times[max(i-5, 0)]).total_seconds()/60)

        lastPricesMa = calculateSma(lastPrices, 30, True)
        slopeMA = calculateSma(slope, 5, True)

        ap.ax[0].clear()
        ap.ax[1].clear()
        ap.ax[2].clear()
        ap.ax[3].clear()
        ap.ax[0].plot(times, lastPrices)
        today = datetime.datetime.now().date()
        startLim = datetime.datetime(today.year, today.month, today.day, 9, 0)
        stopLim = datetime.datetime(today.year, today.month, today.day, 12, 30)
        ap.ax[0].set_xlim([startLim, stopLim])
        ap.ax[0].plot(times, lastPricesMa)
        ap.ax[0].set_ylabel('Index')
        ap.ax[1].plot(times, slope)
        ap.ax[1].plot(times, slopeMA)
        ap.ax[1].plot(times, [0 for _ in range(len(times))])
        ap.ax[1].plot(times, [0.03 for _ in range(len(times))])
        ap.ax[1].plot(times, [-0.03 for _ in range(len(times))])
        ap.ax[1].set_ylabel('Slope')
        ap.ax[2].plot(times, realPowerDif)
        ap.ax[2].plot(times, [1 for _ in range(len(times))])
        ap.ax[2].set_ylabel('RealPower')
        ap.ax[3].plot(times, valueDif)
        ap.ax[3].plot(times, [0 for _ in range(len(times))])
        ap.ax[3].set_ylabel('Value')

        plt.pause(60)
    
    else:
        plt.pause(30)
