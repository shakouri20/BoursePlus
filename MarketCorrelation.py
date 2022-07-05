import datetime
from math import ceil
from numpy import nan
from Application.Services.OfflineLab.OfflineLab import offlineLab
from Application.Utility.AdvancedPlot import advancedPlot
from Application.Utility.DateConverter import gregorian_to_jalali, jalali_to_gregorian
from Domain.Enums.TableType import tableType
from Domain.Models.TickerOfflineData import tickersGroupData
from Infrastructure.Repository.OfflineDataRepository import offlineData_repo
from Infrastructure.Repository.OnlineDataRepository import onlineData_repo
from Infrastructure.Repository.TickerRepository import ticker_repo
from scipy.stats import pearsonr

startDate = '1400-01-22'
endDate = '1400-12-28'
name = 'کگل'

marketID = 1234
ID = ticker_repo().read_by_name(name)['ID']

jalalianDays = onlineData_repo().read_days(startDate= startDate, endDate= endDate, ID= marketID)
days = [datetime.datetime.strptime(jalali_to_gregorian(day), "%Y-%m-%d").date() for day in jalalianDays]
webPricesData = offlineLab().get_prices_data(ticker_repo().read_by_ID(ID)['IR1'], days, '1')
offData = offlineData_repo().read_OfflineData_in_time_range(
            'Time', 'MinAllowedPrice', 'MaxAllowedPrice', table= tableType.OfflineData.value, IDList= [ID],
                fromDate= jalali_to_gregorian(startDate), toDate= jalali_to_gregorian(endDate))

coreSum = 0
coreNum = 0
for i in range(len(days)):
    data = tickersGroupData(marketID, days[i])

    if days[i] in offData[ID]['Time']:
        for j in range(len(webPricesData['t'])):
            if  days[i] == webPricesData['t'][j][0].date():
                indice = offData[ID]['Time'].index(days[i])
                if offData[ID]['MinAllowedPrice'][indice] != None:
                    yesterdayPrice = (offData[ID]['MinAllowedPrice'][indice]+offData[ID]['MaxAllowedPrice'][indice])/2
                else:
                    allowedPrice = offlineLab.get_daily_allowed_price(ID, days[i])
                    offlineData_repo().write_price_range(ID, days[i].strftime("%Y-%m-%d"), allowedPrice['Min'], allowedPrice['Max'])
                    yesterdayPrice = (allowedPrice['Min']+allowedPrice['Max'])/2
                tickerTime = webPricesData['t'][j]
                tickerPrice = [(webPricesData['c'][j][k]-yesterdayPrice)/yesterdayPrice*100 for k in range(len(webPricesData['c'][j]))]
                
                finalTime = []
                finaltickersGroupData = []
                finalTickerPrice = []
                lastIndice = 0
                for m in range(len(tickerTime)):
                    for k in range(lastIndice, len(data.time)-1):
                        if data.time[k] < tickerTime[m] < data.time[k+1]:
                            finalTime.append(data.time[k])
                            finaltickersGroupData.append(data.index[k])
                            finalTickerPrice.append(tickerPrice[m])
                            lastIndice = k

                if len(finalTickerPrice) > 2:
                    corr, _ = pearsonr(finaltickersGroupData, finalTickerPrice)
                    if -1 <= corr <= 1:
                        coreSum += corr
                        coreNum += 1
                x = 1
                # print(gregorian_to_jalali(days[i].strftime("%Y-%m-%d")), 'correlation: %.3f' % corr)
                    
print(round(coreSum/coreNum, 2))
