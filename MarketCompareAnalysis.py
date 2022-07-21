import datetime
from math import log10, nan
import pandas as pd
from Application.Services.WriteData.GetOnlineDataService import get_last_clientType_Data, get_last_marketWatch_data
from Application.Utility.DateConverter import *
from Application.Utility.Indicators.IndicatorService import calculateIchimoko, calculateMacd, calculateRsi, calculateSma
from Domain.Enums.TableType import tableType
from Domain.Enums.dateType import dateType
from Infrastructure.DbContext.DbSession import database_session
from Infrastructure.Repository.OfflineDataRepository import offlineData_repo
from Application.Utility.AdvancedPlot import advancedPlot
import mplfinance as mpf
from Infrastructure.Repository.TickerRepository import ticker_repo
import copy

fromDate = '1400-10-01'
toDate = '1402-07-01'

ichimokoAnalysis = 0

hIndexData = offlineData_repo().read_by_ID_and_time('Time', 'ClosePrice', 'OpenPrice', 'HighPrice', 'LowPrice', ID= 67130298613737946, fromDate= fromDate, toDate= toDate, outputDateType= dateType.gregorian)
hDatesG = hIndexData['Time']
hIndexClosePrice = []
hIndexOpenPrice = []
hIndexHighPrice = []
hIndexLowPrice = []

kIndexData = offlineData_repo().read_by_ID_and_time('Time', 'ClosePrice', 'OpenPrice', 'HighPrice', 'LowPrice', ID= 32097828799138957, fromDate= fromDate, toDate= toDate, outputDateType= dateType.gregorian)
kDatesG = kIndexData['Time']
kIndexClosePrice = []
kIndexOpenPrice = []
kIndexHighPrice = []
kIndexLowPrice = []

datesG = []

for date in kDatesG:
    if date in hDatesG:
        datesG.append(date)
        for i in range(len(kDatesG)):
            if kDatesG[i] == date:
                kIndexClosePrice.append(kIndexData['ClosePrice'][i] if len(kIndexClosePrice)==0 or 0.9 < kIndexData['ClosePrice'][i]/kIndexClosePrice[-1] < 1.1 else kIndexClosePrice[-1])
                kIndexOpenPrice.append(kIndexData['OpenPrice'][i] if len(kIndexOpenPrice)==0 or 0.9 < kIndexData['OpenPrice'][i]/kIndexOpenPrice[-1] < 1.1 else kIndexOpenPrice[-1])
                kIndexHighPrice.append(kIndexData['HighPrice'][i] if len(kIndexHighPrice)==0 or 0.9 < kIndexData['HighPrice'][i]/kIndexHighPrice[-1] < 1.1 else kIndexHighPrice[-1])
                kIndexLowPrice.append(kIndexData['LowPrice'][i] if len(kIndexLowPrice)==0 or 0.9 < kIndexData['LowPrice'][i]/kIndexLowPrice[-1] < 1.1 else kIndexLowPrice[-1])
        for i in range(len(hDatesG)):
            if hDatesG[i] == date:
                hIndexClosePrice.append(hIndexData['ClosePrice'][i] if len(hIndexClosePrice)==0 or 0.9 < hIndexData['ClosePrice'][i]/hIndexClosePrice[-1] < 1.1 else hIndexClosePrice[-1])
                hIndexOpenPrice.append(hIndexData['OpenPrice'][i] if len(hIndexOpenPrice)==0 or 0.9 < hIndexData['OpenPrice'][i]/hIndexOpenPrice[-1] < 1.1 else hIndexOpenPrice[-1])
                hIndexHighPrice.append(hIndexData['HighPrice'][i] if len(hIndexHighPrice)==0 or 0.9 < hIndexData['HighPrice'][i]/hIndexHighPrice[-1] < 1.1 else hIndexHighPrice[-1])
                hIndexLowPrice.append(hIndexData['LowPrice'][i] if len(hIndexLowPrice)==0 or 0.9 < hIndexData['LowPrice'][i]/hIndexLowPrice[-1] < 1.1 else hIndexLowPrice[-1])

hTotalNumber = []
hTotalValue = []
hTotalRealMoney = []
hTotalRealPower = []
hTotalPercapitaBuy = []
hTotalPercapitaSell = []

hIndexClosePrice1 = []
hIndexOpenPrice1 = []
hIndexHighPrice1 = []
hIndexLowPrice1 = []

kTotalNumber = []
kTotalValue = []
kTotalRealMoney = []
kTotalRealPower = []
kTotalPercapitaBuy = []
kTotalPercapitaSell = []

