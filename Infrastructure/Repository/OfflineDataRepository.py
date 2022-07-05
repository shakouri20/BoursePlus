from Infrastructure.DbContext.DbContext import dbContext
from Application.Utility.DateConverter import *
from Domain.ImportEnums import *
from Settings import SettingsService 
from Infrastructure.Repository.TickerRepository import ticker_repo
import datetime

class offlineData_repo(dbContext):

    def __init__(self) -> None:

        type = SettingsService.operation.get_runType_setting()
        if type == runType.BackTest:
            self.offlineTableName = tableType.MockOfflineData.value
        else:
            self.offlineTableName = tableType.OfflineData.value

        # Call parent init method
        super(offlineData_repo, self).__init__()

    
    def read_by_ID_and_time(self, *selectedColumns: str, ID: int, fromDate = '1300-01-01', toDate = '2500-01-01', outputDateType = dateType.jalali) -> dict:
        """ Returns the reqested columns from offline table for specified Id. fromDate and toDate are optioanl."""
        fromDate = jalali_to_gregorian(fromDate)
        toDate = jalali_to_gregorian(toDate)
        data = self.read_general(*selectedColumns, table= tableType.OfflineData.value, filter= f"ID = {ID} and Time between '{fromDate}' and '{toDate}' order by Time asc")
        if 'Time' in selectedColumns:
            if outputDateType == dateType.jalali:
                data['Time'] = [gregorian_to_jalali(data['Time'][i].strftime("%Y-%m-%d")) for i in range(len(data['Time']))]
            else:
                data['Time'] = [data['Time'][i].strftime("%Y-%m-%d") for i in range(len(data['Time']))]
        return data
        
    def read_by_farsiTicker_and_time(self, *selectedColumns: str, farsiTicker: str, fromDate = '1300-01-01', toDate = '2500-01-01', outputDateType = dateType.jalali) -> dict:
        """ Returns the reqested columns from offline table for ticker name. fromDate and toDate are optioanl."""
        ID = ticker_repo().read_by_name(farsiTicker)['ID']
        fromDate = jalali_to_gregorian(fromDate)
        toDate = jalali_to_gregorian(toDate)
        if ID == None:
            return None
        data = self.read_general(*selectedColumns, table= tableType.OfflineData.value, filter= f"ID = {ID} and Time between '{fromDate}' and '{toDate}' order by Time asc")
        if 'Time' in selectedColumns:
            if outputDateType == dateType.jalali:
                data['Time'] = [gregorian_to_jalali(data['Time'][i].strftime("%Y-%m-%d")) for i in range(len(data['Time']))]
            else:
                data['Time'] = [data['Time'][i].strftime("%Y-%m-%d") for i in range(len(data['Time']))]
        return data

    def read_lastDate_and_lastTodayPrice_by_ID(self, ID: int) -> dict:
        """ Returns the last available price and corresponding Time for an Id in offline Data table """
        resultDict = self.read_general('top 1 Time, TodayPrice', table= tableType.OfflineData.value, filter= f"ID = {ID} order by Time desc")
        if resultDict == None:
            return None
        outputDict = {}
        outputDict['LastTime'] = resultDict['Time'][0]
        outputDict['LastTodayPrice'] = resultDict['TodayPrice'][0]
        return outputDict
    
    def delete_data_by_ID(self, ID: int) -> None:
        """ Deletes data for an Id from offline data table """
        self.connect()
        self.execute(f"delete from {tableType.OfflineData.value} where ID = {ID}")
        self.commit()
        self.close()

    # applied settings
    def write(self, table: str, dataList: list, isIndex: bool= False):
        """ Write ticker offline data in table with option that Ticker is Index or not"""
        self.connect()
        if isIndex == False:
            cmd = 'insert into {} values (%d, %s, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d)'.format(table)
            self.executemany(cmd, dataList)
        else:
            cmd = '''
            insert into {} (ID, Time, LowPrice, HighPrice, OpenPrice, closePrice, TodayPrice, YesterdayPrice, Volume, Value, Number)
            values (%d, %s, %d, %d, %d, %d, %d, %d, %d, %d, %d)
            '''.format(table)
            self.executemany(cmd, dataList)
        self.commit()
        self.close()

    # applied settings
    def read_last_N_offlineData(self, *selectedColumns: str, Num: int, IDList: list, table: str = None):
        '''returns last n offline data'''
        if table == None:
            return self.read_last_N_data(*selectedColumns, table= self.offlineTableName, Num= Num, IDList= IDList)
        else:
            return self.read_last_N_data(*selectedColumns, table= table, Num= Num, IDList= IDList)

    # applied settings
    def filter_tickerIDList_by_daysNumberTraded_and_lastTradeDate(self, IDList: list, daysNumberFilter: int = 200, lastDatefilter: str = '1400-01-01', table: str = None) -> list:
        """returns tickerIDList filtered by daysNumberTraded and lastTradeDate"""
        # convert lastDayFilter to gregorian datetime.date format
        lastDatefilter = jalali_to_gregorian(lastDatefilter)
        lastDatefilter = datetime.date(int(lastDatefilter[:4]), int(lastDatefilter[5:7]), int(lastDatefilter[8:10]))

        tableName = self.offlineTableName if table == None else table

        filteredIDList = []

        self.connect()

        for ID in IDList:
            # get daysNumberTraded
            cmd = f'''
                select count(ID) as cnt from {tableName} where ID = {ID}
            '''
            self.execute(cmd)
            daysNumberTraded = self.fetchall()[0]['cnt']
            # get lastTradeDate
            cmd = f'''
                select max(Time) as maxTime from {tableName} where ID = {ID}
            '''
            self.execute(cmd)
            lastTradeDate = self.fetchall()[0]['maxTime']

            if daysNumberTraded > daysNumberFilter and lastTradeDate > lastDatefilter:
                filteredIDList.append(ID)

        self.close()

        return filteredIDList


    # Mock**************************
    def delete_all_MockOfflineData_rows(self) -> None:
        '''deletes all MockOfflineData rows'''
        self.connect()
        self.execute(f"delete from {tableType.MockOfflineData.value}")
        self.commit()
        self.close()

    def read_last_N_OfflineData_by_date(self, Num: int, IDList: list, date: str, outPutType= queryOutPutType.ListDict) -> list:
        '''returns last n offlineData as a list, date is in gregorian mode'''

        dataList = []
        dataDict = {}
        self.connect()

        for ID in IDList:
            # print(ID)
            cmd = f"select top {Num} * from {tableType.OfflineData.value} where ID = {ID} and Time < '{date}' order by Time desc"
            self.execute(cmd)
            thisIDResult = self.fetchall()
            dataList += thisIDResult

            if thisIDResult != []:
                resultDict = {}
                for thisKey in thisIDResult[0]:
                    if thisKey != 'ID':
                        resultDict[thisKey] = [thisIDResult[i][thisKey] for i in range(len(thisIDResult))]
                        resultDict[thisKey] = resultDict[thisKey][::-1]
                dataDict[ID] = resultDict

        self.close()

        if outPutType == queryOutPutType.ListDict:
            return dataList
        elif outPutType == queryOutPutType.DictDict:
            return dataDict
        else:
            raise Exception ('Wrong outPutType!')
            
    def write_isIPO_in_tickers_table(self) -> None:

        IDs = ticker_repo().read_list_of_tickers()['ID']
        data = self.read_last_N_offlineData('RealBuyVolume', 'RealBuyNumber', 'RealSellVolume', 'RealSellNumber', 'TodayPrice', Num= 4, IDList= IDs)

        self.connect()

        for ID in data:

            print(ID)

            if len(data[ID]['TodayPrice']) == 0:
                self.execute(f'update {tableType.Tickers.value} set isIPO = 0 where ID = {ID}')
                continue

            realPowerAverage = []
            perCapitaSellAverage = []

            for i in range(len(data[ID]['TodayPrice'])):

                try:
                    realPowerAverage.append((data[ID]['RealBuyVolume'][i]/data[ID]['RealBuyNumber'][i])/(data[ID]['RealSellVolume'][i]/data[ID]['RealSellNumber'][i]))
                    perCapitaSellAverage.append(data[ID]['RealSellVolume'][i]/data[ID]['RealSellNumber'][i]*data[ID]['TodayPrice'][i]/10**7)
                except:
                    pass

            if len(realPowerAverage) == 0 or len(perCapitaSellAverage) == 0:
                self.execute(f'update {tableType.Tickers.value} set isIPO = 0 where ID = {ID}')
                continue

            realPowerAverage = sum(realPowerAverage) / len(realPowerAverage)
            perCapitaSellAverage = sum(perCapitaSellAverage) / len(perCapitaSellAverage)

            if realPowerAverage > 2 and perCapitaSellAverage < 6:
                self.execute(f'update {tableType.Tickers.value} set isIPO = 1 where ID = {ID}')
            else:
                self.execute(f'update {tableType.Tickers.value} set isIPO = 0 where ID = {ID}')

        self.commit()
        self.close()

    def read_OfflineData_in_time_range(self, *selectedColumns: str, table: str, IDList: list, fromDate: str, toDate: str):
        '''returns last in time range from selected table in selected outPutType format, date is in gregorian mode'''

        data = {}
        if len(selectedColumns) == 1 and selectedColumns[0] == 'all':
            columnsStr = '* '
        else:
            columnsStr = 'ID, '
            for thisColumn in selectedColumns:
                columnsStr += thisColumn + ', '
            columnsStr = columnsStr[:-2] + ' '

        for ID in IDList:
            # query
            cmd = f'select ' + columnsStr +\
                f'''from {table} where ID = {ID} and time between '{fromDate}' and '{toDate}' order by Time asc'''
            # get data
            self.connect()
            self.execute(cmd)
            result = self.fetchall()
            self.close()
            
            if len(result) == 0:
                continue

            resultDict = {}
            for thisKey in result[0]:
                if thisKey != 'ID':
                    resultDict[thisKey] = [result[i][thisKey] for i in range(len(result))]
            data[ID] = resultDict

        return data

    def write_price_range(self, ID, day, minAllowedPrice, maxAllowedPrice):
        """ Write ticker offline data in table with option that Ticker is Index or not"""
        self.connect()
        cmd = f"update {tableType.OfflineData.value} set MinAllowedPrice = {minAllowedPrice}, MaxAllowedPrice = {maxAllowedPrice} where ID = {ID} and time = '{day}'"
        self.execute(cmd)
        self.commit()
        self.close()
