from math import inf, log10
from Domain.Enums.OnlineColumns import onlineColumns
from Infrastructure.Repository.OnlineDataRepository import onlineData_repo
from Application.Services.ReadData.ReadOffline.ReadOfflineServices import read_offline_services
from Application.Services.ReadData.ReadOnline.OnlineDataHandler import onlineDataHandler
from Application.Utility.DateConverter import *
from Infrastructure.Repository.TickerRepository import ticker_repo
import concurrent.futures   
import json, datetime

date = '1400-08-18'
print(date)
distinctTimes = onlineData_repo().read_distinct_times_of_day(jalali_to_gregorian(date))
IDs = ticker_repo().read_list_of_tickers(tickerTypes= [1])["ID"]
# IDs = [70219663893822560]
volumeAvg = read_offline_services.average.get_averge_volume(IDs, 30)

cache = onlineDataHandler(IDs)

totalTrades = []
buyedIDs = {}

def tr(a):
    return float('%.2f'%a)

def write_list(data: list):
    file = open(r'LOG.txt', 'w', encoding= 'utf-8')
    str = date + '\n'
    for trade in data:
        str += (json.dumps(trade, ensure_ascii=False).encode('utf8')).decode() + '\n'
    file.write(str)
    file.close()

def sell(trade, sellMethod):
    trade['ST'] = thisTime[-8:]
    trade['SP'] = tr(lastPricePRC[ID][-1])
    trade['M'] = sellMethod
    trade['P'] = tr(trade['SP'] - trade['BP'] - 1.25)
    if sellMethod == 'RPVP':
        trade['AV'] = (volumeAvg[ID], volumeDif[ID][-1])
    del buyedIDs[ID]
    print(trade['ST'])
    print(trade['N'][::-1], tr(lastPricePRC[ID][-1]), "Sell...")
    write_list(totalTrades)

def buy():

    farsiName = str(ticker_repo().read_by_ID(ID)['FarsiTicker'])

    if ID not in buyedIDs: # len(list(buyedIDs.keys())) < 3 and 

        totalTrades.append({'I': ID,
        'N': farsiName,
        'PCB': perCapitaBuyDif[ID][-1],
        'RP': tr(realPowerDif[ID][-1]),
        'V': int(volumeDif[ID][-1] * lastPrice[ID][0] /10000000),
        # 'RPV': int(int(volumeDif[ID][-1] * lastPrice[ID][0] /10000000)*log10(realPowerDif[ID][-1])),
        # 'F': tr((minAllowedPrice[ID] - maxPrice[ID][0]) / maxPrice[ID][0] * 100),
        # 'RF': -int(volumeDif[ID][-1] * lastPrice[ID][0] /10000000*log10(realPowerDif[ID][-1])/((minAllowedPrice[ID] - maxPrice[ID][0]) / maxPrice[ID][0] * 100)) if minAllowedPrice[ID] != maxPrice[ID][0] else inf,
        'BT': thisTime[-8:],
        'BP': tr(lastPricePRC[ID][-1])})
        # 'SL': tr(lastPricePRC[ID][-1]) - 1.25})
        # 'MSV': max(row1[onlineColumns.SupplyVolume1.value][ID])})
        write_list(totalTrades)
        print(thisTime[-8:])
        print(farsiName[::-1], tr(lastPricePRC[ID][-1]), "Buy...")
        buyedIDs[ID] = False  
    else:
        print(thisTime[-8:])
        print(farsiName[::-1], tr(lastPricePRC[ID][-1]), "Signal...")

onRepo = onlineData_repo()
onRepo.connect()

