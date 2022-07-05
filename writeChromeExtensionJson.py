import json
from Domain.Enums.QueryOutPutType import queryOutPutType
from Domain.Enums.TableType import tableType
from Infrastructure.Repository.OfflineDataRepository import offlineData_repo
from Infrastructure.Repository.TickerRepository import ticker_repo

def write_chrome_extension_json():
    
    tickersData = ticker_repo().read_list_of_tickers(tickerTypes= [1, 3], outPutType= queryOutPutType.DictDict)
    IDs = list(tickersData.keys())[:]

    data = offlineData_repo().read_last_N_offlineData('all', Num=30, IDList=IDs, table= tableType.OfflineData.value)
    finalData = {}

    for ID in data:

        finalData[ID] = {}
        
        volumes = [data[ID]['Value'][i]/data[ID]['TodayPrice'][i] for i in range(len(data[ID]['Value']))]
        monthlyVolume = sum(volumes)/len(volumes)
        weeklyVolume = sum(volumes[-7:])/len(volumes[-7:])
        volumes3day = volumes[-3:]
        realPower3day = data[ID]['RealPower'][-3:]

        finalData[ID]['MonthlyVolume'] = monthlyVolume
        finalData[ID]['WeeklyVolume'] = weeklyVolume
        finalData[ID]['RecentVolume'] = sum(volumes3day)
        finalData[ID]['RecentRealPower'] = sum([volumes3day[i]*realPower3day[i] for i in range(len(volumes3day))])/sum(volumes3day)
        finalData[ID]['RahavardEntityID'] = tickersData[ID]['RahavardEntityID']

    IDs = list(finalData.keys())
    for ID in IDs:
        finalData[tickersData[ID]['FarsiTicker']] = finalData[ID]
        del finalData[ID]

    with open(r"E:\Skill\JavaScript\EasyTrader Extension\offlineData.json", "w") as outfile:
        json.dump(finalData, outfile)