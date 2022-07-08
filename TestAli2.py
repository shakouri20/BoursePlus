

import datetime
import time
from Application.Services.WriteData.GetOnlineDataService import get_last_clientType_Data
from Application.Utility.Web.WebRequest import getCsvData
import DefaultParams as defParams

# t1 = time.perf_counter()
# csvData = getCsvData('http://www.tsetmc.com/tse/data/Export-txt.aspx?a=InsTrade&InsCode=7745894403636165&DateFrom=20200613&DateTo=20220613&b=0', ['\r\n', ','])
# print(time.perf_counter ()-t1)

# t1 = time.perf_counter()
# csvData = getCsvData('http://members.tsetmc.com/tsev2/data/InstTradeHistory.aspx?i=7745894403636165&Top=1&A=0', [';', '@'])
# print(time.perf_counter ()-t1)

# t1 = time.perf_counter()
# csvData = getCsvData(defParams.clientTypeIUrl.format(4247709727327181))
# print(time.perf_counter ()-t1)

# t1 = time.perf_counter()
# csvData = get_day_clientType_data(7745894403636165, '2022-06-13')
# print(time.perf_counter()-t1)

# print(csvData)

# t1 = time.perf_counter()
# csvData = getCsvData('http://www.tsetmc.com/tsev2/data/MarketWatchPlus.aspx?h=174955&r=10318087725', ['@', ';', ','])
# csvData = getCsvData('http://www.tsetmc.com/tsev2/data/MarketWatchPlus.aspx', ['@', ';', ','])
# csvData = getCsvData('http://members.tsetmc.com/tsev2/data/InstTradeHistory.aspx?i=62177651435283872&Top=10&A=0', [';', '@'])

# data = get_last_clientType_Data()


# print(time.perf_counter ()-t1)

# print(len(csvData[2][0]))

cmd = '''
tickers.ID in '''

IDs = str([364335, 54357, 3876])

print(cmd + IDs)