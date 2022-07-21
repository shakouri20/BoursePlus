import datetime
from math import log10, nan
import pandas as pd
from Application.Services.WriteData.GetOnlineDataService import get_last_clientType_Data, get_last_marketWatch_data
from Application.Utility.DateConverter import *
from Application.Utility.Indicators.IndicatorService import calculateIchimoko, calculateSma
from Domain.Enums.TableType import tableType
from Domain.Enums.dateType import dateType
from Infrastructure.DbContext.DbSession import database_session
from Infrastructure.Repository.OfflineDataRepository import offlineData_repo
from Application.Utility.AdvancedPlot import advancedPlot
import mplfinance as mpf
from Infrastructure.Repository.TickerRepository import ticker_repo
import requests, time

fromDate = '1400-11-01'
toDate = '1402-07-01'

ichimokoAnalysis = 1

# 32097828799138957 شاخص کل
# 67130298613737946 شاخص هم وزن
indexData = offlineData_repo().read_by_ID_and_time('Time', 'ClosePrice', 'OpenPrice', 'HighPrice', 'LowPrice', ID= 67130298613737946, fromDate= fromDate, toDate= toDate, outputDateType= dateType.gregorian)
indexClosePrice = indexData['ClosePrice']
indexOpenPrice = indexData['OpenPrice']
indexHighPrice = indexData['HighPrice']
indexLowPrice = indexData['LowPrice']
datesG = indexData['Time']

totalNumber = []
totalValue = []
totalRealMoney = []
totalRealPower = []
totalPercapitaBuy = []
totalPercapitaSell = []
sandoghTotalNumber = []
sandoghTotalValue = []
sandoghTotalRealMoney = []
sandoghTotalRealPower = []
sandoghTotalPercapitaBuy = []
sandoghTotalPercapitaSell = []
totalCorporateBuyNumber = []
totalCorporateSellNumber = []

db = database_session()
db.connect()

for thisDate in datesG:

    cmd = '''
    select realBuyValue, realBuyNumber, realSellValue, realSellNumber, RealPower, CorporateBuyNumber, CorporateSellNumber, Value from OfflineData
    inner join tickers on tickers.ID = OfflineData.ID
    where Time = '{}' and tickers.tickerTypeID in (1, 3)
    '''.format(thisDate)
    db.execute(cmd)
    result = db.fetchall()

    number = 0
    value = 0
    realMoney = 0
    realPower = 0
    percapitaBuy = 0
    percapitaSell = 0
    corporateBuyNumber = 0
    corporateSellNumber = 0

    for row in result:

        value += (row['Value'])/10**10
        realMoney += ((row['realBuyValue']-row['realSellValue']))/10**10
        corporateBuyNumber += row['CorporateBuyNumber']
        corporateSellNumber += row['CorporateSellNumber']
        
        if row['realBuyValue'] != 0 and row['realSellValue'] != 0:
            number += 1
            realPower += log10(row['RealPower'])
            percapitaBuy += log10(row['realBuyValue']/row['realBuyNumber']/10**7) if row['realBuyValue'] != 0 else 0
            percapitaSell += log10(row['realSellValue']/row['realSellNumber']/10**7) if row['realSellValue'] != 0 else 0

    totalNumber.append(number)
    totalValue.append(value)
    totalRealMoney.append(realMoney)
    totalRealPower.append(realPower/number)
    totalPercapitaBuy.append(10 ** (percapitaBuy/number))
    totalPercapitaSell.append(10 ** (percapitaSell/number))
    totalCorporateBuyNumber.append(corporateBuyNumber)
    totalCorporateSellNumber.append(corporateSellNumber)

    cmd = '''
    select realBuyValue, realBuyNumber, realSellValue, realSellNumber, RealPower, Value from OfflineData
    inner join tickers on tickers.ID = OfflineData.ID
    where Time = '{}' and tickers.tickerTypeID = 4
    '''.format(thisDate)
    db.execute(cmd)
    result = db.fetchall()
    
    number = 0
    value = 0
    realMoney = 0
    realPower = 0
    percapitaBuy = 0
    percapitaSell = 0

    for row in result:

        value += (row['Value'])/10**10
        realMoney += ((row['realSellValue']-row['realBuyValue']))/10**10

        if row['realBuyValue'] != 0 and row['realSellValue'] != 0:
            number += 1
            realPower += log10(1/row['RealPower'])
            percapitaBuy += log10(row['realSellValue']/row['realSellNumber']/10**7) if row['realSellValue'] != 0 else 0
            percapitaSell += log10(row['realBuyValue']/row['realBuyNumber']/10**7) if row['realBuyValue'] != 0 else 0

    sandoghTotalNumber.append(number)
    sandoghTotalValue.append(value)
    sandoghTotalRealMoney.append(realMoney)
    sandoghTotalRealPower.append(realPower/number if number != 0 else 0)
    sandoghTotalPercapitaBuy.append(10 ** (percapitaBuy/number) if number != 0 else 0)
    sandoghTotalPercapitaSell.append(10 ** (percapitaSell/number) if number != 0 else 0)


