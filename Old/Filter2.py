from SqlServerDataBaseLib import UpdateDailyRecordsOfDataTable, DatabaseConnection

file = open('Filter.txt', 'w', encoding = 'utf-8')

db = DatabaseConnection()
db.connect()

cmd = '''
select distinct ID, FarsiTicker from tickers where MarketTypeID in (1, 2, 3, 4, 5, 6, 7)
'''
db.execute(cmd)

IDs = []
FarsiTickers = []
for row in db.cursor:
    IDs.append(row['ID'])
    FarsiTickers.append(row['FarsiTicker'])

FilteredTickers = ''

for i in range(len(IDs)):
    cmd = '''
    select top 1 RealPower from data where ID = {} order by date desc
    '''.format(IDs[i])

    db.execute(cmd)

    RealPowers = []
    for row in db.cursor:
        RealPowers.append(row['RealPower'])
    
    if len(RealPowers) == 3:
        if RealPowers[0] > RealPowers[1] and RealPowers[1] > RealPowers[2]:
            if RealPowers[0] > 1.2:
                FilteredTickers += FarsiTickers[i] + '\n'

file.write(FilteredTickers)
file.close()

db.close()



