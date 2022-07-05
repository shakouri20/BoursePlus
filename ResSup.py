from matplotlib import colors
import matplotlib.pyplot as plt
import pandas as pd
from Infrastructure.Repository.OfflineDataRepository import offlineData_repo
import mplfinance as mpf
import winsound
import numpy as np
import datetime
from ta.trend import SMAIndicator
from Domain.ImportEnums import *


def strDate_to_lineDates(strDate: str, price: int, dates: list):

    thisDate = datetime.datetime.strptime(strDate, "%Y-%m-%d") # datetime.datetime.strptime(dates[0], "%Y-%m-%d")
    delta = datetime. timedelta(days=6)
    thisDateNeg = (max((thisDate - delta), datetime.datetime.strptime(dates[0], "%Y-%m-%d"))).strftime("%Y-%m-%d")
    thisDatePos = (min((thisDate + delta), datetime.datetime.strptime(dates[-1], "%Y-%m-%d"))).strftime("%Y-%m-%d")
    return [(thisDateNeg, price), (thisDatePos, price)]
 

# read
data = offlineData_repo().read_by_farsiTicker_and_time('Time', 'HighPrice', 'LowPrice', 'OpenPrice', 'ClosePrice', 'TodayPrice', 'Volume',\
farsiTicker= 'حسیر', fromDate = '1400-05-01', toDate= '1400-12-01', outputDateType= dateType.gregorian)

# data to pd
prices = {'Date': data['Time'], 'High': data['HighPrice'], 'Low': data['LowPrice'], 'Open': data['OpenPrice'], 'Close': data['ClosePrice'], 'Volume': data['Volume']}
dataPd = pd.DataFrame(prices) 
dataPd.index = pd.DatetimeIndex(dataPd['Date'])

# Resistance and Support calc
lines = []
levels = []

def smaMethod(window):
    #  method sma
    title = 'SMA method'
    maObj= SMAIndicator(pd.Series(data['TodayPrice']), window= window,  fillna= True)
    todayMA = maObj.sma_indicator().to_list()

    if todayMA[window] > todayMA[window-1]: 
        Rising = True
    else:
        Rising = False


    for i in range(window+1, len(todayMA)):

        if todayMA[i] > todayMA[i-1] and Rising == False:
            Rising = True
            sup = min(data['LowPrice'][i-window:i])
            levels.append(sup)
            indexes = [index for index, item in enumerate(data['LowPrice'][i-window:i]) if item == sup]
            lines.append(strDate_to_lineDates(data['Date'][i-window+max(indexes)], sup, data['Date']))

        elif todayMA[i] < todayMA[i-1] and Rising == True:
            Rising = False
            res = max(data['HighPrice'][i-window:i])
            levels.append(res)
            indexes = [index for index, item in enumerate(data['HighPrice'][i-window:i]) if item == res]
            lines.append(strDate_to_lineDates(data['Date'][i-window+max(indexes)], res, data['Date']))

    return [levels, lines, title]

def sideMethod():
    # method side
    space1 = 10
    space2 = 3
    title = 'Side method'

    def isSupporSide(data, i, space1, space2):

        right = 0
        left = 0

        for j in range(1, space1+1):
            if data['LowPrice'][i] <= data['LowPrice'][i-j]:
                left += 1
            else:
                break

        for j in range(1, space1+1):
            if data['LowPrice'][i] <= data['LowPrice'][i+j]:
                right += 1
            else:
                break
        # print(left, right)
        if max(right, left) >= space1 and min(right, left) >= space2:
            return True
        else:
            return False

    def isResistanceSide(data, i, space1, space2):

        right = 0
        left = 0

        for j in range(1, space1+1):
            if data['HighPrice'][i] >= data['HighPrice'][i-j]:
                left += 1
            else:
                break

        for j in range(1, space1+1):
            if data['HighPrice'][i] >= data['HighPrice'][i+j]:
                right += 1
            else:
                break
        # print(left, right)

        if max(right, left) >= space1 and min(right, left) >= space2:
            return True
        else:
            return False


    for i in range(space1, len(data['Date'])-1-space1):
        if isSupporSide(data, i, space1, space2):
            l = data['LowPrice'][i]
            # if isFarFromLevel(l):
            levels.append(int(l))
            lines.append(strDate_to_lineDates(data['Date'][i],int(l), data['Date']))

        elif isResistanceSide(data, i, space1, space2):
            l = data['HighPrice'][i]

            # if isFarFromLevel(l):
            levels.append(int(l))
            lines.append(strDate_to_lineDates(data['Date'][i], int(l), data['Date']))

    return [levels, lines, title]

