from Application.Utility.DateConverter import gregorian_to_jalali, jalali_to_gregorian
from Infrastructure.Repository.OnlineDataRepository import onlineData_repo
from Infrastructure.Repository.TickerRepository import ticker_repo
from Application.Utility.Web.WebRequest import getCsvData
import DefaultParams as defParam
from Colors import bcolors
from datetime import datetime
import time
import os

def get_last_clientType_Data() -> dict:
    '''returns ClientTypeData as a dict whose keys is ticker Ids'''
    # get Data as list of lists
    csvData = getCsvData(defParam.clientTypeAllUrl)
    # define dict and defult parameters
    ClientTypeDataDict = {}
    lineLength = 9
    ID = 0
    RealBuyNumber = 1
    CorporateBuyNumber = 2
    RealBuyVolume = 3
    CorporateBuyVolume = 4
    RealSellNumber = 5
    CorporateSellNumber = 6
    RealSellVolume = 7
    CorporateSellVolume = 8
    # feeding dict
    for thisLine in csvData:
        if len(thisLine) == lineLength:
            isNumericAll = True
            for i in range(lineLength):
                if thisLine[i].isnumeric() == False:
                    isNumericAll = False
                    break
            if isNumericAll == True:
                thisID = int(thisLine[ID])
                ClientTypeDataDict[thisID] = {}
                ClientTypeDataDict[thisID]['RealBuyNumber'] = int(thisLine[RealBuyNumber])
                ClientTypeDataDict[thisID]['CorporateBuyNumber'] = int(thisLine[CorporateBuyNumber])
                ClientTypeDataDict[thisID]['RealBuyVolume'] = int(thisLine[RealBuyVolume])
                ClientTypeDataDict[thisID]['CorporateBuyVolume'] = int(thisLine[CorporateBuyVolume])
                ClientTypeDataDict[thisID]['RealSellNumber'] = int(thisLine[RealSellNumber])
                ClientTypeDataDict[thisID]['CorporateSellNumber'] = int(thisLine[CorporateSellNumber])
                ClientTypeDataDict[thisID]['RealSellVolume'] = int(thisLine[RealSellVolume])
                ClientTypeDataDict[thisID]['CorporateSellVolume'] = int(thisLine[CorporateSellVolume])
    return ClientTypeDataDict