for thisTime in distinctTimes:

    data = onRepo.read_onlineData_by_every_time(thisTime)
    cache.update(data)
    # print(thisTime)

    # run strategy

    volumeDif = cache.clientVolumeDif(decNum= 4, num= 1)
    volumeDif3min = cache.clientVolumeDif(decNum= 10, num= 1)
    realPowerDif = cache.realPowerDif(decNum= 4, num= 1)
    realPowerDif3min = cache.realPowerDif(decNum= 10, num= 1)
    perCapitaBuyDif = cache.perCapitaBuyDif(decNum= 4, num= 1)
    perCapitaSellDif = cache.perCapitaSellDif(decNum= 4, num= 1)
    lastPrice = cache.lastPrice(num= 1)
    lastPricePRC = cache.lastPricePRC(num= 10)
    minAllowedPrice = cache.minAllowedPrice()
    maxPrice = cache.maxPrice(num= 1)
    row1 = cache.row1(num= 10)
    # demToSupPower = cache.demandToSupplyPower(num= 3)
    demandValue = cache.demandValue(num= 1)
    supplyValue = cache.supplyValue(num= 1)

    minPrice = cache.minPrice(num= 1)

    availableIDs = list(lastPrice.keys())

    def single_ticker_calc(ID):

        if ID in volumeAvg:

            # if lastPrice[ID][0] * volumeAvg[ID] > 20000000000:
            normalVolume = volumeDif[ID][-1]/volumeAvg[ID]*3.5*60
            valueDif = volumeDif[ID][-1] * lastPrice[ID][0] /10000000
            # realPowerValueProduct = int(valueDif*log10(realPowerDif[ID][-1]))

            if normalVolume > 5 and valueDif > 500 and realPowerDif[ID][-1] > 1.5: # and realPowerValueProduct > 400
                
                # tmp = (lastPrice[ID][0] - minAllowedPrice[ID]) / minAllowedPrice[ID] * 100
                # fallPRC = (minAllowedPrice[ID] - maxPrice[ID][0]) / maxPrice[ID][0] * 100

                if lastPricePRC[ID][-1] < -2: # and fallPRC > -6 and tmp < 1
            
                    if perCapitaBuyDif[ID][-1] > 80: #  and perCapitaSell[ID][0] > 5

                        if len(row1[onlineColumns.SupplyVolume1.value][ID]) >= 2:

                            maxSellQueueVolume = max(row1[onlineColumns.SupplyVolume1.value][ID])
                            maxSellQueueVolumeIndex = row1[onlineColumns.SupplyVolume1.value][ID].index(maxSellQueueVolume)

                            if row1[onlineColumns.SupplyPrice1.value][ID][maxSellQueueVolumeIndex] == minAllowedPrice[ID]:
                                if row1[onlineColumns.SupplyPrice1.value][ID][-1] != minAllowedPrice[ID]:
                                    buy()
                                elif maxSellQueueVolume > 20 * row1[onlineColumns.SupplyVolume1.value][ID][-1]:
                                    buy()
                            # else:
                            #     buy()
                            

        if ID in buyedIDs:

            for trade in totalTrades:

                if trade['I'] == ID and 'ST' not in trade:

                    # # 1
                    # if buyedIDs[ID] == True:

                    #     # if demToSupPower[ID][-1] < -0.6:
                    #     #     sell(trade)
                    #     #     x = 1
                    #     # else:
                    #     #     for thisDemToSup in demToSupPower[ID]:
                    #     #         if thisDemToSup > -0.1:
                    #     #             break
                    #     #     else:
                    #     #         sell(trade)
                    #     #         x = 1
                    #     sellQueueValue = trade['MSV'] * minAllowedPrice[ID] / 10000000

                    #     if supplyValue[ID][0] > 0.08 * sellQueueValue and (demandValue[ID][0] == 0 or supplyValue[ID][0] / demandValue[ID][0] > 1.6):
                    #         sell(trade)

                    # if ID in buyedIDs and buyedIDs[ID] == False and demandValue[ID][0] > 1.5 * supplyValue[ID][0]: # demToSupPower[ID][0] > 0.1:
                    #     buyedIDs[ID] = True
                    #     x = 1

                    # break

                    # 2
                    buyTime = datetime.datetime.strptime(trade['BT'], '%H:%M:%S')
                    now = datetime.datetime.strptime(thisTime[-8:], '%H:%M:%S')

                    if lastPricePRC[ID][0] > trade['BP'] + 0.5 or now - buyTime > datetime.timedelta(minutes= 5):

                        if max(lastPricePRC[ID])-min(lastPricePRC[ID]) < 0.7 and realPowerDif3min[ID][-1] < 1:
                            sell(trade, 'range')
                            break
                    
                    # if len(realPowerDif3min[ID]) == 2:
                    #     normalVolume = volumeDif[ID][-1]/volumeAvg[ID]*3.5*60
                    #     if normalVolume > 3 and realPowerDif3min[ID][-1] < 0.4: #  and perCapitaSellDif[ID][-1] > 100
                    #         sell(trade, 'RPVP')
                    #         break

                    # if len(volumeDif3min[ID]) == 2:
                    #     normalVolume5min = volumeDif3min[ID][1]/volumeAvg[ID]*3.5*12 
                    #     if normalVolume5min < 0.1:
                    #         sell(trade, 'Volume')
                    #         break       

                    # trade['SL'] = tr(max(lastPricePRC[ID][-1]-1.5, trade['SL']))
                    # if lastPricePRC[ID][-1] < trade['SL']: 
                    #     sell(trade, 'SL')
                    #     break                     

    for ID in availableIDs:
        single_ticker_calc(ID)

    # with concurrent.futures.ThreadPoolExecutor(max_workers= 1) as executor:
    #     future_to_data = {executor.submit(single_ticker_calc, IDs[k]): k for k in range(len(availableIDs))}
    #     for future in concurrent.futures.as_completed(future_to_data):
    #         pass

onRepo.close()
# print(totalTrades)

totalProfit = 0
openTrades = 0

for trade in totalTrades:
    if 'P' in trade:
        totalProfit += trade['P']
    else:
        openTrades += 1


print('\n\nTotal Profit:', totalProfit)
print('openTrades:', openTrades)