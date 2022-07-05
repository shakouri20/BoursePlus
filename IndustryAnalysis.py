from math import log10, nan
import datetime
import pandas as pd
from Application.Services.ReadData.ReadOffline.RatioService import tickerCompare
from Application.Utility.DateConverter import *
from Application.Utility.AdvancedPlot import advancedPlot
import mplfinance as mpf
from Application.Utility.Indicators.IndicatorService import calculateIchimoko, calculateSma
from Domain.Enums.TableType import tableType
from Infrastructure.DbContext.DbSession import database_session
from Infrastructure.Repository.OfflineDataRepository import offlineData_repo
from Infrastructure.Repository.TickerRepository import ticker_repo

fromDate = '1400-09-01'
toDate = '1402-01-01'

ichimokoAnalysis = 1

ticker1 = 67130298613737946
ticker2 = 32097828799138957
ticker2 = 'شاخص کل (هم وزن)6'

ticker1 = '60-حمل و نقل6'
ticker1 = '53-سيمان6'
ticker2 = '01-زراعت6'
ticker2 = '57-بانکها6'
ticker1 = '34-خودرو6'
ticker2 = '23-فراورده نفتي6'


ticker1 = '34-خودرو6'
ticker2 = '23-فراورده نفتي6'

industriesData = tickerCompare(ticker1, ticker2, fromDate, toDate)
industryTypeID1 = ticker_repo().read_by_name(ticker1)['IndustryTypeID']
industryTypeID2 = ticker_repo().read_by_name(ticker2)['IndustryTypeID']
tickerIDs1 = ticker_repo().read_list_of_tickers(tickerTypes=[1], industryTypes=[industryTypeID1])['ID']
tickerIDs2 = ticker_repo().read_list_of_tickers(tickerTypes=[1], industryTypes=[industryTypeID2])['ID']

industryTickersNumber1 = []
industryTickersValue1 = []
industryTickersRealMoney1 = []
industryTickersRealPower1 = []
industryTickersPercapitaBuy1 = []
industryTickersPercapitaSell1 = []

industryTickersNumber2 = []
industryTickersValue2 = []
industryTickersRealMoney2 = []
industryTickersRealPower2 = []
industryTickersPercapitaBuy2 = []
industryTickersPercapitaSell2 = []

db = database_session()
db.connect()

for thisDate in industriesData.datesG:

    cmd = '''
    select realBuyValue, realBuyNumber, realSellValue, realSellNumber, RealPower, CorporateBuyNumber, CorporateSellNumber, Value from OfflineData
    inner join tickers on tickers.ID = OfflineData.ID
    where Time = '{}' and tickers.tickerTypeID = 1 and tickers.industryTypeID = {}
    '''.format(thisDate, industryTypeID1)
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
        
        if row['realBuyValue'] != 0 and row['realSellValue'] != 0:
            number += 1
            realPower += log10(row['RealPower'])
            percapitaBuy += log10(row['realBuyValue']/row['realBuyNumber']/10**7) if row['realBuyValue'] != 0 else 0
            percapitaSell += log10(row['realSellValue']/row['realSellNumber']/10**7) if row['realSellValue'] != 0 else 0

    industryTickersNumber1.append(number)
    industryTickersValue1.append(value)
    industryTickersRealMoney1.append(realMoney)
    industryTickersRealPower1.append(realPower/number)
    industryTickersPercapitaBuy1.append(10 ** (percapitaBuy/number))
    industryTickersPercapitaSell1.append(10 ** (percapitaSell/number))

    cmd = '''
    select realBuyValue, realBuyNumber, realSellValue, realSellNumber, RealPower, CorporateBuyNumber, CorporateSellNumber, Value from OfflineData
    inner join tickers on tickers.ID = OfflineData.ID
    where Time = '{}' and tickers.tickerTypeID = 1 and tickers.industryTypeID = {}
    '''.format(thisDate, industryTypeID2)
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
        
        if row['realBuyValue'] != 0 and row['realSellValue'] != 0:
            number += 1
            realPower += log10(row['RealPower'])
            percapitaBuy += log10(row['realBuyValue']/row['realBuyNumber']/10**7) if row['realBuyValue'] != 0 else 0
            percapitaSell += log10(row['realSellValue']/row['realSellNumber']/10**7) if row['realSellValue'] != 0 else 0

    industryTickersNumber2.append(number)
    industryTickersValue2.append(value)
    industryTickersRealMoney2.append(realMoney)
    industryTickersRealPower2.append(realPower/number)
    industryTickersPercapitaBuy2.append(10 ** (percapitaBuy/number))
    industryTickersPercapitaSell2.append(10 ** (percapitaSell/number))