kIndexClosePrice1 = []
kIndexOpenPrice1 = []
kIndexHighPrice1 = []
kIndexLowPrice1 = []

db = database_session()
db.connect()

for thisDate in datesG:

    cmd = '''
    select OpenPrice, ClosePrice, HighPrice, LowPrice, YesterdayPrice, realBuyValue, realBuyNumber, realSellValue, realSellNumber, RealPower, CorporateBuyNumber, CorporateSellNumber, Value from OfflineData
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

    closePrice = 0
    openPrice = 0
    highPrice = 0
    lowPrice = 0

    for row in result:

        value += (row['Value'])/10**10
        realMoney += ((row['realBuyValue']-row['realSellValue']))/10**10
        
        if row['realBuyValue'] != 0 and row['realSellValue'] != 0 and -15 < (row['ClosePrice']-row['YesterdayPrice'])/row['YesterdayPrice']*100 < 15:

            number += 1
            realPower += log10(row['RealPower'])
            percapitaBuy += log10(row['realBuyValue']/row['realBuyNumber']/10**7) if row['realBuyValue'] != 0 else 0
            percapitaSell += log10(row['realSellValue']/row['realSellNumber']/10**7) if row['realSellValue'] != 0 else 0

            closePrice += (row['ClosePrice']-row['YesterdayPrice'])/row['YesterdayPrice']*100
            openPrice += (row['OpenPrice']-row['YesterdayPrice'])/row['YesterdayPrice']*100
            highPrice += (row['HighPrice']-row['YesterdayPrice'])/row['YesterdayPrice']*100
            lowPrice += (row['LowPrice']-row['YesterdayPrice'])/row['YesterdayPrice']*100

    hTotalNumber.append(number)
    hTotalValue.append(value)
    hTotalRealMoney.append(realMoney)
    hTotalRealPower.append(realPower/number)
    hTotalPercapitaBuy.append(10 ** (percapitaBuy/number))
    hTotalPercapitaSell.append(10 ** (percapitaSell/number))

    hIndexClosePrice1.append(closePrice/number)
    hIndexOpenPrice1.append(openPrice/number)
    hIndexHighPrice1.append(highPrice/number)
    hIndexLowPrice1.append(lowPrice/number)

    cmd = '''
    select OpenPrice, ClosePrice, HighPrice, LowPrice, YesterdayPrice, realBuyValue, realBuyNumber, realSellValue, realSellNumber, RealPower, Value from OfflineData
    inner join tickers on tickers.ID = OfflineData.ID
    where Time = '{}' and tickers.ID in (25244329144808274, 46348559193224090, 35425587644337450, 
            35700344742885862, 33441514568901717, 18027801615184692, 
            2400322364771558, 51971068201094874, 53449700212786324, 
            52232388263291380, 22560050433388046, 7745894403636165, 
            35366681030756042, 30703140537034664, 23441366113375722, 
            9536587154100457, 58931793851445922, 55127657985997520,
            19040514831923530, 26014913469567886, 20562694899904339, 
            51617145873056483, 32357363984168442, 67126881188552864, 
            65883838195688438, 28864540805361867, 48753732042176709,
            27922860956133067, 37204371816016200, 60610861509165508, 
            22811176775480091, 68635710163497089, 44891482026867833)
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

    closePrice = 0
    openPrice = 0
    highPrice = 0
    lowPrice = 0

    for row in result:

        value += (row['Value'])/10**10
        realMoney += ((row['realBuyValue']-row['realSellValue']))/10**10
        
        if row['realBuyValue'] != 0 and row['realSellValue'] != 0 and -15 < (row['ClosePrice']-row['YesterdayPrice'])/row['YesterdayPrice']*100 < 15:

            number += 1
            realPower += log10(row['RealPower'])
            percapitaBuy += log10(row['realBuyValue']/row['realBuyNumber']/10**7) if row['realBuyValue'] != 0 else 0
            percapitaSell += log10(row['realSellValue']/row['realSellNumber']/10**7) if row['realSellValue'] != 0 else 0

            closePrice += (row['ClosePrice']-row['YesterdayPrice'])/row['YesterdayPrice']*100
            openPrice += (row['OpenPrice']-row['YesterdayPrice'])/row['YesterdayPrice']*100
            highPrice += (row['HighPrice']-row['YesterdayPrice'])/row['YesterdayPrice']*100
            lowPrice += (row['LowPrice']-row['YesterdayPrice'])/row['YesterdayPrice']*100

    kTotalNumber.append(number)
    kTotalValue.append(value)
    kTotalRealMoney.append(realMoney)
    kTotalRealPower.append(realPower/number)
    kTotalPercapitaBuy.append(10 ** (percapitaBuy/number))
    kTotalPercapitaSell.append(10 ** (percapitaSell/number))

    kIndexClosePrice1.append(closePrice/number)
    kIndexOpenPrice1.append(openPrice/number)
    kIndexHighPrice1.append(highPrice/number)
    kIndexLowPrice1.append(lowPrice/number)