if datetime.datetime.strptime(datesG[-1], "%Y-%m-%d").date() != datetime.datetime.now().date() and datetime.datetime.strptime(jalali_to_gregorian(toDate), "%Y-%m-%d").date() >= datetime.datetime.now().date():

    sahamIDs = ticker_repo().read_list_of_tickers(tickerTypes= [1, 3])['ID']
    dsIDs = ticker_repo().read_list_of_tickers(tickerTypes= [4])['ID']
    datesG.append(datetime.datetime.strftime(datetime.datetime.now(), "%Y-%m-%d"))

    mwData = get_last_marketWatch_data()
    ctData = get_last_clientType_Data()

    number = 0
    value = 0
    realMoney = 0
    realPower = 0
    percapitaBuy = 0
    percapitaSell = 0
    corporateBuyNumber = 0
    corporateSellNumber = 0

    firstPrice = 0
    lastPrice = 0
    maxPrice = 0
    minPrice = 0
    todayPrice = 0

    for ID in mwData:

        if ID in sahamIDs and ID in ctData:

            value += (mwData[ID]['TodayPrice']*mwData[ID]['Volume'])/10**10
            realMoney += (mwData[ID]['TodayPrice'] * (ctData[ID]['RealBuyVolume']-ctData[ID]['RealSellVolume']))/10**10
            corporateBuyNumber += ctData[ID]['CorporateBuyNumber']
            corporateSellNumber += ctData[ID]['CorporateSellNumber']
            
            if ctData[ID]['RealBuyVolume'] != 0 and ctData[ID]['RealSellVolume'] != 0:

                if 0.8 < mwData[ID]['TodayPrice']/mwData[ID]['YesterdayPrice'] < 1.2:
                    todayPrice += mwData[ID]['TodayPrice']/mwData[ID]['YesterdayPrice']
                    number += 1

                realPower += log10((ctData[ID]['RealBuyVolume']/ctData[ID]['RealBuyNumber'])/(ctData[ID]['RealSellVolume']/ctData[ID]['RealSellNumber']))
                percapitaBuy += log10(mwData[ID]['TodayPrice']*ctData[ID]['RealBuyVolume']/ctData[ID]['RealBuyNumber']/10**7) if ctData[ID]['RealBuyVolume'] != 0 else 0
                percapitaSell += log10(mwData[ID]['TodayPrice']*ctData[ID]['RealSellVolume']/ctData[ID]['RealSellNumber']/10**7) if ctData[ID]['RealSellVolume'] != 0 else 0

    indexOpenPrice.append(indexClosePrice[-1])
    indexClosePrice.append(indexClosePrice[-1]*todayPrice/number)
    indexHighPrice.append(max(indexClosePrice[-1], indexOpenPrice[-1]))
    indexLowPrice.append(min(indexClosePrice[-1], indexOpenPrice[-1]))

    totalNumber.append(number)
    totalValue.append(value)
    totalRealMoney.append(realMoney)
    totalRealPower.append(realPower/number)
    totalPercapitaBuy.append(10 ** (percapitaBuy/number))
    totalPercapitaSell.append(10 ** (percapitaSell/number))
    totalCorporateBuyNumber.append(corporateBuyNumber)
    totalCorporateSellNumber.append(corporateSellNumber)

    number = 0
    value = 0
    realMoney = 0
    realPower = 0
    percapitaBuy = 0
    percapitaSell = 0

    for ID in mwData:

        if ID in dsIDs and ID in ctData:

            value += (mwData[ID]['TodayPrice']*mwData[ID]['Volume'])/10**10
            realMoney += (mwData[ID]['TodayPrice'] * (ctData[ID]['RealSellVolume']-ctData[ID]['RealBuyVolume']))/10**10

            if ctData[ID]['RealBuyVolume'] != 0 and ctData[ID]['RealSellVolume'] != 0:
                number += 1
                realPower += log10((ctData[ID]['RealSellVolume']/ctData[ID]['RealSellNumber'])/(ctData[ID]['RealBuyVolume']/ctData[ID]['RealBuyNumber']))
                percapitaBuy += log10(mwData[ID]['TodayPrice']*ctData[ID]['RealSellVolume']/ctData[ID]['RealSellNumber']/10**7) if ctData[ID]['RealSellVolume'] != 0 else 0
                percapitaSell += log10(mwData[ID]['TodayPrice']*ctData[ID]['RealBuyVolume']/ctData[ID]['RealBuyNumber']/10**7) if ctData[ID]['RealBuyVolume'] != 0 else 0

    sandoghTotalNumber.append(number)
    sandoghTotalValue.append(value)
    sandoghTotalRealMoney.append(realMoney)
    sandoghTotalRealPower.append(realPower/number if number != 0 else 0)
    sandoghTotalPercapitaBuy.append(10 ** (percapitaBuy/number) if number != 0 else 0)
    sandoghTotalPercapitaSell.append(10 ** (percapitaSell/number) if number != 0 else 0)


