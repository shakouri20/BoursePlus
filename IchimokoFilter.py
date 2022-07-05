from Application.Utility.Indicators.IndicatorService import calculateIchimoko
from Domain.Enums.QueryOutPutType import queryOutPutType
from Domain.Enums.TableType import tableType
from Infrastructure.Repository.OfflineDataRepository import offlineData_repo
from Infrastructure.Repository.TickerRepository import ticker_repo

tickersData = ticker_repo().read_list_of_tickers(tickerTypes= [1], marketTypes = list(range(1, 9)), outPutType= queryOutPutType.DictDict)
IDs = list(tickersData.keys())[:]

data = offlineData_repo().read_last_N_offlineData('all', Num=100, IDList=IDs, table= tableType.OfflineData.value)

file = open('IchimokoFilter.txt', 'w', encoding = 'utf-8')
FilteredTickers = ''

for ID in data:

    ich = calculateIchimoko(data[ID]['HighPrice'], data[ID]['LowPrice'], 9, 26, 52, True, False)

    if len(ich[0]) > 26:

        tenkansen = ich[0][-1]
        kijunsen = ich[1][-1]
        spanA = ich[2][-1]
        spanB = ich[3][-1]
        spanAshifted = ich[2][-26]
        spanBshifted = ich[3][-26]

        lastPrice = data[ID]['ClosePrice'][-1]
        yesterdayMinPrice = data[ID]['LowPrice'][-2]
        yesterdayMaxPrice = data[ID]['HighPrice'][-2]
        yesterdayClosePrice = data[ID]['ClosePrice'][-2]

        #  and lastPrice > kijunsen and lastPrice > spanA and lastPrice > spanB and lastPrice > spanAshifted and lastPrice > spanBshifted:
        # if lastPrice > kijunsen and yesterdayClosePrice < kijunsen:
        # if lastPrice > tenkansen and yesterdayMinPrice < tenkansen and lastPrice > kijunsen and yesterdayMinPrice < kijunsen:
        if spanA < spanB and lastPrice > spanA and yesterdayClosePrice < spanA:
        # if spanA > spanB and lastPrice > spanB and yesterdayClosePrice < spanB:

            FilteredTickers += tickersData[ID]['FarsiTicker'] + '\n'
    
file.write(FilteredTickers)
file.close()


