import datetime
from math import ceil
from re import T
from matplotlib import pyplot as plt
from numpy import nan
from Application.Services.OfflineLab.OfflineLab import offlineLab
from Application.Utility.AdvancedPlot import advancedPlot
from Application.Utility.DateConverter import gregorian_to_jalali, jalali_to_gregorian
from Application.Utility.Indicators.IndicatorService import calculateEma, calculateMacd, calculateSma
from Application.Utility.IntegerIndexDateTimeFormatter import IntegerIndexDateTimeFormatter
from Domain.Enums.TableType import tableType
from Domain.Models.TickerOfflineData import tickersGroupData
from Infrastructure.Repository.OfflineDataRepository import offlineData_repo
from Infrastructure.Repository.OnlineDataRepository import onlineData_repo
from Infrastructure.Repository.TickerRepository import ticker_repo
from scipy.stats import pearsonr
import matplotlib.dates as mdates
import pandas as pd
import numpy as np

fromDate = '1400-11-12'
toDate = '1400-11-20'
name = 'پالایش'
plotTicker = 0
plotIndex = 1
plotDaysTogether = 0
IndexID = 1234

# Index
if plotIndex:
    jalalianDays = onlineData_repo().read_days(startDate= fromDate, endDate= toDate, ID= IndexID)
    indexDays = [datetime.datetime.strptime(jalali_to_gregorian(day), "%Y-%m-%d").date() for day in jalalianDays]

# ticker
ID = ticker_repo().read_by_name(name)['ID']
if plotTicker:
    tickerDays = [datetime.datetime.strptime(jalali_to_gregorian(fromDate), "%Y-%m-%d").date(), 
                    datetime.datetime.strptime(jalali_to_gregorian(toDate), "%Y-%m-%d").date()]
    webPricesData = offlineLab().get_prices_data(ticker_repo().read_by_ID(ID)['IR1'], tickerDays, '1')
    offData = offlineData_repo().read_OfflineData_in_time_range(
                'Time', 'MinAllowedPrice', 'MaxAllowedPrice', table= tableType.OfflineData.value, IDList= [ID],
                    fromDate= jalali_to_gregorian(fromDate), toDate= jalali_to_gregorian(toDate))

if plotTicker and not plotIndex:
    finalDays = offData[ID]['Time']
    plotName = name
elif not plotTicker and plotIndex:
    finalDays = indexDays
    plotName = str(IndexID)
elif plotTicker and plotIndex:
    finalDays = []
    for day in offData[ID]['Time']:
        if day in indexDays:
            finalDays.append(day)
    plotName = str(IndexID) + ' ' + name
else:
    raise Exception

if not plotDaysTogether:
    
    rowNum = max(ceil(len(finalDays)/3), 2)
    ap = advancedPlot(rowNum, 3, plotName, False)

    for i in range(len(finalDays)):

        rowIndex = i%rowNum
        columnIndex = int(i/rowNum)

        if plotIndex:
            indexData = tickersGroupData(IndexID, finalDays[i])
            ap.ax[rowIndex][columnIndex].plot(indexData.time, indexData.index)
            ap.ax[rowIndex][columnIndex].plot(indexData.time, indexData.indexMa)
            times = indexData.time

        if plotTicker:
            for j in range(len(webPricesData['t'])):
                if  finalDays[i] == webPricesData['t'][j][0].date():
                    indice = offData[ID]['Time'].index(finalDays[i])
                    if offData[ID]['MinAllowedPrice'][indice] != None:
                        yesterdayPrice = (offData[ID]['MinAllowedPrice'][indice]+offData[ID]['MaxAllowedPrice'][indice])/2
                    else:
                        allowedPrice = offlineLab.get_daily_allowed_price(ID, finalDays[i])
                        offlineData_repo().write_price_range(ID, finalDays[i].strftime("%Y-%m-%d"), allowedPrice['Min'], allowedPrice['Max'])
                        yesterdayPrice = (allowedPrice['Min']+allowedPrice['Max'])/2
                    tickerTime = webPricesData['t'][j]
                    tickerPrice = [(webPricesData['c'][j][k]-yesterdayPrice)/yesterdayPrice*100 for k in range(len(webPricesData['c'][j]))]
                    ap.ax[rowIndex][columnIndex].plot(tickerTime, tickerPrice)
                    times = tickerTime

                    tickerPriceMa = calculateEma(tickerPrice, 15, True)
                    # tickerPriceMaMa = calculateEma(tickerPriceMa, 20, True)
                    # maDif = [(tickerPriceMa[i]-tickerPriceMaMa[i])*10 for i in range(len(tickerPriceMa))]
                    ap.ax[rowIndex][columnIndex].plot(tickerTime, tickerPriceMa)
                    myFmt = mdates.DateFormatter("%d %H-%M")
                    ap.ax[rowIndex][columnIndex].xaxis.set_major_formatter(myFmt)
        
        if plotIndex:
            constantLine = indexData.yesterdayPrice
        else:
            constantLine = 0

        ap.ax[rowIndex][columnIndex].plot(times, [constantLine for _ in range(len(times))], label= gregorian_to_jalali(finalDays[i].strftime("%Y-%m-%d")))
        ap.ax[rowIndex][columnIndex].legend(loc="lower right", prop={'size': 8})
        # ap.ax[rowIndex][columnIndex].axes.xaxis.set_ticks([])    
