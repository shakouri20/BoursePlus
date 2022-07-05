from math import inf, log10
from Domain.Enums.OnlineColumns import onlineColumns
from Infrastructure.Repository.OnlineDataRepository import onlineData_repo
from Application.Services.ReadData.ReadOffline.ReadOfflineServices import read_offline_services
from Application.Services.ReadData.ReadOnline.OnlineDataHandler import onlineDataHandler
from Application.Utility.DateConverter import *
from Infrastructure.Repository.TickerRepository import ticker_repo
import concurrent.futures
import json

date = '1400-07-11'
print(date)
distinctTimes = onlineData_repo().read_distint_times_of_day(jalali_to_gregorian(date))
IDs = ticker_repo().read_list_of_tickers(tickerTypes= [1])["ID"]
# IDs = [70219663893822560]
volumeAvg = read_offline_services.average.get_averge_volume(IDs, 30)

cache = onlineDataHandler(IDs)

totalTrades = []
buyedIDs = {}

def tr(a):
    return float('%.2f'%a)

def write_list(data: list):
        file = open(r'E:\TseExpertProject\TseTmc\LOG.txt', 'w', encoding= 'utf-8')
        str = date + '\n'
        for trade in data:
            str += (json.dumps(trade, ensure_ascii=False).encode('utf8')).decode() + '\n'
        file.write(str)
        file.close()

def sell(trade):
    trade['ST'] = thisTime
    trade['SP'] = tr(lastPricePRC[ID][1])
    trade['P'] = tr(trade['SP'] - trade['BP'] - 1.25)
    del buyedIDs[ID]
    print(trade['N'], lastPricePRC[ID][1], "Sell...")
    write_list(totalTrades)

def buy():

    farsiName = str(ticker_repo().read_by_ID(ID)['FarsiTicker'])

    if ID not in buyedIDs: # len(list(buyedIDs.keys())) < 4 and 

        totalTrades.append({'I': ID,
        'N': farsiName,
        'PCB': perCapitaBuyDif[ID][-1],
        'RP': tr(realPowerDif[ID][-1]),
        'V': int(volumeDif[ID][-1] * lastPrice[ID][0] /10000000),
        'RPV': int(int(volumeDif[ID][-1] * lastPrice[ID][0] /10000000)*log10(realPowerDif[ID][-1])),
        'BT': thisTime,
        'BP': tr(lastPricePRC[ID][1])})
        write_list(totalTrades)
        print(farsiName, lastPricePRC[ID][1], "Buy...")
        buyedIDs[ID] = False  
    else:
        print(farsiName, lastPricePRC[ID][1], "Signal...")

for thisTime in distinctTimes:

    data = onlineData_repo().read_onlineData_by_every_time(thisTime)
    cache.update(data)
    print(thisTime)

    # run strategy

    volumeDif = cache.clientVolumeDif(decNum= 4, num= 1)
    realPowerDif = cache.realPowerDif(decNum= 4, num= 1)
    perCapitaBuyDif = cache.perCapitaBuyDif(decNum= 2, num= 1)
    perCapitaSell = cache.perCapitaSell(num= 1)
    lastPrice = cache.lastPrice(num= 1)
    lastPricePRC = cache.lastPricePRC(decNum= 2, num= 2)
    maxAllowedPrice = cache.maxAllowedPrice()
    maxPrice = cache.maxPrice(num= 1)
    # row1 = cache.row1(num=  10)
    # demToSupPower = cache.demandToSupplyPower(num= 3)
    # demandValue = cache.demandValue(num= 1)
    # supplyValue = cache.supplyValue(num= 1)

    availableIDs = list(lastPrice.keys())

    def single_ticker_calc(ID):

        if len(lastPricePRC[ID]) == 2:

            if ID in volumeAvg:
            # if lastPrice[ID][0] * volumeAvg[ID] > 20000000000:

                normalVolume = volumeDif[ID][-1]/volumeAvg[ID]*3.5*60
                valueDif = volumeDif[ID][-1] * lastPrice[ID][0] /10000000
                # realPowerValueProduct = int(valueDif*log10(realPowerDif[ID][-1]))

                if normalVolume > 5 and valueDif > 1000 and realPowerDif[ID][-1] > 1: # and realPowerValueProduct > 400
                    
                    # tmp = (lastPrice[ID][0] - maxAllowedPrice[ID]) / maxAllowedPrice[ID] * 100
                    # fallPRC = (minAllowedPrice[ID] - maxPrice[ID][0]) / maxPrice[ID][0] * 100

                    # if tmp > -3 and lastPricePRC[ID][0] > 0: # and fallPRC > -6
                
                    if perCapitaBuyDif[ID][-1] > 60 and perCapitaSell[ID][0] > 5:

                        if lastPricePRC[ID][1] - lastPricePRC[ID][0] > 1:
                         buy()
                            
            if ID in buyedIDs:

                for trade in totalTrades:

                    if trade['I'] == ID and 'SellTime' not in trade:

                        if lastPricePRC[ID][1] - trade['BP'] > 2.25 or lastPricePRC[ID][1] - trade['BP'] < -2.5:
                            sell(trade)


    for ID in availableIDs:
        single_ticker_calc(ID)

print(totalTrades)