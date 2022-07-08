
import datetime
import time
from Application.Utility.AdvancedPlot import advancedPlot
from Application.Utility.DateConverter import jalali_to_gregorian
from Application.Utility.Indicators.IndicatorService import calculateIchimoko, calculateMacd
from Domain.Models.TickerOfflineData import tickersGroupData
import requests

date = '1401-03-17'
ID = 12345

data = tickersGroupData(ID, datetime.datetime.strptime(jalali_to_gregorian(date), "%Y-%m-%d"))

ap = advancedPlot(1, 1, date+ ' ' + str(ID))

ap.ax.plot(data.time, data.index)
ap.ax.plot(data.time, data.indexMa)

# ap.ax[1].plot(data.time, data.slope)
# ap.ax[1].plot(data.time, data.slopeMA)
# ap.ax[1].plot(data.time, [0 for _ in range(len(data.time))],'black')
# ap.ax[1].plot(data.time, [0.03 for _ in range(len(data.time))],'red') # 0.03 for 1234
# ap.ax[1].plot(data.time, [-0.03 for _ in range(len(data.time))],'red')

if data.index[5] < sum(data.index[:5])/5:
    trend = 'down'
else:
    trend = 'up'

for i in range(15, len(data.index)):

    if trend == 'down':
        if data.index[i] > min(data.index[i-15:i]) + 0.1 and data.index[i] > data.indexMa[i]:# or data.index[i] > max(data.index[i-15:i]) + 0.05:
            trend = 'up'
            print(data.time[i], trend)
            continue
    if trend == 'up':
        if data.index[i] < max(data.index[i-15:i]) - 0.1 and data.index[i] < data.indexMa[i]:# or data.index[i] < min(data.index[i-15:i]) - 0.05:
            trend = 'down'
            print(data.time[i], trend)
            continue

    # if max15-min15 > 0.15:
    #     if trend == 'down' and data.index[i] > min15 + 0.1 and data.index[i-min(i, 20)] > min15 < data.index[i]:
    #         trend = 'up'
    #         print(data.time[i], 'up 1')
    #         continue
    #     if trend == 'up' and data.index[i] < max15 - 0.1 and data.index[i-min(i, 20)] < max15 > data.index[i]:
    #         trend = 'down'
    #         print(data.time[i], 'down 1')
    #         continue
    # else:
    #     if trend == 'down' and data.index[i] > max15 + 0.05:
    #         trend = 'up'
    #         print(data.time[i], 'up 2')
    #         continue
    #     if trend == 'up' and data.index[i] < min15 - 0.05:
    #         trend = 'down'
    #         print(data.time[i], 'down 2')
    #         continue

ap.run()

