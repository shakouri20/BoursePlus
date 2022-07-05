import datetime
from Application.Utility.AdvancedPlot import advancedPlot
from Application.Utility.DateConverter import *
from Application.Utility.Indicators.IndicatorService import calculateSma
from Domain.Models.TickerOfflineData import tickersGroupData
from Infrastructure.DbContext.DbSession import database_session
import pandas as pd

db = database_session()
db.connect()
db.execute('select distinct cast(time as date) as days from OnlineData where id = 1234 group by cast(time as date) order by cast(time as date) asc')
result = db.fetchall()
db.close()

days: list[datetime.date] = []
for row in result:
    days.append(row['days'])

finalData = []
for day in days[:]:
    data = tickersGroupData(day)
    minIndex = min(data.index)
    minTime = data.time[data.index.index(minIndex)].strftime("%H:%M:%S")
    maxIndex = max(data.index[data.index.index(minIndex):])
    maxTime = data.time[data.index.index(maxIndex)].strftime("%H:%M:%S")
    finalData.append([gregorian_to_jalali(day.strftime("%Y-%m-%d")), minTime, minIndex, maxTime, maxIndex, maxIndex-minIndex])

df = pd.DataFrame(data= finalData, columns=['Day', 'Min Time', 'Min Index', 'Max Time', 'Max Index', 'Rise'])
df.to_excel('indexLab.xlsx')

x = 1