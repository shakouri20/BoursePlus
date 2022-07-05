from Infrastructure.Repository.DataBaseRepository import database_repo
import winsound

rp = database_repo()
rp.connect()

# ID generator
IDs = rp.read_list_of_tickers(marketType= [1])['ID']

# Offline Data Dict generator
volumeAvg = rp.read_monthly_Volume_by_ID_list(IDs)

# Online Data Dict generator
data = rp.read_online_lastData('Volume', 'RealPower', IDList= IDs)
print(data[7745894403636165])

rp.close()
winsound.Beep(500, 200)