totalPriceChangePrc = [(indexClosePrice[i]-indexClosePrice[i-1])/indexClosePrice[i-1]*100 if i != 0 and indexClosePrice[i-1] != 0 else 0 for i in range(len(datesG))]
totalValueMa = calculateSma(totalValue, 10, False)
totalRealMoneyMa = calculateSma(totalRealMoney, 10, False)
totalRealPowerMa = calculateSma(totalRealPower, 10, False)
sandoghTotalValueMa = calculateSma(sandoghTotalValue, 10, False)
sandoghTotalRealMoneyMa = calculateSma(sandoghTotalRealMoney, 10, False)
sandoghTotalRealPowerMa = calculateSma(sandoghTotalRealPower, 10, False)

datesJ = [gregorian_to_jalali(date) + '   ' + str((datetime.datetime.strptime(date, "%Y-%m-%d").weekday()+2)%7)+'    ' for date in datesG]

score = []

for i in range(len(datesJ)):

    temp = 0
    temp += min(20, totalValue[i]/totalValueMa[i]*10)
    temp += min(20, (totalRealMoney[i]-totalRealMoneyMa[i])*(10/(1000*10**10))+10)
    temp += min(20, totalRealPower[i]*(10/log10(1.5))+10)

    temp += min(10, (sandoghTotalRealMoney[i]-sandoghTotalRealPowerMa[i])*(10/(1000*10**10))+10)
    temp += min(10, sandoghTotalRealPower[i]*(10/log10(2))+10)
    
    temp += min(10, (indexClosePrice[i]-indexOpenPrice[i])/indexOpenPrice[i]*100*5/3+5)

    score.append(temp)

    if (totalRealPower[i] > 0 and totalRealMoney[i] > 0 and sandoghTotalRealPower[i] > 0 and sandoghTotalRealMoney[i] > 0):
        print('in:', datesJ[i])
    if (totalRealPower[i] < 0 and totalRealMoney[i] < 0 and sandoghTotalRealPower[i] < 0 and sandoghTotalRealMoney[i] < 0):
        print('out:', datesJ[i])

scoreMa = calculateSma(score, 10, False)