def sidePrcMethod():
    # method side
    space1 = 10
    space2 = 4
    prc = 11
    title = 'SidePRC method'

    def isSupport(data, i, space1, space2, prc):

        rightNum = 0
        leftNum = 0
        rightHighPrice = 0
        leftHighPrice = 0

        for j in range(1, space1+1):
            if data['LowPrice'][i] <= data['LowPrice'][i-j]:
                leftNum += 1
                leftHighPrice = max(data['HighPrice'][i-j], leftHighPrice)
            else:
                break

        for j in range(1, space1+1):
            if data['LowPrice'][i] <= data['LowPrice'][i+j]:
                rightNum += 1
                rightHighPrice = max(data['HighPrice'][i+j], rightHighPrice)
            else:
                break

        leftPrc = (leftHighPrice-data['LowPrice'][i])/data['LowPrice'][i]*100
        rightPrc = (rightHighPrice-data['LowPrice'][i])/data['LowPrice'][i]*100

        if leftPrc >= prc and rightPrc >= prc and max(rightNum, leftNum) >= space1 and min(rightNum, leftNum) >= space2: # and 
            # print(leftPrc, rightPrc)
            return True
        else:
            return False

    def isResistance(data, i, space1, space2, prc):

        rightNum = 0
        leftNum = 0
        rightLowPrice = 10000000
        leftLowPrice = 10000000

        for j in range(1, space1+1):
            if data['HighPrice'][i] >= data['HighPrice'][i-j]:
                leftNum += 1
                leftLowPrice = min(data['LowPrice'][i-j], leftLowPrice)
            else:
                break

        for j in range(1, space1+1):
            if data['HighPrice'][i] >= data['HighPrice'][i+j]:
                rightNum += 1
                rightLowPrice = min(data['LowPrice'][i+j], rightLowPrice)
            else:
                break

        leftPrc = (leftLowPrice-data['HighPrice'][i])/data['HighPrice'][i]*100
        rightPrc = (rightLowPrice-data['HighPrice'][i])/data['HighPrice'][i]*100

        if leftPrc <= prc and rightPrc <= prc and max(rightNum, leftNum) >= space1 and min(rightNum, leftNum) >= space2: #  and
            # print(leftPrc, rightPrc)
            return True
        else:
            return False

    for i in range(space1, len(data['Date'])-1-space1):

        if isSupport(data, i, space1, space2, prc):
            sup = data['LowPrice'][i]
            levels.append(sup)
            lines.append(strDate_to_lineDates(data['Date'][i],sup, data['Date']))

        if isResistance(data, i, space1, space2, -prc):
            res = data['HighPrice'][i]
            levels.append(res)
            lines.append(strDate_to_lineDates(data['Date'][i], res, data['Date']))

    return [levels, lines, title]

