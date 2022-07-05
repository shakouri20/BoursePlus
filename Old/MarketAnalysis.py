from math import log10
from SqlServerDataBaseLib import DatabaseConnection
from DateConverter import *
import matplotlib.pyplot as plt

db = DatabaseConnection()
db.connect()

fromDate = '1401-01-01'
toDate = '1401-12-01'

cmd = '''
    select Time, ClosePrice from OfflineData where Time between '{}' and '{}' and ID = 32097828799138957 order by Time asc
'''.format(jalali_to_gregorian(fromDate), jalali_to_gregorian(toDate))
db.execute(cmd)

dates = []
closePrices = []

for row in db.cursor:
    dates.append(row['Time'].strftime("%Y-%m-%d"))
    closePrices.append(row['ClosePrice']) 

totalValue = []
totalRealMoney = []
totalRealPower = []

for thisDate in dates:


    cmd = '''
    select realBuyValue, realBuyNumber, realSellValue, realSellNumber, RealPower, Value from OfflineData
    inner join tickers on tickers.ID = OfflineData.ID
    where Time = '{}' and tickers.marketTypeId < 8
    '''.format(thisDate)
    db.execute(cmd)

    number = 0
    value = 0
    realMoney = 0
    realPower = 0


    for row in db.cursor:

        number += 1
        value += row['Value']
        realMoney += (row['realBuyValue']-row['realSellValue'])
        realPower += log10(row['RealPower'])

    totalValue.append(value)
    totalRealMoney.append(realMoney)
    totalRealPower.append(10 ** (realPower/number))

    # print(thisDate, value, realMoney, 10 ** realPower)

dates = [gregorian_to_jalali(dates[i]) for i in range(len(dates))]
f, ax = plt.subplots(nrows=4, ncols=1, sharex=True, figsize=(14,14))
ax[0].semilogy(dates, closePrices, 'blue')
ax[1].plot(dates, totalValue, color= 'black')
ax[2].bar(dates, totalRealMoney, color= 'green')
ax[3].plot(dates, totalRealPower, color= 'green')
ax[3].plot(dates, [1 for _ in range(len(dates))], color= 'red')

f.tight_layout() 
mng = plt.get_current_fig_manager()
mng.window.state('zoomed')   
plt.show()