if datetime.datetime.strptime(datesG[-1], "%Y-%m-%d").date() != datetime.datetime.now().date() and datetime.datetime.strptime(jalali_to_gregorian(toDate), "%Y-%m-%d").date() >= datetime.datetime.now().date():

    hIDs = ticker_repo().read_list_of_tickers(tickerTypes= [1, 3])['ID']
    kIDs = [25244329144808274, 46348559193224090, 35425587644337450, 
            35700344742885862, 33441514568901717, 18027801615184692, 
            2400322364771558, 51971068201094874, 53449700212786324, 
            52232388263291380, 22560050433388046, 7745894403636165, 
            35366681030756042, 30703140537034664, 23441366113375722, 
            9536587154100457, 58931793851445922, 55127657985997520,
            19040514831923530, 26014913469567886, 20562694899904339, 
            51617145873056483, 32357363984168442, 67126881188552864, 
            65883838195688438, 28864540805361867, 48753732042176709,
            27922860956133067, 37204371816016200, 60610861509165508, 
            22811176775480091, 68635710163497089, 44891482026867833]
    datesG.append(datetime.datetime.strftime(datetime.datetime.now(), "%Y-%m-%d"))

    mwData = get_last_marketWatch_data()
    ctData = get_last_clientType_Data()

    number = 0
    value = 0
    realMoney = 0
    realPower = 0
    percapitaBuy = 0
    percapitaSell = 0

    todayPrice = 0
    openPrice = 0
    closePrice = 0
    highPrice = 0
    lowPrice = 0

    for ID in mwData:

        if ID in hIDs and ID in ctData:

            value += (mwData[ID]['TodayPrice']*mwData[ID]['Volume'])/10**10
            realMoney += (mwData[ID]['TodayPrice'] * (ctData[ID]['RealBuyVolume']-ctData[ID]['RealSellVolume']))/10**10
            
            if ctData[ID]['RealBuyVolume'] != 0 and ctData[ID]['RealSellVolume'] != 0:

                if 0.85 < mwData[ID]['TodayPrice']/mwData[ID]['YesterdayPrice'] < 1.15:
                    todayPrice += mwData[ID]['TodayPrice']/mwData[ID]['YesterdayPrice']
                    openPrice += mwData[ID]['FirstPrice']/mwData[ID]['YesterdayPrice']
                    closePrice += mwData[ID]['LastPrice']/mwData[ID]['YesterdayPrice']
                    highPrice += mwData[ID]['MaxPrice']/mwData[ID]['YesterdayPrice']
                    lowPrice += mwData[ID]['MinPrice']/mwData[ID]['YesterdayPrice']
                    number += 1

                realPower += log10((ctData[ID]['RealBuyVolume']/ctData[ID]['RealBuyNumber'])/(ctData[ID]['RealSellVolume']/ctData[ID]['RealSellNumber']))
                percapitaBuy += log10(mwData[ID]['TodayPrice']*ctData[ID]['RealBuyVolume']/ctData[ID]['RealBuyNumber']/10**7) if ctData[ID]['RealBuyVolume'] != 0 else 0
                percapitaSell += log10(mwData[ID]['TodayPrice']*ctData[ID]['RealSellVolume']/ctData[ID]['RealSellNumber']/10**7) if ctData[ID]['RealSellVolume'] != 0 else 0

    hIndexOpenPrice.append(hIndexClosePrice[-1])
    hIndexClosePrice.append(hIndexClosePrice[-1]*todayPrice/number)
    hIndexHighPrice.append(max(hIndexClosePrice[-1], hIndexOpenPrice[-1]))
    hIndexLowPrice.append(min(hIndexClosePrice[-1], hIndexOpenPrice[-1]))
    
    hIndexOpenPrice1.append((openPrice/number-1)*100)
    hIndexClosePrice1.append((closePrice/number-1)*100)
    hIndexHighPrice1.append((highPrice/number-1)*100)
    hIndexLowPrice1.append((lowPrice/number-1)*100)

    hTotalNumber.append(number)
    hTotalValue.append(value)
    hTotalRealMoney.append(realMoney)
    hTotalRealPower.append(realPower/number)
    hTotalPercapitaBuy.append(10 ** (percapitaBuy/number))
    hTotalPercapitaSell.append(10 ** (percapitaSell/number))

    number = 0
    value = 0
    realMoney = 0
    realPower = 0
    percapitaBuy = 0
    percapitaSell = 0

    todayPrice = 0
    openPrice = 0
    closePrice = 0
    highPrice = 0
    lowPrice = 0

    for ID in mwData:

        if ID in kIDs and ID in ctData:

            value += (mwData[ID]['TodayPrice']*mwData[ID]['Volume'])/10**10
            realMoney += (mwData[ID]['TodayPrice'] * (ctData[ID]['RealBuyVolume']-ctData[ID]['RealSellVolume']))/10**10
            
            if ctData[ID]['RealBuyVolume'] != 0 and ctData[ID]['RealSellVolume'] != 0:

                if 0.85 < mwData[ID]['TodayPrice']/mwData[ID]['YesterdayPrice'] < 1.15:
                    todayPrice += mwData[ID]['TodayPrice']/mwData[ID]['YesterdayPrice']
                    openPrice += mwData[ID]['FirstPrice']/mwData[ID]['YesterdayPrice']
                    closePrice += mwData[ID]['LastPrice']/mwData[ID]['YesterdayPrice']
                    highPrice += mwData[ID]['MaxPrice']/mwData[ID]['YesterdayPrice']
                    lowPrice += mwData[ID]['MinPrice']/mwData[ID]['YesterdayPrice']
                    number += 1

                realPower += log10((ctData[ID]['RealBuyVolume']/ctData[ID]['RealBuyNumber'])/(ctData[ID]['RealSellVolume']/ctData[ID]['RealSellNumber']))
                percapitaBuy += log10(mwData[ID]['TodayPrice']*ctData[ID]['RealBuyVolume']/ctData[ID]['RealBuyNumber']/10**7) if ctData[ID]['RealBuyVolume'] != 0 else 0
                percapitaSell += log10(mwData[ID]['TodayPrice']*ctData[ID]['RealSellVolume']/ctData[ID]['RealSellNumber']/10**7) if ctData[ID]['RealSellVolume'] != 0 else 0

    kIndexOpenPrice.append(kIndexClosePrice[-1])
    kIndexClosePrice.append(kIndexClosePrice[-1]*todayPrice/number)
    kIndexHighPrice.append(max(kIndexClosePrice[-1], kIndexOpenPrice[-1]))
    kIndexLowPrice.append(min(kIndexClosePrice[-1], kIndexOpenPrice[-1]))

    kIndexOpenPrice1.append((openPrice/number-1)*100)
    kIndexClosePrice1.append((closePrice/number-1)*100)
    kIndexHighPrice1.append((highPrice/number-1)*100)
    kIndexLowPrice1.append((lowPrice/number-1)*100)

    kTotalNumber.append(number)
    kTotalValue.append(value)
    kTotalRealMoney.append(realMoney)
    kTotalRealPower.append(realPower/number)
    kTotalPercapitaBuy.append(10 ** (percapitaBuy/number))
    kTotalPercapitaSell.append(10 ** (percapitaSell/number))

