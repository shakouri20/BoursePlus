from Application.Services.WriteData.GetOnlineDataService import *
from Infrastructure.Repository.OnlineDataRepository import onlineData_repo
from Application.Services.WriteData.WriteOfflineData.WriteOfflineDataStockService import write_mock_offline_data
from Domain.ImportEnums import *
import os
from datetime import datetime, timedelta
from Colors import bcolors
import time
from Application.Utility.DateConverter import *
from Application.Services.ReadData.ReadOnline.MarketWatchDataGenerator import marketWatchDataGenerator
from threading import Thread


def write_data_to_sql(data):
    try:
        onlineData_repo().write_onlineData(data)
        # print(datetime.now())

    except:
        print(f'{bcolors.WARNING}SQL Error{bcolors.ENDC}')

    return

def get_data_from_web():

    clientTypeData = get_last_clientType_Data()
    marketWatchData = get_last_marketWatch_data()

    onlineDataList = []
    cacheDataDict = {}
    
    now = datetime.now()

    for ID in clientTypeData:
        if ID in marketWatchData:
            onlineDataList.append((ID,\
                                    now,\
                                    marketWatchData[ID]['TodayPrice'],\
                                    marketWatchData[ID]['LastPrice'],\
                                    marketWatchData[ID]['Number'],\
                                    marketWatchData[ID]['Volume'],\
                                    marketWatchData[ID]['MinPrice'],\
                                    marketWatchData[ID]['MaxPrice'],\
                                    marketWatchData[ID]['YesterdayPrice'],\
                                    marketWatchData[ID]['MaxAllowedPrice'],\
                                    marketWatchData[ID]['MinAllowedPrice'],\
                                    clientTypeData[ID]['RealBuyNumber'],\
                                    clientTypeData[ID]['CorporateBuyNumber'],\
                                    clientTypeData[ID]['RealBuyVolume'],\
                                    clientTypeData[ID]['CorporateBuyVolume'],\
                                    clientTypeData[ID]['RealSellNumber'],\
                                    clientTypeData[ID]['CorporateSellNumber'],\
                                    clientTypeData[ID]['RealSellVolume'],\
                                    clientTypeData[ID]['CorporateSellVolume'],\
                                    marketWatchData[ID]['SupplyNumber1'],\
                                    marketWatchData[ID]['SupplyVolume1'],\
                                    marketWatchData[ID]['SupplyPrice1'],\
                                    marketWatchData[ID]['DemandPrice1'],\
                                    marketWatchData[ID]['DemandVolume1'],\
                                    marketWatchData[ID]['DemandNumber1'],\
                                    marketWatchData[ID]['SupplyNumber2'],\
                                    marketWatchData[ID]['SupplyVolume2'],\
                                    marketWatchData[ID]['SupplyPrice2'],\
                                    marketWatchData[ID]['DemandPrice2'],\
                                    marketWatchData[ID]['DemandVolume2'],\
                                    marketWatchData[ID]['DemandNumber2'],\
                                    marketWatchData[ID]['SupplyNumber3'],\
                                    marketWatchData[ID]['SupplyVolume3'],\
                                    marketWatchData[ID]['SupplyPrice3'],\
                                    marketWatchData[ID]['DemandPrice3'],\
                                    marketWatchData[ID]['DemandVolume3'],\
                                    marketWatchData[ID]['DemandNumber3'],\
                                    marketWatchData[ID]['SupplyNumber4'],\
                                    marketWatchData[ID]['SupplyVolume4'],\
                                    marketWatchData[ID]['SupplyPrice4'],\
                                    marketWatchData[ID]['DemandPrice4'],\
                                    marketWatchData[ID]['DemandVolume4'],\
                                    marketWatchData[ID]['DemandNumber4'],\
                                    marketWatchData[ID]['SupplyNumber5'],\
                                    marketWatchData[ID]['SupplyVolume5'],\
                                    marketWatchData[ID]['SupplyPrice5'],\
                                    marketWatchData[ID]['DemandPrice5'],\
                                    marketWatchData[ID]['DemandVolume5'],\
                                    marketWatchData[ID]['DemandNumber5'],\
                                    marketWatchData[ID]['heven']))
            cacheDataDict[ID] = {
                # 'Time': now.strftime("%Y-%m-%d %H:%M:%S"),
                'Time': now,
                'TodayPrice': marketWatchData[ID]['TodayPrice'],
                'LastPrice': marketWatchData[ID]['LastPrice'],
                'Number': marketWatchData[ID]['Number'],
                'Volume': marketWatchData[ID]['Volume'],
                'MinPrice': marketWatchData[ID]['MinPrice'],
                'MaxPrice': marketWatchData[ID]['MaxPrice'],
                'YesterdayPrice': marketWatchData[ID]['YesterdayPrice'],
                'MaxAllowedPrice': marketWatchData[ID]['MaxAllowedPrice'],
                'MinAllowedPrice': marketWatchData[ID]['MinAllowedPrice'],
                'RealBuyNumber': clientTypeData[ID]['RealBuyNumber'],
                'CorporateBuyNumber': clientTypeData[ID]['CorporateBuyNumber'],
                'RealBuyVolume': clientTypeData[ID]['RealBuyVolume'],
                'CorporateBuyVolume': clientTypeData[ID]['CorporateBuyVolume'],
                'RealSellNumber': clientTypeData[ID]['RealSellNumber'],
                'CorporateSellNumber': clientTypeData[ID]['CorporateSellNumber'],
                'RealSellVolume': clientTypeData[ID]['RealSellVolume'],
                'CorporateSellVolume': clientTypeData[ID]['CorporateSellVolume'],
                'SupplyNumber1': marketWatchData[ID]['SupplyNumber1'],
                'SupplyVolume1': marketWatchData[ID]['SupplyVolume1'],
                'SupplyPrice1': marketWatchData[ID]['SupplyPrice1'],
                'DemandPrice1': marketWatchData[ID]['DemandPrice1'],
                'DemandVolume1': marketWatchData[ID]['DemandVolume1'],
                'DemandNumber1': marketWatchData[ID]['DemandNumber1'],
                'SupplyNumber2': marketWatchData[ID]['SupplyNumber2'],
                'SupplyVolume2': marketWatchData[ID]['SupplyVolume2'],
                'SupplyPrice2': marketWatchData[ID]['SupplyPrice2'],
                'DemandPrice2': marketWatchData[ID]['DemandPrice2'],
                'DemandVolume2': marketWatchData[ID]['DemandVolume2'],
                'DemandNumber2': marketWatchData[ID]['DemandNumber2'],
                'SupplyNumber3': marketWatchData[ID]['SupplyNumber3'],
                'SupplyVolume3': marketWatchData[ID]['SupplyVolume3'],
                'SupplyPrice3': marketWatchData[ID]['SupplyPrice3'],
                'DemandPrice3': marketWatchData[ID]['DemandPrice3'],
                'DemandVolume3': marketWatchData[ID]['DemandVolume3'],
                'DemandNumber3': marketWatchData[ID]['DemandNumber3'],
                'SupplyNumber4': marketWatchData[ID]['SupplyNumber4'],
                'SupplyVolume4': marketWatchData[ID]['SupplyVolume4'],
                'SupplyPrice4': marketWatchData[ID]['SupplyPrice4'],
                'DemandPrice4': marketWatchData[ID]['DemandPrice4'],
                'DemandVolume4': marketWatchData[ID]['DemandVolume4'],
                'DemandNumber4': marketWatchData[ID]['DemandNumber4'],
                'SupplyNumber5': marketWatchData[ID]['SupplyNumber5'],
                'SupplyVolume5': marketWatchData[ID]['SupplyVolume5'],
                'SupplyPrice5': marketWatchData[ID]['SupplyPrice5'],
                'DemandPrice5': marketWatchData[ID]['DemandPrice5'],
                'DemandVolume5': marketWatchData[ID]['DemandVolume5'],
                'DemandNumber5': marketWatchData[ID]['DemandNumber5'],
                'heven': marketWatchData[ID]['heven']
            }                        
            
    return (onlineDataList, cacheDataDict)

