from Application.Services.OfflineLab.OfflineLab import offlineLab
import datetime
from Application.Utility.DateConverter import *
from Domain.Enums.TableType import tableType
from Infrastructure.Repository.OfflineDataRepository import offlineData_repo
from Infrastructure.Repository.OnlineDataRepository import onlineData_repo
from Infrastructure.Repository.TickerRepository import ticker_repo
import matplotlib.pyplot as plt

fromDate = '1400-11-19'
toDate = '1402-11-01'

writeID = 12345

days = [datetime.datetime.strptime(jalali_to_gregorian(fromDate), "%Y-%m-%d").date(), 
        datetime.datetime.strptime(jalali_to_gregorian(toDate), "%Y-%m-%d").date()]

# IDList = [35366681030756042, 7745894403636165, 51617145873056483, 
#             35425587644337450, 46348559193224090, 63917421733088077, 
#             778253364357513, 28320293733348826, 25244329144808274, 
#             65883838195688438, 44891482026867833, 2400322364771558, 
#             26014913469567886, 22560050433388046, 19040514831923530, 
#             22811176775480091, 60610861509165508, 48990026850202503, 
#             48753732042176709, 28864540805361867, 20562694899904339]
IDList = ticker_repo().read_list_of_tickers(marketTypes= [1, 2, 3, 4])['ID']
# 
data = {}
for i in range(len(IDList)):
    print('', round((i+1)/len(IDList)*100, 2), end= '\r')
    IR = ticker_repo().read_by_ID(IDList[i])['IR1']
    tickerData = offlineLab([]).get_prices_data(IR, days, '1')
    data[IDList[i]] = tickerData

print('\nDone.')

dates: list[datetime.date] = []
for ID in data:
    for i in range(len(data[ID]['t'])):
        today = data[ID]['t'][i][0].date()
        if today not in dates:
            dates.append(today)

dates.sort()

for today in dates:

    print('', gregorian_to_jalali(today.strftime("%Y-%m-%d")), end= '\r')

    time = []
    lastPrice = []
    dataList = []

    todayActiveTickers = {}
    for ID in data:
        tickerTimes: list[list[datetime.datetime]] = data[ID]['t']
        for j in range(len(tickerTimes)):
            if tickerTimes[j][0].date() == today:
                priceRange = offlineLab.get_daily_allowed_price(ID, tickerTimes[j][0].date())
                if priceRange != None:
                    yesterdayPrice = int((priceRange['Min']+priceRange['Max'])/2)
                    todayActiveTickers[ID] = {'YesterdayPrice': yesterdayPrice, 'TickerDateIndex': j, 'LastTimeIndex': 1}

    dt = datetime.datetime.combine(today, datetime.datetime.min.time()) + datetime.timedelta(hours=9)

    for i in range(210):

        dt += datetime.timedelta(minutes= 1)
        
        activeTickerNum = 0
        lastPricesSum = 0

        for ID in todayActiveTickers:
            tickerDateIndex = todayActiveTickers[ID]['TickerDateIndex']
            yesterdayPrice = todayActiveTickers[ID]['YesterdayPrice']
            tickerTimes: list[datetime.datetime] = data[ID]['t'][tickerDateIndex]
            lastTimeIndex = todayActiveTickers[ID]['LastTimeIndex']
            for j in range(lastTimeIndex, len(tickerTimes)):
                if tickerTimes[j] >= dt and tickerTimes[j-1] < dt:
                    price = (data[ID]['c'][tickerDateIndex][j-1] + data[ID]['o'][tickerDateIndex][j-1] +
                                data[ID]['h'][tickerDateIndex][j-1] + data[ID]['l'][tickerDateIndex][j-1])/4
                    break
            else:
                price = (data[ID]['c'][tickerDateIndex][-1] + data[ID]['o'][tickerDateIndex][-1] +
                                data[ID]['h'][tickerDateIndex][-1] + data[ID]['l'][tickerDateIndex][-1])/4

            prc = (price-yesterdayPrice)/yesterdayPrice*100
            lastPricesSum += prc
            activeTickerNum += 1
            todayActiveTickers[ID]['LastTimeIndex'] = j

        if activeTickerNum != 0:
            time.append(dt)
            lastPrice.append(lastPricesSum/activeTickerNum*1000)


    for i in range(len(time)):
        dataList.append((writeID,time[i],0,lastPrice[i],0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0))

    while True:
        try:
            onlineData_repo().write_onlineData(dataList)
            break
        except:
            print('SQL Error.')
            pass


x = 1