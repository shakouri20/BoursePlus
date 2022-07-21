from tkinter import N
from Application.Utility.General import create_ID_dict
from Infrastructure.DbContext.DbContext import dbContext
from Application.Utility.DateConverter import *
from Domain.ImportEnums import *
from Settings import SettingsService
from Infrastructure.Repository.TickerRepository import ticker_repo
import concurrent.futures as f
import threading, datetime

class onlineData_repo(dbContext):

    def __init__(self) -> None:

        type = SettingsService.operation.get_runType_setting()
        if type == runType.BackTest:
            self.onlineTableName = tableType.MockOnlineData.value
        else:
            self.onlineTableName = tableType.OnlineData.value

        # Call parent init method
        super(onlineData_repo, self).__init__()

    def read_by_ID_and_time(self, *selectedColumns: str, ID: int, fromTime, toTime) -> dict:
        """ Returns online data filtered by ID and time """
        return self.read_general(*selectedColumns, table= tableType.OnlineData, filter= f"ID = {ID} and Time between '{fromTime}' and '{toTime}' order by Time asc")

    def read_by_farsiTicker_and_time(self, *selectedColumns: str, tickerFarsi: str, fromTime, toTime) -> dict:
            """ Returns online data filtered by Farsi ticker and time """
            ID = ticker_repo().read_by_name(tickerFarsi)['ID']
            if ID == None:
                return None
            return self.read_general(*selectedColumns, table= tableType.OnlineData, filter= f"ID = {ID} and Time between '{fromTime}' and '{toTime}' order by Time asc")

    def write_onlineData(self, dataList: list):
        """Inserts priceData into OnlineData Table. Gets a list of tuples """
        self.connect()
        cmd = 'insert into {} values (%d, %s, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d)'.format(tableType.OnlineData.value)
        self.executemany(cmd, dataList)
        self.commit()
        self.close()

    # applied settings
    def read_last_N_OnlineData(self, *selectedColumns: str, Num: int, IDList: list) -> dict:
        '''returns last n data'''
        return self.read_last_N_data(*selectedColumns, table= self.onlineTableName, Num= Num, IDList= IDList)

    # applied settings
    def read_last_N_OrdersBoard(self, *selectedColumns: str, Num: int, IDList: list) -> dict:
        '''returns last n data'''
    
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
            cmd = f'select top {Num} ' + columnsStr +\
                f'''from {self.ordersBoardTableName} where ID = {ID} order by row asc, Time desc
                '''
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
                    resultDict[thisKey] = resultDict[thisKey][::-1]
            data[ID] = resultDict

        return data

    # Mock Online**************************

    def read_saved_days(self, ID= None) -> list:
        '''returns saved days in online data table in dateTime gregorian mode'''
        self.connect()
        if ID == None:
            cmd = f"""select distinct cast(time as date) as days from {tableType.OnlineData.value}
                    group by cast(time as date) order by cast(time as date) asc"""
        else:
            cmd = f"""select distinct cast(time as date) as days from {tableType.OnlineData.value}
                    where ID = {ID} group by cast(time as date) order by cast(time as date) asc"""
        self.execute(cmd)
        result = self.fetchall()
        self.close()

        days = []
        for row in result:
            days.append(row['days'])

        return days

    def read_days(self, startDate = '1300-01-01', endDate= '1500-01-01', ID= None):
        startDate = datetime.datetime.strptime(jalali_to_gregorian(startDate), "%Y-%m-%d").date()
        endDate = datetime.datetime.strptime(jalali_to_gregorian(endDate), "%Y-%m-%d").date()
        allDays:list[datetime.date]  = self.read_saved_days(ID)
        days= []
        for day in allDays:
            if day >= startDate and day <= endDate:
                days.append(gregorian_to_jalali(day.strftime("%Y-%m-%d")))
        return days



    def read_distinct_times_of_day(self, date: str) -> list:
        '''returns distint times of day in string type'''
        self.connect()
        self.execute(f"""select distinct Time from {tableType.OnlineData.value}
                    where cast(time as date) = '{date}' order by Time asc""")
        result = self.fetchall()
        self.close()

        distinctTimes = []
        for row in result:
            distinctTimes.append(row['Time'].strftime('%Y-%m-%d %H:%M:%S.%f')[:-3])

        return distinctTimes

    def write_mockOnline_whole_day(self, date: str) -> None:
        '''writes specific day all data in MockOnlineData
        \n date in gregorian mode'''
        # onlineData
        self.connect()
        self.execute(f"""
        insert into {tableType.MockOnlineData.value} select *
        from {tableType.OnlineData.value} where cast(time as date) = '{date}'
        """) 
        self.commit()
        self.close()

    def delete_all_mockOnline_rows(self) -> None:
        '''deletes all MockOnlineData rows'''
        self.connect()
        self.execute(f"delete from {tableType.MockOnlineData.value}")
        self.commit()
        self.close()

    def write_mockOnline_days_ago(self, date: str, num: int) -> None:
        '''writes last 'num' privious days online data in mockOnlineData table.
        \n date in gregorian mode'''

        self.disable_indexes(tableType.MockOnlineData.value)

        print('\nDeleting MockOnline rows')
        self.delete_all_mockOnline_rows()
        
        if num != 0:

            daysSaved = self.read_saved_days()
            for i in range(len(daysSaved)):
                if date == daysSaved[i].strftime("%Y-%m-%d"):
                        daysToBeWritten = [daysSaved[i].strftime("%Y-%m-%d") for i in range(i-num, i)]
                        if len(daysToBeWritten) != num:
                            raise Exception('Not Enough days in db.')
                        break
            else:
                raise Exception('There is not selected date in onlineData for backTest process. ')
            


            for thisDay in daysToBeWritten:
                print(f'writing {gregorian_to_jalali(thisDay)} data in MockOnline\n')
                self.write_mockOnline_by_every_time(thisDay)

        self.enable_indexes(tableType.MockOnlineData.value)
        
    def read_onlineData_by_every_time(self, time: str) -> None:
        '''read every single time from OnlineData'''
        self.connect()
        cmd = f"select * from {tableType.OnlineData.value} where time = '{time}'"
        self.execute(cmd) 
        result = self.fetchall()
        self.close()
        
        data = {}

        for row in result:
            data[row['ID']] = {}
            for column in row:
                if column != 'ID':
                    data[row['ID']][column] = row[column]

        return data


    def read_onlineData_by_ID_and_day(self, ID: int, date: str) -> dict:
        '''read every single date from OnlineData and returns a dict. keys: distinct times, values: data'''
        self.connect()
        cmd = f"select * from {tableType.OnlineData.value} where cast(time as date) = '{date}' and ID = {ID} order by Time asc"
        self.execute(cmd) 
        result = self.fetchall()
        self.close()

        if len(result) == 0:
            return None
            
        data = {}

        data[ID] = {}

        for row in result:
            for column in row:
                if column != 'ID':
                    if column in [onlineColumns.YesterdayPrice.value, onlineColumns.MinAllowedPrice.value, onlineColumns.MaxAllowedPrice.value]:
                        data[ID][column] = row[column]
                    elif column not in data[ID]:
                        data[ID][column] = [row[column]]
                    else:
                        data[ID][column].append(row[column])
                        
        return data

    def read_onlineData_by_time_range(self, ID: int, startDate = '1300-01-01', endDate= '1500-01-01') -> dict:
        self.connect()
        cmd = f"select * from {tableType.OnlineData.value} where time between '{jalali_to_gregorian(startDate)}' and '{jalali_to_gregorian(endDate)}' and ID = {ID} order by Time asc"
        self.execute(cmd) 
        result = self.fetchall()
        self.close()

        if len(result) == 0:
            return None
            
        data = {}

        data[ID] = {}

        for row in result:
            for column in row:
                if column != 'ID':
                    if column in [onlineColumns.YesterdayPrice.value, onlineColumns.MinAllowedPrice.value, onlineColumns.MaxAllowedPrice.value]:
                        data[ID][column] = row[column]
                    elif column not in data[ID]:
                        data[ID][column] = [row[column]]
                    else:
                        data[ID][column].append(row[column])
                        
        return data