def realTime_data_process(strategiesDataPipes):
    
    os.system("color")
    startTime = datetime.now().replace(hour= 9, minute= 3)
    stopTime = datetime.now().replace(hour= 12, minute= 30)

    marketWatchGen = marketWatchDataGenerator()
    
    while True:

        if datetime.now() > startTime:
            beginTime = datetime.now()
            cacheDataDict = {}

            (onlineDataList, cacheDataDict) = get_data_from_web()

            if len(list(cacheDataDict.keys())) == 0:
                print('Data Error... Continiuing...')
                continue

            cacheDataDict['TickersData'] = cacheDataDict

            thread1 = Thread(target= write_data_to_sql,
                                args= (onlineDataList,))
            thread1.start()

            cacheDataDict['MarketWatchData'] = marketWatchGen.get_marketWatchInfo(cacheDataDict['TickersData'])

            if cacheDataDict['TickersData'] != None:
                for key in strategiesDataPipes:
                    strategiesDataPipes[key].send(cacheDataDict)
            else:
                continue
            
            print(datetime.now().strftime("%H:%M:%S"))
            while True:
                now = datetime.now()
                timeDif: timedelta = now - beginTime
                if timeDif.seconds >= 3:
                    break
                else:
                    time.sleep(0.1)

            thread1.join()
        else:
            time.sleep(1)

        if datetime.now() >= stopTime:
            print('Exiting real data process...')
            return
    
def backTest_data_process(date: str, strategiesDataPipes, strategiesDataChildPipes, dataUpdateQueue, numberOfStrategy, finishEvent):
    # time.sleep(15)
    os.system("color")

    strategyCount = numberOfStrategy

    print('Writing MockOfflineData...')
    # write_mock_offline_data(jalali_to_gregorian(date), 45) 
    print('Done!')

    distinctTimes = onlineData_repo().read_distint_times_of_day(jalali_to_gregorian(date))

    marketWatchGen = marketWatchDataGenerator()
    db = onlineData_repo()

    for thisTime in distinctTimes[:]:
        # wait for data update queue
        # time.sleep(2)
        while strategyCount > 0:
            dataUpdateQueue.get()
            strategyCount -= 1

        strategyCount = numberOfStrategy

        while True:
            try:
                print(thisTime)
                data = db.read_onlineData_by_every_time(thisTime)
                break
            except:
                print('SQL ERROR............................!')
                db = onlineData_repo()
                continue

        cacheDataDict = {}

        cacheDataDict['TickersData'] = data
        cacheDataDict['MarketWatchData'] = marketWatchGen.get_marketWatchInfo(cacheDataDict['TickersData'])
        

        for key in strategiesDataPipes:
            clear_pipe(strategiesDataChildPipes[key])
            strategiesDataPipes[key].send(cacheDataDict)
        
        # time.sleep(1)

    finishEvent.set()
    time.sleep(15)


    print('Exiting data Process...')
    return

def clear_pipe(pipe):
    while pipe.poll(0.001):
        pipe.recv()
    