industryTickersValueMa1 = calculateSma(industryTickersValue1, 10, False)
industryTickersRealMoneyMa1 = calculateSma(industryTickersRealMoney1, 5, False)
industryTickersRealPowerMa1 = calculateSma(industryTickersRealPower1, 5, False)

industryTickersValueMa2 = calculateSma(industryTickersValue2, 10, False)
industryTickersRealMoneyMa2 = calculateSma(industryTickersRealMoney2, 5, False)
industryTickersRealPowerMa2 = calculateSma(industryTickersRealPower2, 5, False)

realPowerDif = [industryTickersRealPower1[i]-industryTickersRealPower2[i] for i in range(len(industriesData.datesG))]
realPowerDifMa = calculateSma(realPowerDif, 5, False)
valueRatio = [industryTickersValueMa1[i]/industryTickersValueMa2[i] for i in range(len(industriesData.datesG))]

# ichimoko analysis
if ichimokoAnalysis:

    # index1
    data = offlineData_repo().read_OfflineData_in_time_range('Time', 'ClosePrice', 'HighPrice', 'LowPrice', table= tableType.OfflineData.value, IDList= tickerIDs1, fromDate= jalali_to_gregorian(fromDate), toDate= jalali_to_gregorian(toDate))

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

    industryTickersTenkansen1 = []
    industryTickersKijunsen1 = []
    industryTickersSpanA1 = []
    industryTickersSpanB1 = []

    for date in industriesData.datesG:

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

        industryTickersTenkansen1.append(ten/tenNum if tenNum != 0 else nan)
        industryTickersKijunsen1.append(kij/kijNum if kijNum != 0 else nan)
        industryTickersSpanA1.append(sa/saNum if saNum != 0 else nan)
        industryTickersSpanB1.append(sb/sbNum if sbNum != 0 else nan)

    industryTickersTenkansenMa1 = calculateSma(industryTickersTenkansen1, 9, False)
    industryTickersKijunsenMa1 = calculateSma(industryTickersKijunsen1, 9, False)

    # index2
    data = offlineData_repo().read_OfflineData_in_time_range('Time', 'ClosePrice', 'HighPrice', 'LowPrice', table= tableType.OfflineData.value, IDList= tickerIDs2, fromDate= jalali_to_gregorian(fromDate), toDate= jalali_to_gregorian(toDate))

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

    industryTickersTenkansen2 = []
    industryTickersKijunsen2 = []
    industryTickersSpanA2 = []
    industryTickersSpanB2 = []

    for date in industriesData.datesG:

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

        industryTickersTenkansen2.append(ten/tenNum if tenNum != 0 else nan)
        industryTickersKijunsen2.append(kij/kijNum if kijNum != 0 else nan)
        industryTickersSpanA2.append(sa/saNum if saNum != 0 else nan)
        industryTickersSpanB2.append(sb/sbNum if sbNum != 0 else nan)

    industryTickersTenkansenMa2 = calculateSma(industryTickersTenkansen2, 9, False)
    industryTickersKijunsenMa2 = calculateSma(industryTickersKijunsen2, 9, False)

    tenkansenDif = [industryTickersTenkansen1[i]-industryTickersTenkansen2[i] for i in range(len(industriesData.datesJ))]
    kijunsenDif = [industryTickersKijunsen1[i]-industryTickersKijunsen2[i] for i in range(len(industriesData.datesJ))]


# plot
ap = advancedPlot(10 if ichimokoAnalysis else 7, 2, ticker2+'    '+ticker1)

#index
custom_rc = {'font.size': 8, 'figure.titlesize': 'x-large', 'figure.titleweight': 'normal'}
s =mpf.make_mpf_style(base_mpf_style='charles', rc=custom_rc) #

