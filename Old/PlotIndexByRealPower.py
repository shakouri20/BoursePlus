from math import log10
from SqlServerDataBaseLib import DatabaseConnection
from DateConverter import *
import matplotlib.pyplot as plt

db = DatabaseConnection()
db.connect()

FromDate = '1401-01-01'
ToDate = '1401-12-01'

cmd = '''
    select Time, ClosePrice from OfflineData where Time between '{}' and '{}' and ID = 32097828799138957 order by Time asc
'''.format(jalali_to_gregorian(FromDate), jalali_to_gregorian(ToDate))
db.execute(cmd)

Dates = []
ClosePrices = []

for row in db.cursor:
    Dates.append(row['Time'].strftime("%Y-%m-%d"))
    ClosePrices.append(row['ClosePrice']) 

TotRealPower = []
PowerFulTickersPRC = []
PowerFulTickersPRC = []
totalValue = []
totalRealMoney = []

for ThisDate in Dates:

    # print(ThisDate)
    cmd = '''
    select RealBuyValue, RealBuyNumber, RealSellValue, RealSellNumber, RealPower, Value from OfflineData
    inner join tickers on tickers.ID = OfflineData.ID
    where Time = '{}' and tickers.marketTypeId < 9
    '''.format(ThisDate)
    db.execute(cmd)

    RealBuyValue = 0
    RealBuyNumber= 0
    RealSellValue = 0
    RealSellNumber = 0

    PowerFulTicekrsNum = 0
    WeakTickersNum = 0

    value = 0
    realMoney = 0

    for row in db.cursor:
        # RealBuyValue += row['RealBuyValue']
        # RealBuyNumber += row['RealBuyNumber']
        # RealSellValue += row['RealSellValue']
        # RealSellNumber += row['RealSellNumber']
        
        # if row['RealPower'] >= 1:
        #     PowerFulTicekrsNum += 1
        # else:
        #     WeakTickersNum += 1

        value += row['Value']
        realMoney += (row['RealBuyValue']-row['RealSellValue'])

    
    # try:
    #     PowerFulTickersPRC.append(PowerFulTicekrsNum/(PowerFulTicekrsNum + WeakTickersNum)*100)
    # except:
    #     PowerFulTickersPRC.append(0)
    # try:
    #     RealPower = (RealBuyValue/RealBuyNumber)/(RealSellValue/RealSellNumber)
    #     if RealPower >= 1:
    #         TotRealPower.append(RealPower)
    #     else:
    #         TotRealPower.append(-1/RealPower)
    # except:
    #     TotRealPower.append(1)

    totalValue.append(value)
    totalRealMoney.append(realMoney)

Dates = [gregorian_to_jalali(Dates[i]) for i in range(len(Dates))]
f, ax = plt.subplots(nrows=3, ncols=1, sharex=True, figsize=(14,14))
# [log10(TotRealPower[i]) for i in range(len(TotRealPower))]
ax[0].semilogy(Dates, ClosePrices, 'blue')
# ax[1].bar(Dates, TotRealPower, color= 'green')
# ax[1].plot(Dates, [1 for i in range(len(TotRealPower))], 'red')
# ax[1].plot(Dates, [-1 for i in range(len(TotRealPower))], 'red')
# ax[1].plot(Dates, [0 for i in range(len(TotRealPower))], 'black')
# ax[2].bar(Dates, PowerFulTickersPRC, color= 'green')
ax[1].plot(Dates, totalValue, color= 'black')
ax[2].bar(Dates, totalRealMoney, color= 'green')

f.tight_layout() 
mng = plt.get_current_fig_manager()
mng.window.state('zoomed')   
plt.show()
