from Domain.Enums.TableType import tableType
from Application.Utility.Web.WebRequest import getCsvData
from Infrastructure.Repository.TickerRepository import ticker_repo
from Infrastructure.Repository.OfflineDataRepository import offlineData_repo
import DefaultParams as defParams
from Application.Utility.DateConverter import *
import os
import concurrent.futures

def write_offline_data_index():
    # run tseClient
    run_tseClient()

    print('Start Writing Every Index File to Database...')

    # files properties
    FilesList = os.listdir(defParams.downloadPath)
    offRepo = offlineData_repo()

    # with concurrent.futures.ThreadPoolExecutor(max_workers= 5) as executor:
    #         future_to_data = {executor.submit(read_every_file, FilesList[k]): k for k in range(len(FilesList))}
    #         for future in concurrent.futures.as_completed(future_to_data):
    #             pass
    for file in FilesList:
        read_every_file(file, offRepo)
        
    print('Finished!')

def run_tseClient() -> None:
    """run TseClient and download the ticker distory data and save as csv file in specific path"""  

    # select IDs from database
    IDsList = ticker_repo().read_list_of_tickers(tickerTypes= [2])['ID']
    IDs = ''
    for ID in IDsList:
        IDs += str(ID) + '\n'

    # write the Ids to SelectedInstruments.csv
    path = defParams.selectedInstrumentsPath
    file = open(path, 'w', encoding = 'utf-8')
    file.write(IDs)
    file.close()

    # delete all files in DownloadPath
    dir = defParams.downloadPath
    for f in os.listdir(dir):
        os.remove(os.path.join(dir, f))

    print('DownLoading Index Files...')
    # download csv files From Tsetmc
    os.system('cmd /c "C: & cd {} & TseClient.exe fast"'.format(defParams.tseClientExePath))
    print('Download Completed.')

def get_all_pricesData(filePath: str) -> list:
    """return Prices data as a list whose items is a dict"""
    # open file and read
    myFile = open(filePath, 'r', encoding = 'utf-8')
    csvData = myFile.readlines()
    myFile.close()
    csvData = [row.split(",") for row in csvData]
    # define dict and defult parameters
    PricesDataList = []
    lineLength = 10
    # columns
    Date = 0
    LowPrice = 1
    HighPrice = 2
    OpenPrice = 3
    ClosePrice = 4
    TodayPrice = 5
    YesterdayPrice = 6
    Volume = 7
    Value = 8
    Number = 9
    # feeding dict
    for i in range(1, len(csvData)):
        if len(csvData[i]) == lineLength:
            PricesDataDict = {}
            # thisDate = gregorian_to_jalali(csvData[i][Date][:4]+'-'+csvData[i][Date][4:6]+'-'+csvData[i][Date][6:8])
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
            PricesDataDict['Number'] = int(float(csvData[i][Number].replace('\n', '')))
            PricesDataList.append(PricesDataDict)
    return PricesDataList

def read_every_file(thisFile, offRepo: offlineData_repo):

    if thisFile.endswith(".csv"):

        # find IR from file name
        IR = thisFile.replace('.csv', '')
        if '-a' in IR:
            IR = IR.replace('-a', '')

        # find ID from IR
        TickerData = ticker_repo().read_by_IR(IR)

        if TickerData != None:
            thisID =  TickerData['ID']

            # read pricesData
            filePath = f"{defParams.downloadPath}\{thisFile}"
            pricesData = get_all_pricesData(filePath)
            
            firstLineNumToWrite = 1

            # find the last date data
            TickerData = offRepo.read_lastDate_and_lastTodayPrice_by_ID(thisID)
            if TickerData != None:
                lastDate =  TickerData['LastTime'].strftime("%Y-%m-%d")
                lastTodayPrice = TickerData['LastTodayPrice']  
                
                for LineNum in range(len(pricesData)-1, -1, -1):
                    if lastDate == pricesData[LineNum]['Date']:
                        if lastTodayPrice == pricesData[LineNum]['TodayPrice']:
                            firstLineNumToWrite = LineNum + 1
                        else:
                            offRepo.delete_data_by_ID(thisID)
                        break

            
            dataList = []
            for i in range(firstLineNumToWrite, len(pricesData)):
                thisDatePricesDict = pricesData[i]
                dataList.append((thisID,\
                                thisDatePricesDict['Date'],\
                                thisDatePricesDict['LowPrice'],\
                                thisDatePricesDict['HighPrice'],\
                                thisDatePricesDict['OpenPrice'],\
                                thisDatePricesDict['ClosePrice'],\
                                thisDatePricesDict['TodayPrice'],\
                                thisDatePricesDict['YesterdayPrice'],\
                                thisDatePricesDict['Volume'],\
                                thisDatePricesDict['Value'],\
                                thisDatePricesDict['Number']))
            offRepo.write(tableType.OfflineData.value, dataList, isIndex= True)
