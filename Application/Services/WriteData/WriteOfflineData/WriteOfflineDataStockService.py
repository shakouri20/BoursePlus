import datetime
import json
import requests
from Application.Utility.Web.WebRequest import getCsvData
from Infrastructure.Repository.TickerRepository import ticker_repo
from Infrastructure.Repository.OfflineDataRepository import offlineData_repo
import DefaultParams as defParams
from Application.Utility.DateConverter import *
from Domain.ImportEnums import *
import concurrent.futures
import os

today = datetime.datetime.now().date()

def write_mock_offline_data(date: str, Num: int = 300):
    '''deletes MockOfflineData and write last 'Num' tickers data before selected date in mockOfflineData.
    \n date is in gregorian mode'''

    offlineData_repo().disable_indexes(tableType.MockOfflineData.value)
    offlineData_repo().delete_all_MockOfflineData_rows()
    offlineData_repo().enable_indexes(tableType.MockOfflineData.value)
    IDs = ticker_repo().read_list_of_tickers(tickerTypes= [1])['ID']
    data = offlineData_repo().read_last_N_OfflineData_by_date(Num= Num, IDList= IDs, date= date)

    dataList = []
    
    for RowDict in data:
        dataList.append((RowDict['ID'],
                        RowDict['Time'].strftime("%Y-%m-%d"),
                        RowDict['LowPrice'],
                        RowDict['HighPrice'],
                        RowDict['OpenPrice'],
                        RowDict['ClosePrice'],
                        RowDict['TodayPrice'],
                        RowDict['YesterdayPrice'],
                        RowDict['Volume'],
                        RowDict['Value'],
                        RowDict['Number'],
                        RowDict['RealBuyNumber'],
                        RowDict['CorporateBuyNumber'],
                        RowDict['RealSellNumber'],
                        RowDict['CorporateSellNumber'],
                        RowDict['RealBuyVolume'],
                        RowDict['CorporateBuyVolume'],
                        RowDict['RealSellVolume'],
                        RowDict['CorporateSellVolume'],
                        RowDict['RealBuyValue'],
                        RowDict['CorporateBuyValue'],
                        RowDict['RealSellValue'],
                        RowDict['CorporateSellValue']))
    offRepo = offlineData_repo()
    offRepo.connect()
    offRepo.write(tableType.MockOfflineData.value, dataList)
    offRepo.close()

def write_offline_data_stock() -> None:

    print('\nStart Writing Every Stock File to Database...')

    # ID generator
    IDs = ticker_repo().read_list_of_tickers(tickerTypes= [1, 3, 4])['ID']
    # IDs = [7395271748414592]
    offRepo = offlineData_repo()
    # # parallel write
    # with concurrent.futures.ThreadPoolExecutor(max_workers= 2) as executor:
    #     future_to_data = {executor.submit(write_every_ID, IDs[k]): k for k in range(len(IDs))}
    #     for future in concurrent.futures.as_completed(future_to_data):
    #         os.system('cls')
    #         print('Exporting To SQL Server ... %d' % int((future_to_data[future]+1) / len(IDs) * 100), '% Completed!')   

    for i in range(len(IDs)):
        while True:
            try:
                write_every_ID(IDs[i], offRepo)
                break
            except Exception as e:
                print(e)
                continue
            
        # os.system('cls')
        # print('Exporting To SQL Server ... %d' % int((i+1) / len(IDs) * 100), '% Completed!')  
        print('', int((i+1) / len(IDs) * 100), '% Completed!', end= '\r')

    
    print('finished!')