hIndexOpenPriceTemp = copy.deepcopy(hIndexOpenPrice1)
hIndexClosePriceTemp = copy.deepcopy(hIndexClosePrice1)
hIndexHighPriceTemp = copy.deepcopy(hIndexHighPrice1)
hIndexLowPriceTemp = copy.deepcopy(hIndexLowPrice1)
kIndexOpenPriceTemp = copy.deepcopy(kIndexOpenPrice1)
kIndexClosePriceTemp = copy.deepcopy(kIndexClosePrice1)
kIndexHighPriceTemp = copy.deepcopy(kIndexHighPrice1)
kIndexLowPriceTemp = copy.deepcopy(kIndexLowPrice1)

for i in range(len(datesG)):

    if i == 0:
        hIndexOpenPrice1[i] = hIndexOpenPrice[i]
        hIndexClosePrice1[i] = hIndexClosePrice[i]
        hIndexHighPrice1[i] = hIndexHighPrice[i]
        hIndexLowPrice1[i] = hIndexLowPrice[i]

        kIndexClosePrice1[i] = kIndexClosePrice[i]
        kIndexOpenPrice1[i] = kIndexOpenPrice[i]
        kIndexHighPrice1[i] = kIndexHighPrice[i]
        kIndexLowPrice1[i] = kIndexLowPrice[i]
    else:
        hIndexOpenPrice1[i] = hIndexClosePrice[i-1]*(hIndexOpenPriceTemp[i]/100+1)
        hIndexClosePrice1[i] = hIndexClosePrice[i-1]*(hIndexClosePriceTemp[i]/100+1)
        hIndexHighPrice1[i] = hIndexClosePrice[i-1]*(hIndexHighPriceTemp[i]/100+1)
        hIndexLowPrice1[i] = hIndexClosePrice[i-1]*(hIndexLowPriceTemp[i]/100+1)

        kIndexClosePrice1[i] = kIndexClosePrice[i-1]*(kIndexClosePriceTemp[i]/100+1)
        kIndexOpenPrice1[i] = kIndexClosePrice[i-1]*(kIndexOpenPriceTemp[i]/100+1)
        kIndexHighPrice1[i] = kIndexClosePrice[i-1]*(kIndexHighPriceTemp[i]/100+1)
        kIndexLowPrice1[i] = kIndexClosePrice[i-1]*(kIndexLowPriceTemp[i]/100+1)