else:

    ap = advancedPlot(3, 1, plotName)

    if plotIndex:
        indexData = onlineData_repo().read_onlineData_by_time_range(IndexID, fromDate, toDate)
        indexTimes = indexData[IndexID]['Time']
        index = indexData[IndexID]['LastPrice']
        slope = [0 for _ in range(len(indexTimes))]
        slopeLen = 2
        for i in range(3, len(indexTimes)):
            slope[i] = (index[i] - index[max(i-slopeLen, 0)])/index[i]*100 # 5
            slope[i] /= ((indexTimes[i]-indexTimes[max(i-slopeLen, 0)]).total_seconds()/60)
        indexMa = calculateSma(index, 20, True)
        dif = [index[i]-indexMa[i] for i in range(len(index))]
        macd = calculateMacd(index, fillna= True)

        xdates = np.arange(len(indexTimes))
        timesIndex = pd.DatetimeIndex(indexTimes)
        fmtstring = '%Y-%m-%d %H:%M'
        dates = mdates.date2num(timesIndex.to_pydatetime())
        formatter = IntegerIndexDateTimeFormatter(dates, fmtstring)
        ap.ax[0].xaxis.set_major_formatter(formatter)
        ap.ax[1].xaxis.set_major_formatter(formatter)
        ap.ax[2].xaxis.set_major_formatter(formatter)
        ap.ax[0].plot(xdates, index, label= str(IndexID))
        ap.ax[0].legend()
        ap.ax[1].plot(xdates, macd)
        ap.ax[1].plot(xdates, [0 for _ in range(len(indexTimes))])
        ap.ax[2].plot(xdates, slope)
        ap.ax[2].plot(xdates, [0 for _ in range(len(indexTimes))])
        ap.ax[2].plot(xdates, [0.15 for _ in range(len(indexTimes))])
        ap.ax[2].plot(xdates, [-0.15 for _ in range(len(indexTimes))])
           
    if plotTicker:
        prices = []
        if plotIndex:
            tickerTimes = indexTimes
            for i in range(len(indexTimes)):
                for j in range(len(webPricesData['t'])):
                    if webPricesData['t'][j][0].date() == indexTimes[i].date():
                        for k in range(len(webPricesData['t'][j])):
                            if indexTimes[i] < webPricesData['t'][j][k]:
                                prices.append(webPricesData['c'][j][k])
                                break
                        else:
                            prices.append(prices[-1])
                        break
                else:
                    prices.append(prices[-1])
                    
            if len(prices) != len(indexTimes):
                print(len(prices), len(indexTimes))
                raise Exception

            indexAverage = (max(index)+min(index))/2
            pricesAverage = (max(prices)+min(prices))/2
            prices = [indexAverage/pricesAverage*price for price in prices]
        else:
            tickerTimes = []
            for i in range(len(webPricesData['t'])):
                tickerTimes = tickerTimes + webPricesData['t'][i]
                prices = prices + webPricesData['c'][i]


        xdates = np.arange(len(tickerTimes))
        timesIndex = pd.DatetimeIndex(tickerTimes)
        fmtstring = '%Y-%m-%d %H:%M'
        dates = mdates.date2num(timesIndex.to_pydatetime())
        formatter = IntegerIndexDateTimeFormatter(dates, fmtstring)
        ap.ax[0].plot(xdates, prices, label= name[::-1])
        ap.ax[0].legend()
        ap.ax[0].xaxis.set_major_formatter(formatter)
          
ap.run()