def get_last_marketWatch_data_1() -> dict:
    '''returns MarketWatchData as a dict whose keys is ticker Ids'''
    # get Data as list of lists
    csvData = getCsvData(defParam.newMarketWatchUrl, splitters= ['@', ';', ','])

    pricesData = csvData[2]
    ordersBoardData = csvData[3]

    # define dict and defult parameters
    # prices
    marketWatchDict = {}
    # pricesLineLength = 23
    ID = 0
    Name = 2
    LastTradeTime = 4
    FirstPrice = 5
    TodayPrice = 6
    LastPrice = 7
    Number = 8
    Volume = 9
    MinPrice = 11
    MaxPrice = 12
    YesterdayPrice = 13
    MaxAllowedPrice = 19
    MinAllowedPrice = 20
    ShareNumber = 21
    # orders board
    # OrdersLineLength = 8
    ID = 0
    Row = 1
    SupplyNumber = 2
    DemandNumber = 3
    DemandPrice = 4
    SupplyPrice = 5
    DemandVolume = 6
    SupplyVolume = 7

    for thisLine in pricesData:
        thisID = int(thisLine[ID])
        marketWatchDict[thisID] = {}
        marketWatchDict[thisID]['Name'] = thisLine[Name]
        marketWatchDict[thisID]['LastTradeTime'] = int(thisLine[LastTradeTime])
        marketWatchDict[thisID]['FirstPrice'] = int(thisLine[FirstPrice])
        marketWatchDict[thisID]['TodayPrice'] = int(thisLine[TodayPrice])
        marketWatchDict[thisID]['LastPrice'] = int(thisLine[LastPrice])
        marketWatchDict[thisID]['Number'] = int(thisLine[Number])
        marketWatchDict[thisID]['Volume'] = int(thisLine[Volume])
        marketWatchDict[thisID]['MinPrice'] = int(thisLine[MinPrice])
        marketWatchDict[thisID]['MaxPrice'] = int(thisLine[MaxPrice])
        marketWatchDict[thisID]['YesterdayPrice'] = int(thisLine[YesterdayPrice])
        marketWatchDict[thisID]['MaxAllowedPrice'] = int(float(thisLine[MaxAllowedPrice]))
        marketWatchDict[thisID]['MinAllowedPrice'] = int(float(thisLine[MinAllowedPrice]))
        marketWatchDict[thisID]['ShareNumber'] = int(thisLine[ShareNumber])

    for thisLine in ordersBoardData:
        thisID = int(thisLine[ID])
        if thisID in marketWatchDict:
            marketWatchDict[thisID][f'SupplyNumber{int(thisLine[Row])}'] = int(thisLine[SupplyNumber])
            marketWatchDict[thisID][f'DemandNumber{int(thisLine[Row])}'] = int(thisLine[DemandNumber])
            marketWatchDict[thisID][f'DemandPrice{int(thisLine[Row])}'] = int(thisLine[DemandPrice])
            marketWatchDict[thisID][f'SupplyPrice{int(thisLine[Row])}'] = int(thisLine[SupplyPrice])
            marketWatchDict[thisID][f'DemandVolume{int(thisLine[Row])}'] = int(thisLine[DemandVolume])
            marketWatchDict[thisID][f'SupplyVolume{int(thisLine[Row])}'] = int(thisLine[SupplyVolume])

    for ID in tuple(marketWatchDict.keys()):

        if "SupplyNumber5" not in marketWatchDict[ID]:
            del marketWatchDict[ID]
            continue
        if "SupplyNumber4" not in marketWatchDict[ID]:
            del marketWatchDict[ID]
            continue
        if "SupplyNumber3" not in marketWatchDict[ID]:
            del marketWatchDict[ID]
            continue
        if "SupplyNumber2" not in marketWatchDict[ID]:
            del marketWatchDict[ID]
            continue
        if "SupplyNumber1" not in marketWatchDict[ID]:
            del marketWatchDict[ID]
            continue

    return marketWatchDict

def get_last_marketWatch_data_2() -> dict:
    '''returns MarketWatchData as a dict whose keys is ticker Ids'''
    # get Data as list of lists
    csvData = getCsvData(defParam.newMarketWatchUrl, splitters= ['@', ';', ','])

    pricesData = csvData[2]
    ordersBoardData = csvData[3]

    # define dict and defult parameters
    # prices
    marketWatchDict = {}
    # pricesLineLength = 10
    ID = 0
    LastTradeTime = 1
    TodayPrice = 3
    LastPrice = 4
    Number = 5
    Volume = 6
    MinPrice = 8
    MaxPrice = 9
    # YesterdayPrice = 13
    # MaxAllowedPrice = 19
    # MinAllowedPrice = 20
    # orders board
    # OrdersLineLength = 8
    ID = 0
    Row = 1
    SupplyNumber = 2
    DemandNumber = 3
    DemandPrice = 4
    SupplyPrice = 5
    DemandVolume = 6
    SupplyVolume = 7

    for thisLine in pricesData:
        thisID = int(thisLine[ID])
        marketWatchDict[thisID] = {}
        marketWatchDict[thisID]['LastTradeTime'] = int(thisLine[LastTradeTime])
        marketWatchDict[thisID]['TodayPrice'] = int(thisLine[TodayPrice])
        marketWatchDict[thisID]['LastPrice'] = int(thisLine[LastPrice])
        marketWatchDict[thisID]['Number'] = int(thisLine[Number])
        marketWatchDict[thisID]['Volume'] = int(thisLine[Volume])
        marketWatchDict[thisID]['MinPrice'] = int(thisLine[MinPrice])
        marketWatchDict[thisID]['MaxPrice'] = int(thisLine[MaxPrice])
        # marketWatchDict[thisID]['YesterdayPrice'] = int(thisLine[YesterdayPrice])
        # marketWatchDict[thisID]['MaxAllowedPrice'] = int(float(thisLine[MaxAllowedPrice]))
        # marketWatchDict[thisID]['MinAllowedPrice'] = int(float(thisLine[MinAllowedPrice]))

    for thisLine in ordersBoardData:
        thisID = int(thisLine[ID])
        if thisID in marketWatchDict:
            marketWatchDict[thisID][f'SupplyNumber{int(thisLine[Row])}'] = int(thisLine[SupplyNumber])
            marketWatchDict[thisID][f'DemandNumber{int(thisLine[Row])}'] = int(thisLine[DemandNumber])
            marketWatchDict[thisID][f'DemandPrice{int(thisLine[Row])}'] = int(thisLine[DemandPrice])
            marketWatchDict[thisID][f'SupplyPrice{int(thisLine[Row])}'] = int(thisLine[SupplyPrice])
            marketWatchDict[thisID][f'DemandVolume{int(thisLine[Row])}'] = int(thisLine[DemandVolume])
            marketWatchDict[thisID][f'SupplyVolume{int(thisLine[Row])}'] = int(thisLine[SupplyVolume])

    for ID in tuple(marketWatchDict.keys()):

        if "SupplyNumber5" not in marketWatchDict[ID]:
            del marketWatchDict[ID]
            continue
        if "SupplyNumber4" not in marketWatchDict[ID]:
            del marketWatchDict[ID]
            continue
        if "SupplyNumber3" not in marketWatchDict[ID]:
            del marketWatchDict[ID]
            continue
        if "SupplyNumber2" not in marketWatchDict[ID]:
            del marketWatchDict[ID]
            continue
        if "SupplyNumber1" not in marketWatchDict[ID]:
            del marketWatchDict[ID]
            continue

    return marketWatchDict