hHighPriceDif = [4-(hIndexHighPrice1[i]-hIndexClosePrice1[i])/hIndexClosePrice1[i]*100 for i in range(len(datesG))]
hLowPriceDif = [-(hIndexClosePrice1[i]-hIndexLowPrice1[i])/hIndexLowPrice1[i]*100 for i in range(len(datesG))]
hBodyHeight = [(hIndexClosePrice1[i]-hIndexOpenPrice1[i])/hIndexOpenPrice1[i]*100 for i in range(len(datesG))]

kHighPriceDif = [4-(kIndexHighPrice1[i]-kIndexClosePrice1[i])/kIndexClosePrice1[i]*100 for i in range(len(datesG))]
kLowPriceDif = [-(kIndexClosePrice1[i]-kIndexLowPrice1[i])/kIndexLowPrice1[i]*100 for i in range(len(datesG))]
kBodyHeight = [(kIndexClosePrice1[i]-kIndexOpenPrice1[i])/kIndexOpenPrice1[i]*100 for i in range(len(datesG))]

hIndexPower =  [(hHighPriceDif[i]-hLowPriceDif[i])/2 for i in range(len(datesG))]
kIndexPower =  [(kHighPriceDif[i]-kLowPriceDif[i])/2 for i in range(len(datesG))]
hIndexPowerDif = [hIndexPower[i]-kIndexPower[i] for i in range(len(datesG))]

kTotalValueMa = calculateSma(kTotalValue, 10, False)
kTotalRealMoneyMa = calculateSma(kTotalRealMoney, 5, False)
kTotalRealPowerMa = calculateSma(kTotalRealPower, 5, False)

hTotalPriceChangePrc = [(hIndexClosePrice[i]-hIndexClosePrice[i-1])/hIndexClosePrice[i-1]*100 if i != 0 and hIndexClosePrice[i-1] != 0 else 0 for i in range(len(datesG))]
kTotalPriceChangePrc = [(kIndexClosePrice[i]-kIndexClosePrice[i-1])/kIndexClosePrice[i-1]*100 if i != 0 and kIndexClosePrice[i-1] != 0 else 0 for i in range(len(datesG))]
hPriceChangeDif = [(hTotalPriceChangePrc[i]-kTotalPriceChangePrc[i])/2*50+50 for i in range(len(datesG))]

kValueRatio = [kTotalValue[i]/hTotalValue[i]*100 for i in range(len(datesG))]
hTotalValue = [hTotalValue[i]-kTotalValue[i] for i in range(len(datesG))]
hTotalRealMoney = [hTotalRealMoney[i]-kTotalRealMoney[i] for i in range(len(datesG))]

hTotalValueMa = calculateSma(hTotalValue, 10, False)
hTotalRealMoneyMa = calculateSma(hTotalRealMoney, 5, False)
hTotalRealPowerMa = calculateSma(hTotalRealPower, 5, False)

realPowerDif = [hTotalRealPower[i]-kTotalRealPower[i] for i in range(len(datesG))]
realPowerDifMa = calculateSma(realPowerDif, 5, False)

datesJ = [gregorian_to_jalali(date) + '   ' + str((datetime.datetime.strptime(date, "%Y-%m-%d").weekday()+2)%7)+'    ' for date in datesG]