prices = {'Date': [datetime.datetime.strptime(time, "%Y-%m-%d") for time in industriesData.datesG], 'High': industriesData.tickerHighPrice1, 'Low': industriesData.tickerLowPrice1, 'Open': industriesData.tickerOpenPrice1, 'Close': industriesData.tickerClosePrice1}
dataPd = pd.DataFrame(prices)
dataPd.index = pd.DatetimeIndex(dataPd['Date'])
mpf.plot(dataPd, ax= ap.ax[0][0], axisoff = True, type= 'candle', tight_layout= True, returnfig= False, style=s, ylabel= '')
ap.ax[0][0].yaxis.tick_left()
ap.ax[0][0].yaxis.set_label_position("left")
ap.ax[0][0].set_yscale('log')

prices = {'Date': [datetime.datetime.strptime(time, "%Y-%m-%d") for time in industriesData.datesG], 'High': industriesData.tickerHighPrice2, 'Low': industriesData.tickerLowPrice2, 'Open': industriesData.tickerOpenPrice2, 'Close': industriesData.tickerClosePrice2}
dataPd = pd.DataFrame(prices)
dataPd.index = pd.DatetimeIndex(dataPd['Date'])
mpf.plot(dataPd, ax= ap.ax[0][1], axisoff = True, type= 'candle', tight_layout= True, returnfig= False, style=s, ylabel= '')
ap.ax[0][1].yaxis.tick_left()
ap.ax[0][1].yaxis.set_label_position("left")
ap.ax[0][1].set_yscale('log')

ap.ax[1][0].plot(industriesData.datesJ, industryTickersValue1, color= 'black')
ap.ax[1][0].plot(industriesData.datesJ, industryTickersValueMa1, color= 'red', linewidth= 0.7)
ap.ax[1][0].set_ylabel('Value')

ap.ax[2][0].plot(industriesData.datesJ, industryTickersRealMoney1, color= 'black')
ap.ax[2][0].plot(industriesData.datesJ, industryTickersRealMoneyMa1, color= 'red', linewidth= 0.7)
ap.ax[2][0].plot(industriesData.datesJ, [0 for _ in range(len(industriesData.datesJ))], color= 'green', linewidth= 0.9)
ap.ax[2][0].set_ylabel('RealMoney')

clrs = ['red' if (x < 0) else 'green' for x in industryTickersRealPower1]
ap.ax[3][0].bar(industriesData.datesJ, industryTickersRealPower1, color= clrs)
ap.ax[3][0].plot(industriesData.datesJ, industryTickersRealPowerMa1, color= 'blue', linewidth= 0.7)
ap.ax[3][0].plot(industriesData.datesJ, [0 for _ in range(len(industriesData.datesJ))], color= 'black')
ap.ax[3][0].plot(industriesData.datesJ, [log10(1.3) for _ in range(len(industriesData.datesJ))], color= 'green')
ap.ax[3][0].plot(industriesData.datesJ, [-log10(1.3) for _ in range(len(industriesData.datesJ))], color= 'green')
ap.ax[3][0].set_ylim([-log10(1.7), log10(1.7)])
ap.ax[3][0].set_ylabel('RealPower')

ap.ax[4][0].plot(industriesData.datesJ, industryTickersPercapitaBuy1, color= 'green')
ap.ax[4][0].plot(industriesData.datesJ, industryTickersPercapitaSell1, color= 'red')
ap.ax[4][0].set_ylabel('Percapita')

ap.ax[1][1].plot(industriesData.datesJ, industryTickersValue2, color= 'black')
ap.ax[1][1].plot(industriesData.datesJ, industryTickersValueMa2, color= 'red', linewidth= 0.7)
ap.ax[1][1].set_ylabel('Value')

ap.ax[2][1].plot(industriesData.datesJ, industryTickersRealMoney2, color= 'black')
ap.ax[2][1].plot(industriesData.datesJ, industryTickersRealMoneyMa2, color= 'red', linewidth= 0.7)
ap.ax[2][1].plot(industriesData.datesJ, [0 for _ in range(len(industriesData.datesJ))], color= 'green', linewidth= 0.9)
ap.ax[2][1].set_ylabel('RealMoney')

