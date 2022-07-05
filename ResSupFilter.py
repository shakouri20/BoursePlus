from Application.Services.OfflineLab.ResistanceSupport import calc_resistance_support
from Domain.Enums.QueryOutPutType import queryOutPutType
from Domain.Enums.TableType import tableType
from Infrastructure.Repository.OfflineDataRepository import offlineData_repo
from Infrastructure.Repository.TickerRepository import ticker_repo

tickersData = ticker_repo().read_list_of_tickers(tickerTypes= [1], marketTypes = list(range(1, 9)), outPutType= queryOutPutType.DictDict)
IDs = list(tickersData.keys())[:]

data = offlineData_repo().read_last_N_offlineData('all', Num=200, IDList=IDs, table= tableType.OfflineData.value)

file = open('ResSupFilter.txt', 'w', encoding = 'utf-8')
FilteredTickers = ''

for ID in data:
    levels = calc_resistance_support(data[ID]['HighPrice'], data[ID]['LowPrice'])
    lastPrice = data[ID]['ClosePrice'][-1]

    for i in range(len(levels[:2])):
        priceDif = (lastPrice-levels[i])/levels[i]*100
        if 0 < priceDif < 5:

            if len(data[ID]['RealPower']) >= 3:
                if data[ID]['RealPower'][-1] > data[ID]['RealPower'][-2] > data[ID]['RealPower'][-3]:
                    if data[ID]['RealPower'][-1] > 1.2:

                        FilteredTickers += tickersData[ID]['FarsiTicker'] + '\t' + str(int(levels[i])) + '\t' + str(i+1) + '\n'
                        break
    
file.write(FilteredTickers)
file.close()