def get_all_clientTypeData(ID: int) -> dict:
    '''returns ClientTypeData as a dict whose keys is dates'''
    # get Data as list of lists
    csvData = getCsvData(defParams.clientTypeIUrl.format(ID))
    # define dict and defult parameters
    ClientTypeDataDict = {}
    lineLength = 13
    # columns
    Date = 0
    RealBuyNumber = 1
    CorporateBuyNumber = 2
    RealSellNumber = 3
    CorporateSellNumber = 4
    RealBuyVolume = 5
    CorporateBuyVolume = 6
    RealSellVolume = 7
    CorporateSellVolume = 8
    RealBuyValue = 9
    CorporateBuyValue = 10
    RealSellValue = 11
    CorporateSellValue = 12
    # feeding dict
    for thisLine in csvData:
        if len(thisLine) == lineLength:
            # thisDate = gregorian_to_jalali(thisLine[Date][:4]+'-'+thisLine[Date][4:6]+'-'+thisLine[Date][6:8])
            thisDate = thisLine[Date][:4]+'-'+thisLine[Date][4:6]+'-'+thisLine[Date][6:8]
            ClientTypeDataDict[thisDate] = {}
            ClientTypeDataDict[thisDate]['RealBuyNumber'] = int(thisLine[RealBuyNumber])
            ClientTypeDataDict[thisDate]['CorporateBuyNumber'] = int(thisLine[CorporateBuyNumber])
            ClientTypeDataDict[thisDate]['RealBuyVolume'] = int(thisLine[RealBuyVolume])
            ClientTypeDataDict[thisDate]['CorporateBuyVolume'] = int(thisLine[CorporateBuyVolume])
            ClientTypeDataDict[thisDate]['RealSellNumber'] = int(thisLine[RealSellNumber])
            ClientTypeDataDict[thisDate]['CorporateSellNumber'] = int(thisLine[CorporateSellNumber])
            ClientTypeDataDict[thisDate]['RealSellVolume'] = int(thisLine[RealSellVolume])
            ClientTypeDataDict[thisDate]['CorporateSellVolume'] = int(thisLine[CorporateSellVolume])
            ClientTypeDataDict[thisDate]['RealBuyValue'] = int(thisLine[RealBuyValue])
            ClientTypeDataDict[thisDate]['CorporateBuyValue'] = int(thisLine[CorporateBuyValue])
            ClientTypeDataDict[thisDate]['RealSellValue'] = int(thisLine[RealSellValue])
            ClientTypeDataDict[thisDate]['CorporateSellValue'] = int(thisLine[CorporateSellValue])
    return ClientTypeDataDict

def get_prices_data(ID: int, dayNumber) -> list:
    """return Prices data as a list whose items is a dict"""

    # get Data as list of lists
    csvData = getCsvData(defParams.pricesIUrl.format(ID, dayNumber), [';', '@'])

    # define dict and defult parameters
    PricesDataList = []
    lineLength = 10

    # columns
    Date = 0
    HighPrice = 1
    LowPrice = 2
    TodayPrice = 3
    ClosePrice = 4
    OpenPrice = 5
    YesterdayPrice = 6
    Value = 7
    Volume = 8
    Number = 9

    for i in range(len(csvData)):
        if len(csvData[i]) == lineLength:
            PricesDataDict = {}
            thisDate = csvData[i][Date][:4]+'-'+csvData[i][Date][4:6]+'-'+csvData[i][Date][6:8]
            PricesDataDict['Date'] = thisDate
            PricesDataDict['LowPrice'] = int(float(csvData[i][LowPrice]))
            PricesDataDict['HighPrice'] = int(float(csvData[i][HighPrice]))
            PricesDataDict['OpenPrice'] = int(float(csvData[i][OpenPrice]))
            PricesDataDict['ClosePrice'] = int(float(csvData[i][ClosePrice]))
            PricesDataDict['TodayPrice'] = int(float(csvData[i][TodayPrice]))
            PricesDataDict['YesterdayPrice'] = int(float(csvData[i][YesterdayPrice]))
            PricesDataDict['Volume'] = int(float(csvData[i][Volume]))
            PricesDataDict['Value'] = int(float(csvData[i][Value]))
            PricesDataDict['Number'] = int(float(csvData[i][Number]))
            PricesDataList.append(PricesDataDict)
    return PricesDataList

def adjust_prices_data(dataList: list) -> list:
    '''returns adjusted prices data'''

    i = 0

    while i != len(dataList)-1:

        # check today's yesterdayPrice with yesterday's todayPrice
        if dataList[i]['YesterdayPrice'] != dataList[i+1]['TodayPrice']:

            multiplier = dataList[i]['YesterdayPrice'] / dataList[i+1]['TodayPrice']

            # print(dataList[i]['Date'], multiplier)
         
            for j in range(i+1, len(dataList)):
                dataList[j]['LowPrice'] *= multiplier
                dataList[j]['HighPrice'] *= multiplier
                dataList[j]['OpenPrice'] *= multiplier
                dataList[j]['ClosePrice'] *= multiplier
                dataList[j]['TodayPrice'] *= multiplier
                dataList[j]['YesterdayPrice'] *= multiplier

        ## check
        if int(dataList[i]['LowPrice']) == 0:
            dataList.pop(i)
            continue
        if int(dataList[i]['HighPrice']) == 0:
            dataList.pop(i)
            continue
        if int(dataList[i]['OpenPrice']) == 0:
            dataList.pop(i)
            continue
        if int(dataList[i]['ClosePrice']) == 0:
            dataList.pop(i)
            continue
        if int(dataList[i]['TodayPrice']) == 0:
            dataList.pop(i)
            continue
        if int(dataList[i]['YesterdayPrice']) == 0:
            dataList.pop(i)
            continue

        i += 1

    return dataList