clrs = ['red' if (x < 0) else 'green' for x in industryTickersRealPower2]
ap.ax[3][1].bar(industriesData.datesJ, industryTickersRealPower2, color= clrs)
ap.ax[3][1].plot(industriesData.datesJ, industryTickersRealPowerMa2, color= 'blue', linewidth= 0.7)
ap.ax[3][1].plot(industriesData.datesJ, [0 for _ in range(len(industriesData.datesJ))], color= 'black')
ap.ax[3][1].plot(industriesData.datesJ, [log10(1.3) for _ in range(len(industriesData.datesJ))], color= 'green')
ap.ax[3][1].plot(industriesData.datesJ, [-log10(1.3) for _ in range(len(industriesData.datesJ))], color= 'green')
ap.ax[3][1].set_ylim([-log10(1.7), log10(1.7)])
ap.ax[3][1].set_ylabel('RealPower')

ap.ax[4][1].plot(industriesData.datesJ, industryTickersPercapitaBuy2, color= 'green')
ap.ax[4][1].plot(industriesData.datesJ, industryTickersPercapitaSell2, color= 'red')
ap.ax[4][1].set_ylabel('Percapita')

ap.ax[5][0].plot(industriesData.datesJ, industriesData.ratio, color= 'blue')
ap.ax[5][0].plot(industriesData.datesJ, industriesData.ratioMa1, color= 'red', linewidth= 0.7)
ap.ax[5][0].plot(industriesData.datesJ, industriesData.ratioMa2, color= 'green', linewidth= 0.7)
ap.ax[5][0].set_ylabel('Ratio')
ap.ax[5][0].tick_params(labelleft= False)

ap.ax[6][0].plot(industriesData.datesJ, industriesData.ratioRsi, color= 'blue')
ap.ax[6][0].plot(industriesData.datesJ, [30 for _ in range(len(industriesData.datesJ))], color='black', linewidth= 0.6)
ap.ax[6][0].plot(industriesData.datesJ, [50 for _ in range(len(industriesData.datesJ))], color='brown', linewidth= 1.5)
ap.ax[6][0].plot(industriesData.datesJ, [70 for _ in range(len(industriesData.datesJ))], color='black', linewidth= 0.6)
clrs = ['red' if (x < 50) else 'green' for x in industriesData.ratioMacd]
ap.ax[6][0].bar(industriesData.datesJ, industriesData.ratioMacd, color= clrs)
ap.ax[6][0].set_ylabel('Indicator')
ap.ax[6][0].tick_params(labelleft= False)

# ap.ax[6][1].plot(industriesData.datesJ, industryTickersNumber1, color= 'green')
# ap.ax[6][1].plot(industriesData.datesJ, industryTickersNumber2, color= 'black')
ap.ax[6][1].plot(industriesData.datesJ, valueRatio, color= 'black')

clrs = ['red' if (x < 0) else 'green' for x in realPowerDif]
ap.ax[5][1].bar(industriesData.datesJ, realPowerDif, color= clrs)
ap.ax[5][1].plot(industriesData.datesJ, realPowerDifMa, color= 'blue', linewidth= 0.7)
ap.ax[5][1].set_ylabel('RpDif')

if ichimokoAnalysis:

    ap.ax[7][0].plot(industriesData.datesJ, industryTickersTenkansen1, color= 'blue')
    ap.ax[7][0].plot(industriesData.datesJ, industryTickersTenkansenMa1, color= 'green', linewidth= 0.7)
    ap.ax[7][0].plot(industriesData.datesJ, [0 for _ in range(len(industriesData.datesJ))], color= 'red')
    ap.ax[7][0].set_ylabel('Tenkansen')

    ap.ax[7][1].plot(industriesData.datesJ, industryTickersTenkansen2, color= 'blue')
    ap.ax[7][1].plot(industriesData.datesJ, industryTickersTenkansenMa2, color= 'green', linewidth= 0.5)
    ap.ax[7][1].plot(industriesData.datesJ, [0 for _ in range(len(industriesData.datesJ))], color= 'red')
    ap.ax[7][1].set_ylabel('Tenkansen')

    ap.ax[8][0].plot(industriesData.datesJ, industryTickersKijunsen1, color= 'brown')
    ap.ax[8][0].plot(industriesData.datesJ, industryTickersKijunsenMa1, color= 'green', linewidth= 0.8)
    ap.ax[8][0].plot(industriesData.datesJ, [0 for _ in range(len(industriesData.datesJ))], color= 'red')
    ap.ax[8][0].set_ylabel('Kijunsen')

    ap.ax[8][1].plot(industriesData.datesJ, industryTickersKijunsen2, color= 'brown')
    ap.ax[8][1].plot(industriesData.datesJ, industryTickersKijunsenMa2, color= 'green', linewidth= 0.8)
    ap.ax[8][1].plot(industriesData.datesJ, [0 for _ in range(len(industriesData.datesJ))], color= 'red')
    ap.ax[8][1].set_ylabel('Kijunsen')
    
    ap.ax[9][0].plot(industriesData.datesJ, tenkansenDif, color= 'blue')
    ap.ax[9][0].plot(industriesData.datesJ, [0 for _ in range(len(industriesData.datesJ))], color= 'red')
    ap.ax[9][0].set_ylabel('TenkansenDif')
    
    ap.ax[9][1].plot(industriesData.datesJ, kijunsenDif, color= 'brown')
    ap.ax[9][1].plot(industriesData.datesJ, [0 for _ in range(len(industriesData.datesJ))], color= 'red')
    ap.ax[9][1].set_ylabel('KijunsenDif')