if ichimokoAnalysis:
    # ichimoko analysis
    data = offlineData_repo().read_OfflineData_in_time_range('Time', 'ClosePrice', 'HighPrice', 'LowPrice', table= tableType.OfflineData.value, IDList= ticker_repo().read_list_of_tickers(tickerTypes= [1])['ID'], fromDate= jalali_to_gregorian(fromDate), toDate= jalali_to_gregorian(toDate))

    closePrice = {}
    tenkansen = {}
    kijunsen = {}
    spanA = {}
    spanB = {}

    for ID in data:

        ich = calculateIchimoko(data[ID]['HighPrice'], data[ID]['LowPrice'], 9, 26, 52, True, False)

        closePrice[ID] = {}
        tenkansen[ID] = {}
        kijunsen[ID] = {}
        spanA[ID] = {}
        spanB[ID] = {}

        for i in range(len(data[ID]['Time'])):

            date = data[ID]['Time'][i].strftime("%Y-%m-%d")

            closePrice[ID][date] = data[ID]['ClosePrice'][i]

            if (i >= 8):
                tenkansen[ID][date] = ich[0][i]
            if (i >= 25):
                kijunsen[ID][date] = ich[1][i]
            if (i >= 51):
                spanA[ID][date] = ich[2][i]
            if (i >= 77):
                spanB[ID][date] = ich[3][i]

    totalTenkansen = []
    totalKijunsen = []
    totalSpanA = []
    totalSpanB = []

    for date in datesG:

        ten = 0
        kij = 0
        sa = 0
        sb = 0

        tenNum = 0
        kijNum = 0
        saNum = 0
        sbNum = 0

        for ID in tenkansen:
            if date in tenkansen[ID]:
                ten += (closePrice[ID][date]-tenkansen[ID][date])/tenkansen[ID][date]*100
                tenNum += 1
        for ID in kijunsen:
            if date in kijunsen[ID]:
                kij += (closePrice[ID][date]-kijunsen[ID][date])/kijunsen[ID][date]*100
                kijNum += 1
        for ID in spanA:
            if date in spanA[ID]:
                sa += (closePrice[ID][date]-spanA[ID][date])/spanA[ID][date]*100
                saNum += 1
        for ID in spanB:
            if date in spanB[ID]:
                sb += (closePrice[ID][date]-spanB[ID][date])/spanB[ID][date]*100
                sbNum += 1

        totalTenkansen.append(ten/tenNum if tenNum != 0 else nan)
        totalKijunsen.append(kij/kijNum if kijNum != 0 else nan)
        totalSpanA.append(sa/saNum if saNum != 0 else nan)
        totalSpanB.append(sb/sbNum if sbNum != 0 else nan)

    totalTenkansenMa = calculateSma(totalTenkansen, 9, False)
    totalKijunsenMa = calculateSma(totalKijunsen, 9, False)


# plot
ap = advancedPlot(8 if ichimokoAnalysis else 6, 2)

#index
custom_rc = {'font.size': 8, 'figure.titlesize': 'x-large', 'figure.titleweight': 'normal'}
s =mpf.make_mpf_style(base_mpf_style='charles', rc=custom_rc) #
prices = {'Date': [datetime.datetime.strptime(time, "%Y-%m-%d") for time in datesG], 'High': indexHighPrice, 'Low': indexLowPrice, 'Open': indexOpenPrice, 'Close': indexClosePrice}
dataPd = pd.DataFrame(prices)
dataPd.index = pd.DatetimeIndex(dataPd['Date'])
mpf.plot(dataPd, ax= ap.ax[0][0], axisoff = True, type= 'candle', tight_layout= True, returnfig= False, style=s, ylabel= '')
ap.ax[0][0].yaxis.tick_left()
ap.ax[0][0].yaxis.set_label_position("left")
ap.ax[0][0].set_yscale('log')


clrs = ['red' if (x < 0) else 'green' for x in totalPriceChangePrc]
ap.ax[0][1].bar(datesJ, totalPriceChangePrc, color= clrs)
ap.ax[0][1].set_ylabel('Index')

ap.ax[1][0].plot(datesJ, totalValue, color= 'black')
ap.ax[1][0].plot(datesJ, totalValueMa, color= 'red', linewidth= 0.7)
ap.ax[1][0].set_ylabel('Value')

clrs = ['red' if (x < 0) else 'green' for x in totalRealMoney]
ap.ax[2][0].bar(datesJ, totalRealMoney, color= clrs)
ap.ax[2][0].plot(datesJ, totalRealMoneyMa, color= 'blue', linewidth= 0.7)
ap.ax[2][0].set_ylabel('RealMoney')

clrs = ['red' if (x < 0) else 'green' for x in totalRealPower]
ap.ax[3][0].bar(datesJ, totalRealPower, color= clrs)
ap.ax[3][0].plot(datesJ, totalRealPowerMa, color= 'blue', linewidth= 0.7)
ap.ax[3][0].plot(datesJ, [0 for _ in range(len(datesJ))], color= 'black')
ap.ax[3][0].plot(datesJ, [log10(1.3) for _ in range(len(datesJ))], color= 'green')
ap.ax[3][0].plot(datesJ, [-log10(1.3) for _ in range(len(datesJ))], color= 'green')
ap.ax[3][0].set_ylim([-log10(1.7), log10(1.7)])
ap.ax[3][0].set_ylabel('RealPower')