def get_day_clientType_data(ID, day):
    day = day[:4] + day[5:7] + day[8:10]
    url = f"http://cdn.tsetmc.com/api/ClientType/GetClientTypeHistory/{ID}/{day}"
    while True:
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36'}
            response = requests.get(url, timeout=1, headers= headers)
            break
        except:
            pass
    
    try:
        data =  json.loads(response.text)['clientType']
    except:
        return None

    output = {}
    output['RealBuyNumber'] = data['buy_I_Count']
    output['CorporateBuyNumber'] = data['buy_N_Count']
    output['RealSellNumber'] = data['sell_I_Count']
    output['CorporateSellNumber'] = data['sell_N_Count']
    output['RealBuyVolume'] = data['buy_I_Volume']
    output['CorporateBuyVolume'] = data['buy_N_Volume']
    output['RealSellVolume'] = data['sell_I_Volume']
    output['CorporateSellVolume'] = data['sell_N_Volume']
    output['RealBuyValue'] = data['buy_I_Value']
    output['CorporateBuyValue'] = data['buy_N_Value']
    output['RealSellValue'] = data['sell_I_Value']
    output['CorporateSellValue'] = data['sell_N_Value']

    return output

def write_every_ID(ID: int, offRepo: offlineData_repo) -> None:
    '''connects to db and writes input's ID data to db'''

    # find the last date data
    TickerData = offRepo.read_lastDate_and_lastTodayPrice_by_ID(ID)

    if TickerData != None:

        lastDate =  TickerData['LastTime'].strftime("%Y-%m-%d")
        lastTodayPrice = TickerData['LastTodayPrice']  

        dayNumber = (today - TickerData['LastTime']).days + 1

        pricesData = get_prices_data(ID, dayNumber)
    
        if len(pricesData) == 0:
            return
            
        pricesData = adjust_prices_data(pricesData)

        for LineNum in range(len(pricesData)):
            if lastDate == pricesData[LineNum]['Date']:
                if lastTodayPrice == pricesData[LineNum]['TodayPrice']:
                    firstLineNumToWrite = LineNum - 1
                else:
                    pricesData = get_prices_data(ID, 100000)
                    pricesData = adjust_prices_data(pricesData)
                    firstLineNumToWrite = len(pricesData) - 2
                    offRepo.delete_data_by_ID(ID)
                    print(ID, 'deleted!')
                break
        else:
            pricesData = get_prices_data(ID, 100000)
            pricesData = adjust_prices_data(pricesData)
            firstLineNumToWrite = len(pricesData) - 2
            offRepo.delete_data_by_ID(ID)
            print(ID, "day not found! deleted!")


    else:
        pricesData = get_prices_data(ID, 100000)
        pricesData = adjust_prices_data(pricesData)
        firstLineNumToWrite = len(pricesData) - 2
        print(ID, "first time!")

        
    while True:
        try:
            clientTypesData = get_all_clientTypeData(ID)
            break
        except:
            continue

    dataList = [] 

    for i in range(firstLineNumToWrite, -1, -1):
        thisDate = pricesData[i]['Date']
        thisDatePricesDict = pricesData[i]
        if pricesData[i]['Date'] in clientTypesData:
            thisDateClientTypeDict = clientTypesData[thisDate]
        elif datetime.datetime.strptime(thisDate, "%Y-%m-%d") > datetime.datetime(2022, 1, 1):
            thisDateClientTypeDict = get_day_clientType_data(ID, thisDate)
            if thisDateClientTypeDict == None:
                print(ID, thisDate, 'ct not found')
                continue
        else:
            continue
        
        dataList.append((ID,
                        thisDatePricesDict['Date'],
                        thisDatePricesDict['LowPrice'],
                        thisDatePricesDict['HighPrice'],
                        thisDatePricesDict['OpenPrice'],
                        thisDatePricesDict['ClosePrice'],
                        thisDatePricesDict['TodayPrice'],
                        thisDatePricesDict['YesterdayPrice'],
                        thisDatePricesDict['Volume'],
                        thisDatePricesDict['Value'],
                        thisDatePricesDict['Number'],
                        thisDateClientTypeDict['RealBuyNumber'],
                        thisDateClientTypeDict['CorporateBuyNumber'],
                        thisDateClientTypeDict['RealSellNumber'],
                        thisDateClientTypeDict['CorporateSellNumber'],
                        thisDateClientTypeDict['RealBuyVolume'],
                        thisDateClientTypeDict['CorporateBuyVolume'],
                        thisDateClientTypeDict['RealSellVolume'],
                        thisDateClientTypeDict['CorporateSellVolume'],
                        thisDateClientTypeDict['RealBuyValue'],
                        thisDateClientTypeDict['CorporateBuyValue'],
                        thisDateClientTypeDict['RealSellValue'],
                        thisDateClientTypeDict['CorporateSellValue'], 
                        None, None))
        
    offRepo.write(tableType.OfflineData.value, dataList, isIndex= False)
    