# ichimoko analysis
if ichimokoAnalysis:
    # HAMVAZN
    data = offlineData_repo().read_OfflineData_in_time_range('Time', 'ClosePrice', 'HighPrice', 'LowPrice', table= tableType.OfflineData.value, IDList= ticker_repo().read_list_of_tickers(tickerTypes= [1, 3])['ID'], fromDate= jalali_to_gregorian(fromDate), toDate= jalali_to_gregorian(toDate))

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

    hTotalTenkansen = []
    hTotalKijunsen = []
    hTotalSpanA = []
    hTotalSpanB = []

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

        hTotalTenkansen.append(ten/tenNum if tenNum != 0 else nan)
        hTotalKijunsen.append(kij/kijNum if kijNum != 0 else nan)
        hTotalSpanA.append(sa/saNum if saNum != 0 else nan)
        hTotalSpanB.append(sb/sbNum if sbNum != 0 else nan)

    hTotalTenkansenMa = calculateSma(hTotalTenkansen, 9, False)
    hTotalKijunsenMa = calculateSma(hTotalKijunsen, 9, False)

    # KOL
    IDs = [25244329144808274, 46348559193224090, 35425587644337450, 
            35700344742885862, 33441514568901717, 18027801615184692, 
            2400322364771558, 51971068201094874, 53449700212786324, 
            52232388263291380, 22560050433388046, 7745894403636165, 
            35366681030756042, 30703140537034664, 23441366113375722, 
            9536587154100457, 58931793851445922, 55127657985997520,
            19040514831923530, 26014913469567886, 20562694899904339, 
            51617145873056483, 32357363984168442, 67126881188552864, 
            65883838195688438, 28864540805361867, 48753732042176709,
            27922860956133067, 37204371816016200, 60610861509165508, 
            22811176775480091, 68635710163497089, 44891482026867833]

    data = offlineData_repo().read_OfflineData_in_time_range('Time', 'ClosePrice', 'HighPrice', 'LowPrice', table= tableType.OfflineData.value, IDList= IDs, fromDate= jalali_to_gregorian(fromDate), toDate= jalali_to_gregorian(toDate))

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

    kTotalTenkansen = []
    kTotalKijunsen = []
    kTotalSpanA = []
    kTotalSpanB = []

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

        kTotalTenkansen.append(ten/tenNum if tenNum != 0 else nan)
        kTotalKijunsen.append(kij/kijNum if kijNum != 0 else nan)
        kTotalSpanA.append(sa/saNum if saNum != 0 else nan)
        kTotalSpanB.append(sb/sbNum if sbNum != 0 else nan)

    kTotalTenkansenMa = calculateSma(kTotalTenkansen, 9, False)
    kTotalKijunsenMa = calculateSma(kTotalKijunsen, 9, False)

# ratio
hRatio = [hIndexClosePrice[i-1] / kIndexClosePrice[i-1] if kIndexClosePrice[i] == 0 else hIndexClosePrice[i] / kIndexClosePrice[i] for i in range(len(datesG))]
hRatioMa = calculateSma(hRatio, 10)
hRatioMa2 = calculateSma(hRatio, 20)
hRatioRsi = calculateRsi(hRatio)

hRatioMacd = calculateMacd(hRatio)
macdAmp = max(abs(max(hRatioMacd[33:])), abs(min(hRatioMacd[33:])))
hRatioMacd = [item/macdAmp*50+50 for item in hRatioMacd]

# plot
ap = advancedPlot(12 if ichimokoAnalysis else 10, 2)

#index
custom_rc = {'font.size': 8, 'figure.titlesize': 'x-large', 'figure.titleweight': 'normal'}
s =mpf.make_mpf_style(base_mpf_style='charles', rc=custom_rc) #

prices = {'Date': [datetime.datetime.strptime(time, "%Y-%m-%d") for time in datesG], 'High': hIndexHighPrice1, 'Low': hIndexLowPrice1, 'Open': hIndexOpenPrice1, 'Close': hIndexClosePrice1}
dataPd = pd.DataFrame(prices)
dataPd.index = pd.DatetimeIndex(dataPd['Date'])
mpf.plot(dataPd, ax= ap.ax[0][0], axisoff = True, type= 'candle', tight_layout= True, returnfig= False, style=s, ylabel= '')
ap.ax[0][0].yaxis.tick_left()
ap.ax[0][0].yaxis.set_label_position("left")
ap.ax[0][0].set_yscale('log')

prices = {'Date': [datetime.datetime.strptime(time, "%Y-%m-%d") for time in datesG], 'High': kIndexHighPrice1, 'Low': kIndexLowPrice1, 'Open': kIndexOpenPrice1, 'Close': kIndexClosePrice1}
dataPd = pd.DataFrame(prices)
dataPd.index = pd.DatetimeIndex(dataPd['Date'])
mpf.plot(dataPd, ax= ap.ax[0][1], axisoff = True, type= 'candle', tight_layout= True, returnfig= False, style=s, ylabel= '')
ap.ax[0][1].yaxis.tick_left()
ap.ax[0][1].yaxis.set_label_position("left")
ap.ax[0][1].set_yscale('log')

