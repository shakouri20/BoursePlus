from Application.Services.OfflineLab.OfflineLab import offlineLab
import datetime
from Application.Utility.DateConverter import *
from Domain.Enums.TableType import tableType
from Infrastructure.Repository.OfflineDataRepository import offlineData_repo
from Infrastructure.Repository.OnlineDataRepository import onlineData_repo
from Infrastructure.Repository.TickerRepository import ticker_repo
import matplotlib.pyplot as plt

fromDate = '1400-01-01'
toDate = '1400-11-19'

writeID = 700

days = [datetime.datetime.strptime(jalali_to_gregorian(fromDate), "%Y-%m-%d").date(), 
        datetime.datetime.strptime(jalali_to_gregorian(toDate), "%Y-%m-%d").date()]

IDList = [7745894403636165, 51617145873056483, 48753732042176709, 35366681030756042]

data = {}
for i in range(len(IDList)):
    print('', round((i+1)/len(IDList)*100, 2), end= '\r')
    IR = ticker_repo().read_by_ID(IDList[i])['IR1']
    tickerData = offlineLab().get_prices_data(IR, days, '1')
    data[IDList[i]] = tickerData

print('\nDone.')

dates: list[datetime.date] = []
for ID in data:
    for i in range(len(data[ID]['t'])):
        today = data[ID]['t'][i][0].date()
        if today not in dates:
            dates.append(today)

dates.sort()

yesterdayIndex = 1000

for today in dates:

    print('', gregorian_to_jalali(today.strftime("%Y-%m-%d")), end= '\r')

    time = []
    index = []
    dataList = []

    todayActiveTickers = {}
    for ID in data:
        tickerTimes: list[list[datetime.datetime]] = data[ID]['t']
        for j in range(len(tickerTimes)):
            if tickerTimes[j][0].date() == today:
                prices = offlineLab.get_daily_prices(ID, tickerTimes[j][0].date())
                if prices != None:
                    yesterdayPrice = prices['YesterdayPrice']
                    todayPrice = prices['TodayPrice']
                    todayActiveTickers[ID] = {'YesterdayPrice': yesterdayPrice, 'TodayPrice': todayPrice, 'TickerDateIndex': j, 'LastTimeIndex': 1}

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

        time.append(dt)
        index.append(yesterdayIndex * (1+lastPricesSum/activeTickerNum/100))

    activeTickerNum = 0
    todayPricesSum = 0
    for ID in todayActiveTickers:
        yesterdayPrice = todayActiveTickers[ID]['YesterdayPrice']
        todayPrice = todayActiveTickers[ID]['TodayPrice']
        prc = (todayPrice-yesterdayPrice)/yesterdayPrice*100
        todayPricesSum += prc
        activeTickerNum += 1

    todayIndex = yesterdayIndex * (1+todayPricesSum/activeTickerNum/100)

    for i in range(len(time)):
        dataList.append((writeID,time[i],todayIndex,index[i],0,0,0,0,yesterdayIndex,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0))

    yesterdayIndex = todayIndex

    while True:
        try:
            onlineData_repo().write_onlineData(dataList)
            break
        except:
            print('SQL Error.')
            pass


x = 1