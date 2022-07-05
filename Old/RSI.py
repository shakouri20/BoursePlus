from SqlServerDataBaseLib import DatabaseConnection

db = DatabaseConnection()

db.connect()

cmd = '''
select Date, TodayPrice from data where id = 7745894403636165 order by date asc
'''
db.execute(cmd)

Date = []
TodayPrice = []
for row in db.cursor:
    Date.append(row['Date'])
    TodayPrice.append(row['TodayPrice'])

db.close()

Gain = [0]
Loss = [0]

for i in range(1,len(Date)):
    if (TodayPrice[i]>TodayPrice[i-1]):
        Gain.append(TodayPrice[i]-TodayPrice[i-1])
        Loss.append(0)
    else:
        Loss.append(TodayPrice[i-1]-TodayPrice[i])
        Gain.append(0)


RSI = [0 for i in range(14)]

initGain = sum