def write_online_data() -> None:
    """saves ClientTypeData and MarketWatchData in OnlineData table"""

    os.system("color")

    while True:
        
        now = datetime.now()

        if now.hour >= 9 and now.hour <= 12:

            clientTypeData = get_last_clientType_Data()
            marketWatchData = get_last_marketWatch_data_1()

            onlineDataList = []

            for ID in clientTypeData:
                if ID in marketWatchData:
                    onlineDataList.append((ID,\
                                            now.strftime("%Y-%m-%d %H:%M:%S"),\
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
                                            marketWatchData[ID]['LastTradeTime']))
                                             
            try:
                onlineData_repo().write_onlineData(onlineDataList)
                print(now)

                time.sleep(15)

            except:
                print(f'{bcolors.WARNING}SQL Error{bcolors.ENDC}')

        else:
            time.sleep(60)

        if now.hour == 12 and now.minute >= 30:
            # os.system("shutdown /h")
            break

def write_mock_online(fromDate: str, toDate: str, strategiesDataPipes, dataUpdateQueue, numberOfStrategy) -> None:
    """Saves ClientTypeData and MarketWatchData in MockOnlineData table"""

    os.system("color")

    strategyCount = numberOfStrategy

    fromDate = jalali_to_gregorian(fromDate)
    toDate = jalali_to_gregorian(toDate)
    fromDateTime = datetime.strptime(fromDate, '%Y-%m-%d').date()
    toDateTime = datetime.strptime(toDate, '%Y-%m-%d').date()

    # finds days to process
    savedDays = onlineData_repo().read_saved_days()
    backTestDays = []
    for thisDay in savedDays:
        if thisDay >= fromDateTime and thisDay <= toDateTime:
            backTestDays.append(thisDay.strftime("%Y-%m-%d"))

    # print days to process
    print('Days to be processed:')
    for thisDay in backTestDays:
        print(gregorian_to_jalali(thisDay))

    # onlineData_repo().write_mockOnline_days_ago(backTestDays[0], num= 0)

    IDs = ticker_repo().read_list_of_tickers(tickerTypes= [1])['ID']

    # cache = onlineDataHandler(IDs)

    for thisDay in backTestDays:

        distinctTimes = onlineData_repo().read_distint_times_of_day(thisDay)

        for thisTime in distinctTimes:
            # wait for data update queue
            while strategyCount > 0:
                dataUpdateQueue.get()
                strategyCount -= 1

            strategyCount = numberOfStrategy

            # Starting to mock data and set event
            data = onlineData_repo().read_onlineData_by_every_time(thisTime)
            print(thisTime)

            print('Setting Event...')
            for key in strategiesDataPipes:
                strategiesDataPipes[key].send(data)

            print('Event set...')
            # cache.update(data)
            # cacheData = cache.data

    


