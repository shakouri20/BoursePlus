from math import inf, log10
from Domain.Enums.OnlineColumns import onlineColumns
from Infrastructure.Repository.OnlineDataRepository import onlineData_repo
from Application.Services.ReadData.ReadOffline.ReadOfflineServices import read_offline_services
from Application.Services.ReadData.ReadOnline.OnlineDataHandler import onlineDataHandler
from Application.Utility.DateConverter import *
from Infrastructure.Repository.TickerRepository import ticker_repo
import concurrent.futures
import json
from Application.Services.DataProcess import get_data_from_web
import os
from datetime import datetime
import time, winsound

date = '1400-07-03'
print(date)
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

    winsound.Beep(500, 200)

    trade['ST'] = datetime.now()
    trade['SP'] = tr(lastPricePRC[ID][0])
    trade['P'] = tr(trade['SP'] - trade['BP'] - 1.25)
    del buyedIDs[ID]
    print(trade['N'], lastPricePRC[ID][0], "Sell...")
    write_list(totalTrades)

def buy():

    winsound.Beep(500, 200)

    farsiName = str(ticker_repo().read_by_ID(ID)['FarsiTicker'])

    if len(list(buyedIDs.keys())) < 3 and ID not in buyedIDs:

        totalTrades.append({'I': ID,
        'N': farsiName,
        'PCB': perCapitaBuyDif[ID][-1],
        'RP': tr(realPowerDif[ID][-1]),
        'V': int(volumeDif[ID][-1] * lastPrice[ID][0] /10000000),
        'RPV': int(int(volumeDif[ID][-1] * lastPrice[ID][0] /10000000)*log10(realPowerDif[ID][-1])),
        'F': tr((minAllowedPrice[ID] - maxPrice[ID][0]) / maxPrice[ID][0] * 100),
        'RF': -int(volumeDif[ID][-1] * lastPrice[ID][0] /10000000*log10(realPowerDif[ID][-1])/((minAllowedPrice[ID] - maxPrice[ID][0]) / maxPrice[ID][0] * 100)) if minAllowedPrice[ID] != maxPrice[ID][0] else inf,
        'BT': datetime.now(),
        'BP': tr(lastPricePRC[ID][0]),
        'MSV': max(row1[onlineColumns.SupplyVolume1.value][ID])})
        # write_list(totalTrades)
        print(farsiName, lastPricePRC[ID][0], "Buy...")
        buyedIDs[ID] = False  
    else:
        print(farsiName, lastPricePRC[ID][0], "Signal...")

os.system("color")
startTime = datetime.now().replace(hour= 9, minute= 0)
stopTime = datetime.now().replace(hour= 12, minute= 30)
    
while True:

    if datetime.now() > startTime:
        
        try:
            cacheDataDict = get_data_from_web()
        except:
            continue

        if cacheDataDict == None:
            print('None')

        if cacheDataDict != None:

            cache.update(cacheDataDict)

            print(datetime.now())

            # run strategy

            volumeDif = cache.clientVolumeDif(decNum= 4, num= 1)
            realPowerDif = cache.realPowerDif(decNum= 4, num= 1)
            perCapitaBuyDif = cache.perCapitaBuyDif(decNum= 2, num= 1)
            perCapitaSell = cache.perCapitaSell(num= 1)
            lastPrice = cache.lastPrice(num= 1)
            lastPricePRC = cache.lastPricePRC(num= 1)
            minAllowedPrice = cache.minAllowedPrice()
            maxPrice = cache.maxPrice(num= 1)
            row1 = cache.row1(num= 10)
            # demToSupPower = cache.demandToSupplyPower(num= 3)
            demandValue = cache.demandValue(num= 1)
            supplyValue = cache.supplyValue(num= 1)

            availableIDs = list(lastPrice.keys())

            def single_ticker_calc(ID):

                if ID in volumeAvg:
                    # if lastPrice[ID][0] * volumeAvg[ID] > 20000000000:
                    normalVolume = volumeDif[ID][-1]/volumeAvg[ID]*3.5*60
                    valueDif = volumeDif[ID][-1] * lastPrice[ID][0] /10000000
                    # realPowerValueProduct = int(valueDif*log10(realPowerDif[ID][-1]))

                    if normalVolume > 10 and valueDif > 500 and realPowerDif[ID][-1] > 1: # and realPowerValueProduct > 400
                        
                        tmp = (lastPrice[ID][0] - minAllowedPrice[ID]) / minAllowedPrice[ID] * 100
                        # fallPRC = (minAllowedPrice[ID] - maxPrice[ID][0]) / maxPrice[ID][0] * 100

                        if tmp < 1 and lastPricePRC[ID][0] < -2: # and fallPRC > -6
                    
                            if perCapitaBuyDif[ID][-1] > 60 and perCapitaSell[ID][0] > 5:

                                if len(row1[onlineColumns.SupplyVolume1.value][ID]) >= 2:

                                    maxSellQueueVolume = max(row1[onlineColumns.SupplyVolume1.value][ID])
                                    maxSellQueueVolumeIndex = row1[onlineColumns.SupplyVolume1.value][ID].index(maxSellQueueVolume)

                                    if row1[onlineColumns.SupplyPrice1.value][ID][maxSellQueueVolumeIndex] == minAllowedPrice[ID]:
                                        if row1[onlineColumns.SupplyPrice1.value][ID][-1] != minAllowedPrice[ID]:
                                            buy()
                                        elif maxSellQueueVolume > 10 * row1[onlineColumns.SupplyVolume1.value][ID][-1]:
                                            buy()
                                    

                if ID in buyedIDs:

                    for trade in totalTrades:

                        if trade['I'] == ID and 'ST' not in trade:

                            if buyedIDs[ID] == True:

                                # if demToSupPower[ID][-1] < -0.6:
                                #     sell(trade)
                                #     x = 1
                                # else:
                                #     for thisDemToSup in demToSupPower[ID]:
                                #         if thisDemToSup > -0.1:
                                #             break
                                #     else:
                                #         sell(trade)
                                #         x = 1
                                sellQueueValue = trade['MSV'] * minAllowedPrice[ID] / 10000000

                                if supplyValue[ID][0] > 0.08 * sellQueueValue and (demandValue[ID][0] == 0 or supplyValue[ID][0] / demandValue[ID][0] > 1.6):
                                    sell(trade)

                            if ID in buyedIDs and buyedIDs[ID] == False and demandValue[ID][0] > 1.5 * supplyValue[ID][0]: # demToSupPower[ID][0] > 0.1:
                                buyedIDs[ID] = True
                                x = 1

                            break

            for ID in availableIDs:
                single_ticker_calc(ID)

            # with concurrent.futures.ThreadPoolExecutor(max_workers= 1) as executor:
            #     future_to_data = {executor.submit(single_ticker_calc, IDs[k]): k for k in range(len(availableIDs))}
            #     for future in concurrent.futures.as_completed(future_to_data):
            #         pass

        time.sleep(15)
    if datetime.now() > stopTime:
        break

print(totalTrades)