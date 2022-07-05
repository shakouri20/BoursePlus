from math import log10
from Infrastructure.Repository.DataBaseRepository import database_repo
import winsound
import matplotlib.pyplot as plt
from Application.Utility.DateConverter import *
from statistics import stdev

db = database_repo()
db.connect()


fromDate = '1399-06-08'
toDate = '1400-09-08'

# get totalIndex 
data = db.read_offline_by_farsiTicker_and_date('Date', 'ClosePrice', farsiTicker= 'شاخص کل (هم وزن)6', fromDate= fromDate, toDate= toDate)
dates = data['Date']
totalIndex = data['ClosePrice']

#get desired IDs
IDs = db.read_general('ID', table= 'Tickers', filter= 'MarketTypeID < 5')['ID']

# lists
totalRealpowerList = []
totalRealpowerLogList = []
totalRealpowerLogSumList = []
ClosePricePrcAvg = []
ClosePricePrcStdev = []

# get every day data
for thisDateJ in dates:

    thisDateG = jalali_to_gregorian(thisDateJ)
    print(thisDateJ)

    # get data
    data = db.read_general('ID', 'ClosePricePRC', 'RealBuyValue', 'RealBuyNumber', 'RealSellValue', 'RealSellNumber', 'RealPower', table= 'data', filter= f"Date = '{thisDateG}' and ID in {tuple(IDs)}", outPutType= 'DictDict')
    
    RealBuyValue = 0
    RealBuyNumber= 0
    RealSellValue = 0
    RealSellNumber = 0
    ClosePricePrcs = []
    RealPowerLogSum = 0
    
    for ID in data:
        # real power
        if not(data[ID]['RealSellNumber'] > 300 and data[ID]['RealPower'] > 1 and (data[ID]['RealSellValue']/data[ID]['RealSellNumber'])/10000000 < 5):
            RealBuyValue += data[ID]['RealBuyValue']
            RealBuyNumber += data[ID]['RealBuyNumber']
            RealSellValue += data[ID]['RealSellValue']
            RealSellNumber += data[ID]['RealSellNumber']

            RealPowerLogSum += log10(data[ID]['RealPower'])
        # close prices
        ClosePricePrcs.append(data[ID]['ClosePricePRC'])

    # total real power
    try:
        totalRealpowerList.append((RealBuyValue/RealBuyNumber)/(RealSellValue/RealSellNumber))
        totalRealpowerLogList.append(log10((RealBuyValue/RealBuyNumber)/(RealSellValue/RealSellNumber)))
        totalRealpowerLogSumList.append(RealPowerLogSum/len(data.keys()))
    except:
        totalRealpowerList.append(0)
        totalRealpowerLogList.append(0)
        totalRealpowerLogSumList.append(0)

    # total closePrice avg and stdev
    try:
        ClosePricePrcAvg.append(sum(ClosePricePrcs)/len(ClosePricePrcs))
    except:
        ClosePricePrcAvg.append(0)
    try:
        ClosePricePrcStdev.append(stdev(ClosePricePrcs))
    except:
        ClosePricePrcStdev.append(0)

f, ax = plt.subplots(nrows=4, ncols=1, sharex=True, figsize=(14,14))
ax[0].semilogy(dates, totalIndex, 'blue')
ax[1].bar(dates, totalRealpowerLogList, color= 'blue')
ax[1].plot(dates, [0 for i in range(len(dates))], color= 'black')
# ax[2].bar(dates, totalRealpowerList, color= 'blue')
ax[2].bar(dates, ClosePricePrcAvg, color= 'green')
# ax[3].bar(dates, [totalRealpowerLogList[i]*ClosePricePrcAvg[i] for i in range(len(dates))], color= 'red')
# ax[4].bar(dates, ClosePricePrcStdev, color= 'black')
ax[3].bar(dates, totalRealpowerLogSumList, color= 'black')

f.tight_layout() 
mng = plt.get_current_fig_manager()
mng.window.state('zoomed')   
plt.show()

db.close()
winsound.Beep(500, 200)