ap.ax[1][0].plot(datesJ, hTotalValue, color= 'green')
ap.ax[1][0].plot(datesJ, hTotalValueMa, color= 'red', linewidth= 0.7)
ap.ax[1][0].set_ylabel('Value')

# clrs = ['red' if (x < 0) else 'green' for x in hTotalRealMoney]
# ap.ax[2][0].bar(datesJ, hTotalRealMoney, color= clrs)
# ap.ax[2][0].plot(datesJ, hTotalRealMoneyMa, color= 'blue', linewidth= 0.7)
ap.ax[2][0].plot(datesJ, hTotalRealMoney, color= 'green', linewidth= 1)
ap.ax[2][0].plot(datesJ, kTotalRealMoney, color= 'black', linewidth= 1)
ap.ax[2][0].plot(datesJ, [0 for _ in range(len(datesJ))], color= 'red', linewidth= 0.9)
ap.ax[2][0].set_ylabel('RealMoney')

clrs = ['red' if (x < 0) else 'green' for x in hTotalRealPower]
ap.ax[3][0].bar(datesJ, hTotalRealPower, color= clrs)
ap.ax[3][0].plot(datesJ, hTotalRealPowerMa, color= 'blue', linewidth= 0.7)
ap.ax[3][0].plot(datesJ, [0 for _ in range(len(datesJ))], color= 'black')
ap.ax[3][0].plot(datesJ, [log10(1.3) for _ in range(len(datesJ))], color= 'green')
ap.ax[3][0].plot(datesJ, [-log10(1.3) for _ in range(len(datesJ))], color= 'green')
ap.ax[3][0].set_ylim([-log10(1.7), log10(1.7)])
ap.ax[3][0].set_ylabel('RealPower')

ap.ax[4][0].plot(datesJ, hTotalPercapitaBuy, color= 'green')
ap.ax[4][0].plot(datesJ, hTotalPercapitaSell, color= 'red')
ap.ax[4][0].set_ylabel('Percapita')

ap.ax[1][1].plot(datesJ, kTotalValue, color= 'black')
ap.ax[1][1].plot(datesJ, kTotalValueMa, color= 'red', linewidth= 0.7)
ap.ax[1][1].set_ylabel('Value')

# clrs = ['red' if (x < 0) else 'green' for x in kTotalRealMoney]
# ap.ax[2][1].bar(datesJ, kTotalRealMoney, color= clrs)
ap.ax[2][1].plot(datesJ, kTotalRealMoneyMa, color= 'black', linewidth= 1)
ap.ax[2][1].plot(datesJ, hTotalRealMoneyMa, color= 'green', linewidth= 1)
ap.ax[2][1].plot(datesJ, [0 for _ in range(len(datesJ))], color= 'red', linewidth= 0.9)
ap.ax[2][1].set_ylabel('RealMoney')

clrs = ['red' if (x < 0) else 'green' for x in kTotalRealPower]
ap.ax[3][1].bar(datesJ, kTotalRealPower, color= clrs)
ap.ax[3][1].plot(datesJ, kTotalRealPowerMa, color= 'blue', linewidth= 0.7)
ap.ax[3][1].plot(datesJ, [0 for _ in range(len(datesJ))], color= 'black')
ap.ax[3][1].plot(datesJ, [log10(1.7) for _ in range(len(datesJ))], color= 'green')
ap.ax[3][1].plot(datesJ, [-log10(1.7) for _ in range(len(datesJ))], color= 'green')
ap.ax[3][1].set_ylim([-log10(2), log10(2)])
ap.ax[3][1].set_ylabel('RealPower')

ap.ax[4][1].plot(datesJ, kTotalPercapitaBuy, color= 'green')
ap.ax[4][1].plot(datesJ, kTotalPercapitaSell, color= 'red')
ap.ax[4][1].set_ylabel('Percapita')

ap.ax[5][0].plot(datesJ, hRatio, color= 'blue')
ap.ax[5][0].plot(datesJ, hRatioMa, color= 'red', linewidth= 0.7)
ap.ax[5][0].plot(datesJ, hRatioMa2, color= 'green', linewidth= 0.7)
ap.ax[5][0].set_ylabel('Ratio')
ap.ax[5][0].tick_params(labelleft= False)

