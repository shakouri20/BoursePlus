import datetime
from Application.Services.OfflineLab.OfflineLab import offlineLab
from Application.Utility.AdvancedPlot import advancedPlot
from Application.Utility.DateConverter import gregorian_to_jalali, jalali_to_gregorian
from Domain.Enums.TableType import tableType
from Domain.Models.TickerOfflineData import tickersGroupData
from Infrastructure.Repository.OfflineDataRepository import offlineData_repo
from Infrastructure.Repository.OnlineDataRepository import onlineData_repo
from Infrastructure.Repository.TickerRepository import ticker_repo
from scipy.stats import pearsonr


def tickerCorrelation(ID1, ID2, fromDate, toDate) -> None:

    print('', 'start', end= '\r')
    days = [datetime.datetime.strptime(jalali_to_gregorian(fromDate), "%Y-%m-%d").date(), 
            datetime.datetime.strptime(jalali_to_gregorian(toDate), "%Y-%m-%d").date()]

    pricesData1 = offlineLab().get_prices_data(ticker_repo().read_by_ID(ID1)['IR1'], days, '1')
    print('', 'gotData1', end= '\r')
    pricesData2 = offlineLab().get_prices_data(ticker_repo().read_by_ID(ID2)['IR1'], days, '1')
    print('', 'gotData2', end= '\r')

    offData = offlineData_repo().read_OfflineData_in_time_range(
                'Time', 'MinAllowedPrice', 'MaxAllowedPrice', table= tableType.OfflineData.value, IDList= [ID1, ID2],
                    fromDate= jalali_to_gregorian(fromDate), toDate= jalali_to_gregorian(toDate))

    coreSum = 0
    coreNum = 0
    
    for i in range(len(pricesData1['t'])):
        today: datetime.date = pricesData1['t'][i][0].date()
        for j in range(len(pricesData2['t'])):
            if  today == pricesData2['t'][j][0].date():
                if today in offData[ID1]['Time'] and today in offData[ID2]['Time']:
                    indice1 = offData[ID1]['Time'].index(today)
                    indice2 = offData[ID2]['Time'].index(today)
                    yesterdayPrice1 = get_yestedayPrice(offData, ID1, indice1, today)
                    yesterdayPrice2 = get_yestedayPrice(offData, ID2, indice2, today)
                    time1 = pricesData1['t'][i]
                    time2 = pricesData2['t'][j]
                    price1 = [(pricesData1['c'][i][k]-yesterdayPrice1)/yesterdayPrice1*100 for k in range(len(pricesData1['c'][i]))]
                    price2 = [(pricesData2['c'][j][k]-yesterdayPrice2)/yesterdayPrice2*100 for k in range(len(pricesData2['c'][j]))]
                    
                    finalTime = []
                    finalPrice1 = []
                    finalPrice2 = []
                    lastIndice = 0
                    for m in range(len(time1)):
                        for k in range(lastIndice, len(time2)-1):
                            if time2[k] < time1[m] < time2[k+1]:
                                finalTime.append(time2[k])
                                finalPrice1.append(price1[m])
                                finalPrice2.append(price2[k])
                                lastIndice = k

                    if len(finalTime) > 2:
                        corr, _ = pearsonr(finalPrice1, finalPrice2)
                        if -1 <= corr <= 1:
                            coreSum += corr
                            coreNum += 1
                            print('', gregorian_to_jalali(today.strftime("%Y-%m-%d")), 'correlation: %.3f' % corr, end= '\r')

    return round(coreSum/coreNum, 2)                   

def get_yestedayPrice(offData, ID, indice, day: datetime.date):
    if offData[ID]['MinAllowedPrice'][indice] != None:
        yesterdayPrice = (offData[ID]['MinAllowedPrice'][indice]+offData[ID]['MaxAllowedPrice'][indice])/2
    else:
        allowedPrice = offlineLab.get_daily_allowed_price(ID, day)
        offlineData_repo().write_price_range(ID, day.strftime("%Y-%m-%d"), allowedPrice['Min'], allowedPrice['Max'])
        yesterdayPrice= (allowedPrice['Min']+allowedPrice['Max'])/2
    return yesterdayPrice


ticker1 = 'شپنا'
ticker2 = 'سرو'
fromDate = '1400-01-22'
toDate = '1400-12-28'
ID1 = ticker_repo().read_by_name(ticker1)['ID']
ID2 = ticker_repo().read_by_name(ticker2)['ID']

print(ticker1[::-1], ticker2[::-1], tickerCorrelation(ID1, ID2, fromDate, toDate), '                     ')