ap.ax[1][1].plot(datesJ, sandoghTotalValue, color= 'black')
ap.ax[1][1].plot(datesJ, sandoghTotalValueMa, color= 'red', linewidth= 0.7)
ap.ax[1][1].set_ylabel('S Value')

clrs = ['red' if (x < 0) else 'green' for x in sandoghTotalRealMoney]
ap.ax[2][1].bar(datesJ, sandoghTotalRealMoney, color= clrs)
ap.ax[2][1].plot(datesJ, sandoghTotalRealMoneyMa, color= 'blue', linewidth= 0.7)
ap.ax[2][1].set_ylabel('S RealMoney')

clrs = ['red' if (x < 0) else 'green' for x in sandoghTotalRealPower]
ap.ax[3][1].bar(datesJ, sandoghTotalRealPower, color= clrs)
ap.ax[3][1].plot(datesJ, sandoghTotalRealPowerMa, color= 'blue', linewidth= 0.7)
ap.ax[3][1].plot(datesJ, [0 for _ in range(len(datesJ))], color= 'black')
ap.ax[3][1].plot(datesJ, [log10(1.5) for _ in range(len(datesJ))], color= 'green')
ap.ax[3][1].plot(datesJ, [-log10(1.5) for _ in range(len(datesJ))], color= 'green')
ap.ax[3][1].set_ylim([-log10(3), log10(3)])
ap.ax[3][1].set_ylabel('S RealPower')

ap.ax[4][0].plot(datesJ, totalPercapitaBuy, color= 'green')
ap.ax[4][0].plot(datesJ, totalPercapitaSell, color= 'red')
ap.ax[4][0].set_ylabel('percapita')

ap.ax[4][1].plot(datesJ, sandoghTotalPercapitaBuy, color= 'green')
ap.ax[4][1].plot(datesJ, sandoghTotalPercapitaSell, color= 'red')
ap.ax[4][1].set_ylabel('S percapita')

ap.ax[5][0].plot(datesJ, score, color= 'blue')
ap.ax[5][0].plot(datesJ, scoreMa, color= 'black', linewidth= 0.7)
ap.ax[5][0].plot(datesJ, [60 for _ in range(len(datesJ))], color= 'red')
ap.ax[5][0].set_ylabel('score')

# ap.ax[5][1].plot(datesJ, totalNumber, color= 'green')
# ap.ax[5][1].plot(datesJ, sandoghTotalNumber, color= 'green')
ap.ax[5][1].plot(datesJ, totalCorporateBuyNumber, color= 'green')
ap.ax[5][1].plot(datesJ, totalCorporateSellNumber, color= 'red')
ap.ax[5][1].set_ylabel('cprt number')

if ichimokoAnalysis:

    ap.ax[6][0].plot(datesJ, totalTenkansen, color= 'blue')
    ap.ax[6][0].plot(datesJ, totalTenkansenMa, color= 'green', linewidth= 0.7)
    ap.ax[6][0].plot(datesJ, [0 for _ in range(len(datesJ))], color= 'red')
    ap.ax[6][0].set_ylabel('Tenkansen')

    ap.ax[7][0].plot(datesJ, totalKijunsen, color= 'brown')
    ap.ax[7][0].plot(datesJ, totalKijunsenMa, color= 'green', linewidth= 0.7)
    ap.ax[7][0].plot(datesJ, [0 for _ in range(len(datesJ))], color= 'red')
    ap.ax[7][0].set_ylabel('Kijunsen')

    ap.ax[6][1].plot(datesJ, totalSpanA, color= 'green', linewidth= 0.7)
    ap.ax[6][1].plot(datesJ, totalSpanB, color= 'red', linewidth= 0.7)
    ap.ax[6][1].plot(datesJ, [0 for _ in range(len(datesJ))], color= 'blue')
    ap.ax[6][1].set_ylabel('Cloud')


ap.run()

# ap.run(saveFig= True)

# url = 'https://api.telegram.org/bot5306254202:AAF0tjiJqDrLhXtO97xqg-S5Wo2a6ofAeg4/sendPhoto'
# files = {'photo': open(r'E:\TseExpertProject\BoursePlus\foo.png', 'rb')}
# data = {'chat_id': '858421734',
#         'caption': 'سلام'}
# proxies = {'https': "socks5h://127.0.0.1:1080"}

# while True:
#     try:
#         requests.post(url, data= data, proxies= proxies, files=files)
#         break
#     except:
#         time.sleep(0.5)
#         print('error')