ap.ax[6][0].plot(datesJ, hRatioRsi, color= 'blue')
ap.ax[6][0].plot(datesJ, [30 for _ in range(len(datesJ))], color='black', linewidth= 0.6)
ap.ax[6][0].plot(datesJ, [50 for _ in range(len(datesJ))], color='brown', linewidth= 1.5)
ap.ax[6][0].plot(datesJ, [70 for _ in range(len(datesJ))], color='black', linewidth= 0.6)
clrs = ['red' if (x < 50) else 'green' for x in hRatioMacd]
ap.ax[6][0].bar(datesJ, hRatioMacd, color= clrs)
ap.ax[6][0].plot(datesJ, hPriceChangeDif, color= 'black', linewidth= 0.4)
ap.ax[6][0].set_ylabel('Indicator')
ap.ax[6][0].tick_params(labelleft= False)


clrs = ['red' if (x < 0) else 'green' for x in realPowerDif]
ap.ax[5][1].bar(datesJ, realPowerDif, color= clrs)
ap.ax[5][1].plot(datesJ, realPowerDifMa, color= 'blue', linewidth= 0.7)
ap.ax[5][1].set_ylabel('hRpDif')

ap.ax[6][1].plot(datesJ, kValueRatio, color='black')
ap.ax[6][1].set_ylabel('kValueRatio')


ap.ax[7][0].plot(datesJ, hHighPriceDif, color='black', linewidth= 0.7)
ap.ax[7][0].plot(datesJ, hLowPriceDif, color='black', linewidth= 0.7)
ap.ax[7][0].plot(datesJ, [2 for _ in range(len(datesJ))], color='c', linewidth= 0.7)
ap.ax[7][0].plot(datesJ, [-2 for _ in range(len(datesJ))], color='c', linewidth= 0.7)
clrs = ['red' if (x < 0) else 'green' for x in hBodyHeight]
ap.ax[7][0].bar(datesJ, hBodyHeight, color=clrs)

ap.ax[7][1].plot(datesJ, kHighPriceDif, color='black', linewidth= 0.7)
ap.ax[7][1].plot(datesJ, kLowPriceDif, color='black', linewidth= 0.7)
ap.ax[7][1].plot(datesJ, [2 for _ in range(len(datesJ))], color='c', linewidth= 0.7)
ap.ax[7][1].plot(datesJ, [-2 for _ in range(len(datesJ))], color='c', linewidth= 0.7)
clrs = ['red' if (x < 0) else 'green' for x in kBodyHeight]
ap.ax[7][1].bar(datesJ, kBodyHeight, color=clrs)

ap.ax[8][0].bar(datesJ, hIndexPower, color='blue')
ap.ax[8][0].plot(datesJ, [2.5 for _ in range(len(datesJ))], color='red')
ap.ax[8][0].set_ylabel('IndexPower')

ap.ax[8][1].bar(datesJ, kIndexPower, color='blue')
ap.ax[8][1].plot(datesJ, [2.5 for _ in range(len(datesJ))], color='red')
ap.ax[8][1].set_ylabel('IndexPower')

clrs = ['red' if (x < 0) else 'green' for x in hIndexPowerDif]
ap.ax[9][0].bar(datesJ, hIndexPowerDif, color=clrs)

if ichimokoAnalysis:

    ap.ax[10][0].plot(datesJ, hTotalTenkansen, color= 'blue')
    ap.ax[10][0].plot(datesJ, hTotalTenkansenMa, color= 'green', linewidth= 0.5)
    ap.ax[10][0].plot(datesJ, [0 for _ in range(len(datesJ))], color= 'red')
    ap.ax[10][0].set_ylabel('Tenkansen')

    ap.ax[11][0].plot(datesJ, hTotalKijunsen, color= 'brown')
    ap.ax[11][0].plot(datesJ, hTotalKijunsenMa, color= 'green', linewidth= 0.6)
    ap.ax[11][0].plot(datesJ, [0 for _ in range(len(datesJ))], color= 'red')
    ap.ax[11][0].set_ylabel('Kijunsen')

    ap.ax[10][1].plot(datesJ, kTotalTenkansen, color= 'blue')
    ap.ax[10][1].plot(datesJ, kTotalTenkansenMa, color= 'green', linewidth= 0.5)
    ap.ax[10][1].plot(datesJ, [0 for _ in range(len(datesJ))], color= 'red')
    ap.ax[10][1].set_ylabel('Tenkansen')

    ap.ax[11][1].plot(datesJ, kTotalKijunsen, color= 'brown')
    ap.ax[11][1].plot(datesJ, kTotalKijunsenMa, color= 'green', linewidth= 0.6)
    ap.ax[11][1].plot(datesJ, [0 for _ in range(len(datesJ))], color= 'red')
    ap.ax[11][1].set_ylabel('Kijunsen')

ap.run()