def mixMethod():
    # method side
    space1 = 10
    space2 = 4
    prc = 11
    title = 'Mix method'

    def isSupport(data, i, space1, space2, prc):

        rightNum = 0
        leftNum = 0
        rightHighPrice = 0
        leftHighPrice = 0

        for j in range(1, space1+1):
            if data['LowPrice'][i] <= data['LowPrice'][i-j]:
                leftNum += 1
                leftHighPrice = max(data['HighPrice'][i-j], leftHighPrice)
            else:
                break

        for j in range(1, space1+1):
            if data['LowPrice'][i] <= data['LowPrice'][i+j]:
                rightNum += 1
                rightHighPrice = max(data['HighPrice'][i+j], rightHighPrice)
            else:
                break

        leftPrc = (leftHighPrice-data['LowPrice'][i])/data['LowPrice'][i]*100
        rightPrc = (rightHighPrice-data['LowPrice'][i])/data['LowPrice'][i]*100

        if leftPrc >= prc and rightPrc >= prc and max(rightNum, leftNum) >= space1 and min(rightNum, leftNum) >= space2: # and 
            # print(leftPrc, rightPrc)
            return True
        else:
            return False

    def isResistance(data, i, space1, space2, prc):

        rightNum = 0
        leftNum = 0
        rightLowPrice = 10000000
        leftLowPrice = 10000000

        for j in range(1, space1+1):
            if data['HighPrice'][i] >= data['HighPrice'][i-j]:
                leftNum += 1
                leftLowPrice = min(data['LowPrice'][i-j], leftLowPrice)
            else:
                break

        for j in range(1, space1+1):
            if data['HighPrice'][i] >= data['HighPrice'][i+j]:
                rightNum += 1
                rightLowPrice = min(data['LowPrice'][i+j], rightLowPrice)
            else:
                break

        leftPrc = (leftLowPrice-data['HighPrice'][i])/data['HighPrice'][i]*100
        rightPrc = (rightLowPrice-data['HighPrice'][i])/data['HighPrice'][i]*100

        if leftPrc <= prc and rightPrc <= prc and max(rightNum, leftNum) >= space1 and min(rightNum, leftNum) >= space2: #  and
            # print(leftPrc, rightPrc)
            return True
        else:
            return False


    for i in range(space1, len(data['Time'])-space1):

        if isSupport(data, i, space1, space2, prc):
            sup = data['LowPrice'][i]
            levels.append(sup)
            lines.append(strDate_to_lineDates(data['Time'][i],sup, data['Time']))

        if isResistance(data, i, space1, space2, -prc):
            res = data['HighPrice'][i]
            levels.append(res)
            lines.append(strDate_to_lineDates(data['Time'][i], res, data['Time']))

     #  method sma
    window = 10
    maObj= SMAIndicator(pd.Series(data['TodayPrice']), window= window,  fillna= True)
    todayMA = maObj.sma_indicator().to_list()

    # plt.plot(todayMA)
    # plt.show()

    if todayMA[window] > todayMA[window-1]: 
        Rising = True
    else:
        Rising = False

    for i in range(window+1, len(todayMA)):

        if todayMA[i] > todayMA[i-1] and Rising == False:
            Rising = True
            sup = min(data['LowPrice'][i-window:i])
            levels.append(sup)
            indexes = [index for index, item in enumerate(data['LowPrice'][i-window:i]) if item == sup]
            lines.append(strDate_to_lineDates(data['Time'][i-window+max(indexes)], sup, data['Time']))

        elif todayMA[i] < todayMA[i-1] and Rising == True:
            Rising = False
            res = max(data['HighPrice'][i-window:i])
            levels.append(res)
            indexes = [index for index, item in enumerate(data['HighPrice'][i-window:i]) if item == res]
            lines.append(strDate_to_lineDates(data['Time'][i-window+max(indexes)], res, data['Time']))

    return [levels, lines, title]

window = 10

data = mixMethod()

# sort
levels = data[0]
lines = data[1]
title = data[2]

levels.sort()
finalLevels = [[levels[0]]]

for i in range(1,len(levels)):
    for j in range(len(finalLevels)):
        if levels[i] < sum(finalLevels[j])/len(finalLevels[j])*1.05:
            finalLevels[j].append(levels[i])
            break
    else:
        finalLevels.append([levels[i]])

finalLevelsAvg = []
widths = []
for i in range(len(finalLevels)):
    finalLevelsAvg.append(sum(finalLevels[i])/len(finalLevels[i]))
    # interval = (max(finalLevels[i])-min(finalLevels[i]))/min(finalLevels[i])*100
    # widths.append(interval*0.1+0.5)
    widths.append(len(finalLevels[i])*0.5)

# plot
custom_rc = {'font.size': 10, 'lines.linewidth': 0.5}
s =mpf.make_mpf_style(base_mpf_style='charles', rc=custom_rc)
fig, axlist = mpf.plot(dataPd, type='candle', volume=True, tight_layout= True, style=s, returnfig=True, \
    # alines=lines,\
    hlines=dict(hlines=finalLevelsAvg, colors= ['black' for i in range(len(finalLevelsAvg))]\
    # ,linewidths= widths\
    ),
    mav= (window),\
    title= title
    ) 
    # hlines=dict(hlines=finalLevelsAvg, colors= ['red' for i in range(len(finalLevelsAvg))])
ax = axlist[0]
ax.set_yscale('log')
plt.show()
#  hlines=dict(hlines=levels), , alines=lines, , mav= (window) , alines=dict(alines=seq_of_points, colors=seq_of_colors, linestyle='-', linewidths=1)
winsound.Beep(500, 200)

