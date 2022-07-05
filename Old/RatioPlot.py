import matplotlib.pyplot as plt
from SqlServerDataBaseLib import DatabaseConnection
from DateConverter import *
from ta.momentum import *
from ta.trend import *
from ta.volatility import *

DB = DatabaseConnection()
DB.connect()

Ticker1 = 'خودرو و ساخت قطعات'
Ticker2 = '57-بانکها6'

Ticker1 = 'شاخص کل6'
Ticker2 = 'شاخص کل (هم وزن)6'

#main
Ticker1 = '60-حمل و نقل6'
Ticker2 = 'شاخص کل (هم وزن)6'

FromDate = '1400-01-01'
ToDate = '1401-12-04'

# First Ticker
cmd = '''
select Time, TodayPrice from OfflineData as D inner join tickers as T on D.id = T.id and T.FarsiTicker = '{}' and 
Time in (select Time from OfflineData inner join Tickers ON OfflineData.id = tickers.id where FarsiTicker = '{}' or FarsiTicker = '{}'
group by Time having count(OfflineData.id) = 2)  And D.Time between '{}' and '{}' order by D.Time asc
'''.format(Ticker1, Ticker1, Ticker2, jalali_to_gregorian(FromDate), jalali_to_gregorian(ToDate))
DB.execute(cmd)
Date1 = []
Price1 = []
for row in DB.cursor:
    Date1.append(gregorian_to_jalali(row['Time'].strftime("%Y-%m-%d")))
    Price1.append(row['TodayPrice'])

# Second Ticker
cmd = '''
select Time, TodayPrice from OfflineData as D inner join tickers as T on D.id = T.id and T.FarsiTicker = '{}' and 
Time in (select Time from OfflineData inner join Tickers ON OfflineData.id = tickers.id where FarsiTicker = '{}' or FarsiTicker = '{}'
group by Time having count(OfflineData.id) = 2)  And D.Time between '{}' and '{}' order by D.Time asc
'''.format(Ticker2, Ticker1, Ticker2, jalali_to_gregorian(FromDate), jalali_to_gregorian(ToDate))
DB.execute(cmd)
Price2 = []
for row in DB.cursor:
    Price2.append(row['TodayPrice'])
DB.commit()
DB.close()

Ratio = [Price1[i-1] / Price2[i-1] if Price2[i] == 0 else Price1[i] / Price2[i] for i in range(len(Date1))]

rsiObj = RSIIndicator(pd.Series(Ratio))
rsiData = rsiObj.rsi().to_list()

smaObj = SMAIndicator(pd.Series(Ratio), 10)
ratioMa = smaObj.sma_indicator().to_list()

macdObj = MACD(pd.Series(Ratio))
macdObj = macdObj.macd_diff().to_list()
macdAmp = max(abs(max(macdObj[33:])), abs(min(macdObj[33:])))
macdObj = [item/macdAmp*50+50 for item in macdObj]
smaObj = SMAIndicator(pd.Series(macdObj), 10)
macdMa = smaObj.sma_indicator().to_list()

ichObj = IchimokuIndicator(pd.Series(Ratio), pd.Series(Ratio), 9, 36, 52, False, False)
tekansen = ichObj.ichimoku_conversion_line().to_list()
kijunsen = ichObj.ichimoku_base_line().to_list()
    # return (, , ichObj.ichimoku_a().to_list(), ichObj.ichimoku_b().to_list())
  

fig, ax = plt.subplots(2, 1, sharex=True, figsize=(20,20)) # (width, height) in inchese)

ax[0].plot(Date1, Ratio, color='blue')

ax[0].plot(Date1, tekansen)
ax[0].plot(Date1, kijunsen)
ax[0].legend()
# ax[0].grid()

ax[1].plot(Date1, rsiData, color='blue')
ax[1].plot(Date1, [30 for _ in range(len(rsiData))], color='red')
ax[1].plot(Date1, [50 for _ in range(len(rsiData))], color='red')
ax[1].plot(Date1, [70 for _ in range(len(rsiData))], color='red')
clrs = ['red' if (x < 50) else 'green' for x in macdObj]
ax[1].bar(Date1, macdObj, color= clrs)
ax[1].plot(Date1, macdMa, color='black')
ax[1].legend()
# ax[1].grid()

plt.plot(Date1, Ratio)
plt.show()




