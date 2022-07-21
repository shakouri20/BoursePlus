from math import inf
from Domain.Enums.OnlineColumns import onlineColumns
from Infrastructure.Repository.OnlineDataRepository import onlineData_repo
from Application.Services.ReadData.ReadOffline.ReadOfflineServices import read_offline_services
from Application.Services.ReadData.ReadOnline.OnlineDataHandler import onlineDataHandler
from Application.Utility.DateConverter import *
from Infrastructure.Repository.TickerRepository import ticker_repo
import concurrent.futures
import json

date = '1400-06-30'
print(date)
distinctTimes = onlineData_repo().read_distinct_times_of_day(jalali_to_gregorian(date))
IDs = ticker_repo().read_list_of_tickers(tickerTypes= [1])["ID"]
IDs = [63915926161403347]
volumeAvg = read_offline_services.average.get_averge_volume(IDs, 30)

cache = onlineDataHandler(IDs)

totalTrades = []
buyedIDs = {}

def write_list(data: list):
        file = open(r'E:\TseExpertProject\TseTmc\LOG.txt', 'w')
        str = ''
        for trade in data:
            str += json.dumps(trade) + '\n'
        file.write(str)
        file.close()


for thisTime in distinctTimes[10:]:

    data = onlineData_repo().read_onlineData_by_every_time(thisTime)
    cache.update(data)
    print(thisTime)

    # run strategy

    # rpvp = cache.rpvp(num= 1)
    volumeDif = cache.clientVolumeDif(decNum= 2, Num= 1)
    # perCapitaSell = cache.perCapitaSell(num= 1)
    lastPrice = cache.lastPrice(num= 1)
    lastPricePRC = cache.lastPricePRC(num= 1)
    yesterdayPrice = cache.yesterdayPrice()
    minAllowedPrice = cache.minAllowedPrice()
    row1 = cache.row1(decNum= 4, num= 2)
    demToSupPower = cache.demandToSupplyPower(num= 3)

    availableIDs = list(lastPrice.keys())

    def single_ticker_calc(ID):

        if ID in volumeAvg:

            # volume check
            if lastPrice[ID][0] * volumeAvg[ID] > 20000000000:
                normalVolume = volumeDif[ID][-1]/volumeAvg[ID]*3.5*60
                if normalVolume > 50:
                    # price Check
                    if (lastPrice[ID][0] - minAllowedPrice[ID]) / minAllowedPrice[ID] * 100 < 1:
                        # check sell queue
                        if len(row1[onlineColumns.SupplyVolume1.value][ID]) == 2:
                            if row1[onlineColumns.SupplyPrice1.value][ID][0] == minAllowedPrice[ID]:
                                if row1[onlineColumns.SupplyPrice1.value][ID][1] == minAllowedPrice[ID]:
                                    if row1[onlineColumns.SupplyVolume1.value][ID][0] > 10 * row1[onlineColumns.SupplyVolume1.value][ID][1]:
                                        # if perCapitaSell[ID][0] > 5:
                                        if len(list(buyedIDs.keys())) < 4 and ID not in buyedIDs:
                                            # print(ID, lastPricePRC[ID][0], "is bought...")
                                            totalTrades.append({'ID': ID, 'BuyTime': thisTime, 'BuyPricePRC': lastPricePRC[ID][0]})
                                            write_list(totalTrades)
                                            print(ID, lastPricePRC[ID][0], "Signal...")
                                            buyedIDs[ID] = False  
                                        else:
                                            print(ID, lastPricePRC[ID][0], "Signal...")
                                # elif perCapitaSell[ID][0] > 5:
                                elif len(list(buyedIDs.keys())) < 4 and ID not in buyedIDs:
                                    # print(ID, lastPricePRC[ID][0], "is bought...")
                                    totalTrades.append({'ID': ID, 'BuyTime': thisTime, 'BuyPricePRC': lastPricePRC[ID][0]})
                                    write_list(totalTrades)
                                    print(ID, lastPricePRC[ID][0], "Signal...")
                                    buyedIDs[ID] = False  
                                else:
                                    print(ID, lastPricePRC[ID][0], "Signal...")

                                       

        if ID in buyedIDs:
            for trade in totalTrades:
                if trade['ID'] == ID and 'SellTime' not in trade:

                    if buyedIDs[ID] == True:
                        if demToSupPower[ID][-1] < -0.8:
                            trade['SellTime'] = thisTime
                            trade['SellPricePRC'] = lastPricePRC[ID][0]
                            trade['Profit'] = trade['SellPricePRC'] - trade['BuyPricePRC'] - 1.25
                            del buyedIDs[ID]
                            # print(ID, lastPricePRC[ID][0], "is sold...")
                            write_list(totalTrades)
                            x = 1
                        else:
                            for thisDemToSup in demToSupPower[ID]:
                                if thisDemToSup > -0.2:
                                    break
                            else:
                                trade['SellTime'] = thisTime
                                trade['SellPricePRC'] = lastPricePRC[ID][0]
                                trade['Profit'] = trade['SellPricePRC'] - trade['BuyPricePRC'] - 1.25
                                del buyedIDs[ID]
                                # print(ID, lastPricePRC[ID][0], "is sold...")
                                write_list(totalTrades)
                                x = 1

                    if ID in buyedIDs and buyedIDs[ID] == False and demToSupPower[ID][-1] > 0.2:
                        buyedIDs[ID] = True
                        x = 1

                    break

    for ID in availableIDs:
        single_ticker_calc(ID)

    # with concurrent.futures.ThreadPoolExecutor(max_workers= 1) as executor:
    #     future_to_data = {executor.submit(single_ticker_calc, IDs[k]): k for k in range(len(availableIDs))}
    #     for future in concurrent.futures.as_completed(future_to_data):
    #         pass


print(totalTrades)