ap.run()

















# #index
# custom_rc = {'font.size': 8, 'figure.titlesize': 'x-large', 'figure.titleweight': 'normal'}
# s =mpf.make_mpf_style(base_mpf_style='charles', rc=custom_rc) #

# prices = {'Date': [datetime.datetime.strptime(time, "%Y-%m-%d") for time in industriesData.datesG], 'High': industriesData.tickerHighPrice1, 'Low': industriesData.tickerLowPrice1, 'Open': industriesData.tickerOpenPrice1, 'Close': industriesData.tickerClosePrice1}
# dataPd = pd.DataFrame(prices)
# dataPd.index = pd.DatetimeIndex(dataPd['Date'])
# mpf.plot(dataPd, ax= ap.ax[0][0], axisoff = True, type= 'candle', tight_layout= True, returnfig= False, style=s, ylabel= ticker1[::-1] if type(ticker1) == str else '')
# ap.ax[0][0].yaxis.tick_left()
# ap.ax[0][0].yaxis.set_label_position("left")
# ap.ax[0][0].set_yscale('log')

# prices = {'Date': [datetime.datetime.strptime(time, "%Y-%m-%d") for time in industriesData.datesG], 'High': industriesData.tickerHighPrice2, 'Low': industriesData.tickerLowPrice2, 'Open': industriesData.tickerOpenPrice2, 'Close': industriesData.tickerClosePrice2}
# dataPd = pd.DataFrame(prices)
# dataPd.index = pd.DatetimeIndex(dataPd['Date'])
# mpf.plot(dataPd, ax= ap.ax[0][1], axisoff = True, type= 'candle', tight_layout= True, returnfig= False, style=s, ylabel= ticker2[::-1] if type(ticker2) == str else '')
# ap.ax[0][1].yaxis.tick_left()
# ap.ax[0][1].yaxis.set_label_position("left")
# ap.ax[0][1].set_yscale('log')

# ap.ax[1][0].plot(industriesData.datesJ, industriesData.ratio, color= 'blue')
# ap.ax[1][0].plot(industriesData.datesJ, industriesData.ratioMa1, color= 'red', linewidth= 0.7)
# ap.ax[1][0].plot(industriesData.datesJ, industriesData.ratioMa2, color= 'green', linewidth= 0.7)
# ap.ax[1][0].set_ylabel('Ratio')
# ap.ax[1][0].tick_params(labelleft= False)

# ap.ax[1][1].plot(industriesData.datesJ, industriesData.ratioRsi, color= 'blue')
# ap.ax[1][1].plot(industriesData.datesJ, [30 for _ in range(len(industriesData.datesJ))], color='black', linewidth= 0.6)
# ap.ax[1][1].plot(industriesData.datesJ, [50 for _ in range(len(industriesData.datesJ))], color='brown', linewidth= 1.5)
# ap.ax[1][1].plot(industriesData.datesJ, [70 for _ in range(len(industriesData.datesJ))], color='black', linewidth= 0.6)
# clrs = ['red' if (x < 50) else 'green' for x in industriesData.ratioMacd]
# ap.ax[1][1].bar(industriesData.datesJ, industriesData.ratioMacd, color= clrs)
# ap.ax[1][1].plot(industriesData.datesJ, industriesData.ratioMacdMa, color= 'c')
# ap.ax[1][1].set_ylabel('Indicator')
# ap.ax[1][1].tick_params(labelleft= False)


# ap.run()