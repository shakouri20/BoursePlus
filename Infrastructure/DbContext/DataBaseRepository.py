from Infrastructure.DbContext.DbSession import database_session
from Application.Utility.DateConverter import *
from Application.Utility.settingsService import get_runType_setting
from Application.Utility.General import create_ID_dict

class database_repo():
    
    # def __init__(self, readSettings = False):

    #     self.db = database_session()

    #     type = get_runType_setting()
    #     if readSettings == True and type == runType.backTest:
    #         self.onlineTableName = 'MockOnlineData'
    #         self.offlineTableName = 'MockOfflineData'
    #         self.ordersBoardTableName = 'MockOrdersBoard'
    #     else:
    #         self.onlineTableName = 'OnlineData'
    #         self.offlineTableName = 'OfflineData'
    #         self.ordersBoardTableName = 'OrdersBoard'
        
    # def connect(self):
    #     self.db.connect()
    
    # def close(self):
    #     self.db.close()
    

    # # general *************************************************************************
    # def read_general(self, *selectedColumns: str, table: str, filter: str= 'None', outPutType= 'DictList') -> dict:
    #     '''General Read of Tables. if there is no result return None. outPutType in DictDict or DictList
    #     \n in DictDict mode main keys in IDs'''
    #     # check if 'all' exists in args
    #     if len(selectedColumns) == 1 and selectedColumns[0] == 'all':
    #         cmd = 'select *'
    #     else:
    #         cmd = 'select '
    #         for thisColumn in selectedColumns:
    #             cmd += thisColumn + ', '
    #         # remove ', ' characters from end of cmd
    #         cmd = cmd[:-2]
    #     cmd += ' from ' + table
    #     if filter != 'None':
    #         cmd += ' where ' + filter
    #     # cmd exection
    #     # print(cmd)
    #     self.db.execute(cmd)
    #     result = self.db.fetchall()
    #     if outPutType == 'DictList':
    #         resultDict = {}
    #         if len(result) == 0:
    #             return None
    #         for thisKey in result[0].keys():
    #             resultDict[thisKey] = [result[i][thisKey] for i in range(len(result))]
    #         return resultDict
    #     elif outPutType == 'DictDict':
    #         resultDict = {}
    #         for i in range(len(result)):
    #             ID = result[i]['ID']
    #             resultDict[ID] = {}
    #             for column in result[i].keys():
    #                 if column != 'ID':
    #                     resultDict[ID][column] = result[i][column]
    #         return resultDict
    #     else:
    #         return None

    # # ticker repository *************************************************************************
    # def read_list_of_tickers(self, tickerType: str = 'all', industryType: str = 'all', marketType: str = 'all') -> dict:
    #     """Returns list of tickers determined by filters as argument inclduing tickerType, marketType and industry nemes"""
    #     if tickerType == 'all' and industryType == 'all' and  marketType == 'all':
    #         filter = 'None'
    #     else:
    #         filter = f""
    #         if tickerType != 'all':
    #             tickerTypeID = self.read_tickerTypeID_by_name(tickerType)
    #             filter += f"TickerTypeID = {tickerTypeID} and "
    #         if industryType != 'all':
    #             industryTypeID = self.read_industryID_by_name(industryType)
    #             filter += f"IndustryTypeID = {industryTypeID} and "
    #         if marketType != 'all':
    #             marketTypeTypeID = self.read_marketTypeID_by_name(marketType)
    #             filter += f"MarketTypeID = {marketTypeTypeID} and "
    #         filter = filter[:-5]
    #     return self.read_general('all', table= 'Tickers', filter= filter)

    # def filter_tickerIDList_by_daysNumberTraded_and_lastTradeDate(self, IDList: list, daysNumberFilter: int = 200, lastDatefilter: str = '1400-01-01') -> list:
    #     """returns tickerIDList filtered by daysNumberTraded and lastTradeDate"""
    #     # convert lastDayFilter to gregorian datetime.date format
    #     lastDatefilter = jalali_to_gregorian(lastDatefilter)
    #     lastDatefilter = datetime.date(int(lastDatefilter[:4]), int(lastDatefilter[5:7]), int(lastDatefilter[8:10]))

    #     filteredIDList = []

    #     for ID in IDList:
    #         # get daysNumberTraded
    #         cmd = f'''
    #             select count(ID) as cnt from {self.offlineTableName} where ID = {ID}
    #         '''
    #         self.db.execute(cmd)
    #         daysNumberTraded = self.db.fetchall()[0]['cnt']
    #         # get lastTradeDate
    #         cmd = f'''
    #             select max(Date) as maxDate from {self.offlineTableName} where ID = {ID}
    #         '''
    #         self.db.execute(cmd)
    #         lastTradeDate = self.db.fetchall()[0]['maxDate']

    #         if daysNumberTraded > daysNumberFilter and lastTradeDate > lastDatefilter:
    #             filteredIDList.append(ID)
    #         # else:
    #         #     cmd = f'''
    #         #         select FarsiTicker from tickers where ID = {ID}
    #         #     '''
    #         #     self.db.execute(cmd)
    #         #     farsiTickre = self.db.fetchall()[0]['FarsiTicker']
    #         #     print(farsiTickre[::-1])
    #     return filteredIDList

    # def read_tickerID_by_name(self, farsiTicker: str) -> int:
    #     """ Return Id of ticker by farsi ticker. if there is no result return None"""
    #     ID_dict = self.read_general('ID', table= 'Tickers', filter= f"FarsiTicker = '{farsiTicker}'")
    #     if ID_dict == None:
    #         return None
    #     else:
    #         return ID_dict['ID'][0]

    # def read_tickerName_by_ID(self, ID: int) -> str:
    #     """ Return FarsiTicker of ticker by Id. if there is no result return None"""
    #     farsiTickerDict = self.read_general('FarsiTicker', table= 'Tickers', filter= f"ID = {ID}")
    #     if farsiTickerDict == None:
    #         return None
    #     else:
    #         return farsiTickerDict['FarsiTicker'][0]
    
    # def read_tickerInfo_by_ID(self, ID: int) -> dict:
    #     """ Return tickerInfo by Id. if there is no result return None"""
    #     return self.read_general('all', table= 'Tickers', filter= f"ID = {ID}")

    # def read_tickerID_and_tickerTypeID_by_IR(self, IR: str) -> dict:
    #     """Returns Id and tickerTypeID of ticker by it's IR. if there is no result return None"""
    #     outputDict = self.read_general('ID', 'TickerTypeID', table= 'Tickers', filter= f"IR1 = '{IR}' or IR2 = '{IR}'")
    #     if outputDict == None:
    #         return None
    #     else:
    #         outputDict['ID'] = outputDict['ID'][0]
    #         outputDict['TickerTypeID'] = outputDict['TickerTypeID'][0]
    #         return outputDict

    # def delete_all_tickers_info(self) -> None:
    #     """ Deletes all tickers from table"""
    #     self.db.execute('delete from Tickers')
    #     self.db.commit()

    # def write_tickers_info(self, tickersDataList: list) -> None:
    #     """ writes list of tickers in table"""
    #     self.db.executemany('insert into Tickers values (%d, %s, %s, %s, %s, %d, %d, %d)', tickersDataList)
    #     self.db.commit()

    # def read_list_of_tickerTypes(self) -> list:
    #     """ Returns list of all Ticker types. if there is no result return None"""
    #     tickerTypes = self.read_general('Name', table= 'TickerTypes')
    #     return tickerTypes['Name']

    # def read_tickerTypeID_by_name(self, TickerTypeName: str) -> int:
    #     """ Return Id of Ticker type. if there is no result return None"""
    #     tickerTypeID_dict = self.read_general('ID', table= 'TickerTypes', filter= f"Name like '%{TickerTypeName}%'")
    #     if tickerTypeID_dict == None:
    #         return None
    #     else:
    #         return tickerTypeID_dict['ID'][0]

    # def read_list_of_industryTypes(self) -> list:
    #     """ Returns list of all industries. if there is no result return None"""
    #     industriesDict = self.read_general('Name', table= 'industryTypes')
    #     return industriesDict['Name']

    # def read_industryID_by_name(self, industryName: str) -> int:
    #     """ Return Id of industryName. if there is no result return None"""
    #     industryID_dict = self.read_general('ID', 'Name', table= 'IndustryTypes', filter= f"Name like '%{industryName}%'")
    #     if industryID_dict == None:
    #         return None
    #     elif len(industryID_dict['ID']) > 1:
    #         print('select industry:')
    #         for i in range(len(industryID_dict['ID'])):
    #             print(i+1, '\t', industryID_dict['Name'][i])
    #         selectedIndustry = int(input())
    #         return industryID_dict['ID'][selectedIndustry-1]
    #     return industryID_dict['ID'][0]

    # def read_list_of_marketTypes(self) -> list:
    #     """ Returns list of all market types. if there is no result return None"""
    #     marketTypes = self.read_general('Name', table= 'MarketTypes')
    #     return marketTypes['Name']

    # def read_marketTypeID_by_name(self, marketTypeName: str) -> int:
    #     """ Return Id of market type. if there is no result return None"""
    #     marketTypeID_dict = self.read_general('ID', 'Name', table= 'MarketTypes', filter= f"Name like '%{marketTypeName}%'")
    #     if marketTypeID_dict == None:
    #         return None
    #     elif len(marketTypeID_dict['ID']) > 1:
    #         print('select maeket type:')
    #         for i in range(len(marketTypeID_dict['ID'])):
    #             print(i+1, '\t', marketTypeID_dict['Name'][i])
    #         selectedIndustry = int(input())
    #         return marketTypeID_dict['ID'][selectedIndustry-1]
    #     return marketTypeID_dict['ID'][0]

    # def feed_tickerTypes_table(self) -> None:
    #     """feed TickerType table"""
    #     cmd = '''
    #     DELETE FROM TickerTypes
    #     INSERT INTO TickerTypes VALUES (1, 'سهام')
    #     INSERT INTO TickerTypes VALUES (2, 'شاخص')
    #     '''
    #     self.db.execute(cmd)
    #     self.db.commit() 

    # def feed_marketTypes_table(self) -> None:
    #     """feed MarketType table"""
    #     cmd = '''
    #     DELETE FROM MarketTypes
    #     INSERT INTO MarketTypes VALUES (1, 'بورس اول اصلی')
    #     INSERT INTO MarketTypes VALUES (2, 'بورس اول فرعی')
    #     INSERT INTO MarketTypes VALUES (3, 'بورس دوم')
    #     INSERT INTO MarketTypes VALUES (4, 'بورس نامعلوم')
    #     INSERT INTO MarketTypes VALUES (5, 'فرابورس اول')
    #     INSERT INTO MarketTypes VALUES (6, 'فرابورس دوم')
    #     INSERT INTO MarketTypes VALUES (7, 'فرابورس سوم')
    #     INSERT INTO MarketTypes VALUES (8, 'فرابورس پایه نارنجی')
    #     INSERT INTO MarketTypes VALUES (9, 'فرابورس پایه زرد')
    #     INSERT INTO MarketTypes VALUES (10, 'فرابورس پایه قرمز')
    #     INSERT INTO MarketTypes VALUES (11, 'فرابورس کوچک و متوسط')
    #     INSERT INTO MarketTypes VALUES (12, 'فرابورس نامعلوم')
    #     '''
    #     self.db.execute(cmd)
    #     self.db.commit()
    
    # def feed_industryTypes_table(self) -> None:
    #     """feed IndustryType table"""
    #     cmd = '''
    #     INSERT INTO IndustryTypes VALUES (1, 'زراعت و خدمات وابسته')
    #     INSERT INTO IndustryTypes VALUES (2, 'استخراج زغال سنگ')
    #     INSERT INTO IndustryTypes VALUES (3, 'استخراج نفت گاز و خدمات جنبی جز اکتشاف')
    #     INSERT INTO IndustryTypes VALUES (4, 'استخراج کانه هاي فلزی')
    #     INSERT INTO IndustryTypes VALUES (5, 'استخراج ساير معادن')
    #     INSERT INTO IndustryTypes VALUES (6, 'منسوجات')
    #     INSERT INTO IndustryTypes VALUES (7, 'دباغی، پرداخت چرم و ساخت انواع پاپوش')
    #     INSERT INTO IndustryTypes VALUES (8, 'محصولات چوبی')
    #     INSERT INTO IndustryTypes VALUES (9, 'محصولات کاغذی')
    #     INSERT INTO IndustryTypes VALUES (10, 'انتشار، چاپ و تکثیر')
    #     INSERT INTO IndustryTypes VALUES (11, 'فرآورده های نفتی، کک و سوخت هسته ای')
    #     INSERT INTO IndustryTypes VALUES (12, 'لاستیک و پلاستیک')
    #     INSERT INTO IndustryTypes VALUES (13, 'تولید محصولات کامپیوتری الکترونیکی و نوری')
    #     INSERT INTO IndustryTypes VALUES (14, 'فلزات اساسی')
    #     INSERT INTO IndustryTypes VALUES (15, 'ساخت محصولات فلزی')
    #     INSERT INTO IndustryTypes VALUES (16, 'ماشین آلات و تجهیزات')
    #     INSERT INTO IndustryTypes VALUES (17, 'ماشین آلات و دستگاه های برقی')
    #     INSERT INTO IndustryTypes VALUES (18, 'ساخت دستگاه ها و وسایل ارتباطی')
    #     INSERT INTO IndustryTypes VALUES (19, 'خودرو و ساخت قطعات')
    #     INSERT INTO IndustryTypes VALUES (20, 'قند و شکر')
    #     INSERT INTO IndustryTypes VALUES (21, 'شرکت های چند رشته ای صنعتی')
    #     INSERT INTO IndustryTypes VALUES (22, 'عرضه برق، گاز، بخار و آب گرم')
    #     INSERT INTO IndustryTypes VALUES (23, 'محصولات غذایی و آشامیدنی به جز قند و شکر')
    #     INSERT INTO IndustryTypes VALUES (24, 'مواد و محصولات دارویی')
    #     INSERT INTO IndustryTypes VALUES (25, 'محصولات شیمیایی')
    #     INSERT INTO IndustryTypes VALUES (26, 'پیمانکاری صنعتی')
    #     INSERT INTO IndustryTypes VALUES (27, 'تجارت عمده فروشی به جز وسایل نقلیه موتور')
    #     INSERT INTO IndustryTypes VALUES (28, 'خرده فروشی، به استثنای وسایل نقلیه موتوری')
    #     INSERT INTO IndustryTypes VALUES (29, 'کاشی و سرامیک')
    #     INSERT INTO IndustryTypes VALUES (30, 'سیمان، آهک و گچ')
    #     INSERT INTO IndustryTypes VALUES (31, 'سایر محصولات کانی غیرفلزی')
    #     INSERT INTO IndustryTypes VALUES (32, 'هتل و رستوران')
    #     INSERT INTO IndustryTypes VALUES (33, 'سرمایه گذاری ها')
    #     INSERT INTO IndustryTypes VALUES (34, 'بانک ها و موسسات اعتباری')
    #     INSERT INTO IndustryTypes VALUES (35, 'سایر واسطه گری های مالی')
    #     INSERT INTO IndustryTypes VALUES (36, 'حمل و نقل، انبارداری و ارتباطات')
    #     INSERT INTO IndustryTypes VALUES (37, 'حمل و نقل آبی')
    #     INSERT INTO IndustryTypes VALUES (38, 'مخابرات')
    #     INSERT INTO IndustryTypes VALUES (39, 'واسطه گری های مالی و پولی')
    #     INSERT INTO IndustryTypes VALUES (40, 'بیمه و صندوق بازنشستگی به جز تامین اجتماعی')
    #     INSERT INTO IndustryTypes VALUES (41, 'فعالیت های کمکی به نهاد های مالی واسط')
    #     INSERT INTO IndustryTypes VALUES (42, 'صندوق سرمایه گذاری قابل معامله')
    #     INSERT INTO IndustryTypes VALUES (43, 'انبوه سازی، املاک و مستغلات')
    #     INSERT INTO IndustryTypes VALUES (44, 'فعالیت مهندسی، تجزیه، تحلیل و آزمایش فنی')
    #     INSERT INTO IndustryTypes VALUES (45, 'رایانه و فعالیت های وابسته به آن')
    #     INSERT INTO IndustryTypes VALUES (46, 'اطلاعات و ارتباطات')
    #     INSERT INTO IndustryTypes VALUES (47, 'خدمات فنی و مهندسی')
    #     INSERT INTO IndustryTypes VALUES (48, 'فعالیت های هنری، سرگرمی و خلاقانه')
    #     '''
    #     self.db.execute(cmd)
    #     self.db.commit()

    # offlineData repository *************************************************************************
    # def read_offline_by_farsiTicker_and_date(self, *selectedColumns: str, farsiTicker: str, fromDate = '1300-01-01', toDate = '2500-01-01', outputDateType = 'jalali') -> dict:
    #     """ Returns the reqested columns from offline table for ticker name. fromDate and toDate are optioanl."""
    #     ID = self.read_tickerID_by_name(farsiTicker)
    #     fromDate = jalali_to_gregorian(fromDate)
    #     toDate = jalali_to_gregorian(toDate)
    #     if ID == None:
    #         return None
    #     data = self.read_general(*selectedColumns, table= self.offlineTableName, filter= f"ID = {ID} and Date between '{fromDate}' and '{toDate}' order by date asc")
    #     if 'Date' in selectedColumns:
    #         if outputDateType =='jalali':
    #             data['Date'] = [gregorian_to_jalali(data['Date'][i].strftime("%Y-%m-%d")) for i in range(len(data['Date']))]
    #         elif outputDateType =='gregorian':
    #             data['Date'] = [data['Date'][i].strftime("%Y-%m-%d") for i in range(len(data['Date']))]
    #         else:
    #             raise Exception('wrong outputDateType.')
    #     return data

    # def read_offline_by_ID_and_date(self, *selectedColumns: str, ID: int, fromDate = '1300-01-01', toDate = '2500-01-01', outputDateType = 'jalali') -> dict:
    #     """ Returns the reqested columns from offline table for specified Id. fromDate and toDate are optioanl."""
    #     fromDate = jalali_to_gregorian(fromDate)
    #     toDate = jalali_to_gregorian(toDate)
    #     data = self.read_general(*selectedColumns, table= self.offlineTableName, filter= f"ID = {ID} and Date between '{fromDate}' and '{toDate}' order by date asc")
    #     if 'Date' in selectedColumns:
    #         if outputDateType =='jalali':
    #             data['Date'] = [gregorian_to_jalali(data['Date'][i].strftime("%Y-%m-%d")) for i in range(len(data['Date']))]
    #         elif outputDateType =='gregorian':
    #             data['Date'] = [data['Date'][i].strftime("%Y-%m-%d") for i in range(len(data['Date']))]
    #         else:
    #             raise Exception('wrong outputDateType.')
    #     return data
        
    # def read_offline_lastDate_and_lastTodayPrice_by_ID(self, ID: int) -> dict:
    #     """ Returns the last available price and corresponding date for an Id in offline Data table """
    #     resultDict = self.read_general('top 1 Date, TodayPrice', table= self.offlineTableName, filter= f"ID = {ID} order by date desc")
    #     if resultDict == None:
    #         return None
    #     outputDict = {}
    #     outputDict['LastDate'] = resultDict['Date'][0]
    #     outputDict['LastTodayPrice'] = resultDict['TodayPrice'][0]
    #     return outputDict
    
    # def delete_offline_by_ID(self, ID: int) -> None:
    #     """ Deletes data for an Id from offline data table """
    #     self.db.execute(f"delete from OfflineData where ID = {ID}")
    #     self.db.commit()

    # def write_offlineData(self, dataList: list, isIndex: bool= False):
    #     """ Write ticker offline data in table with option that Ticker is Index or not"""
    #     if isIndex == False:
    #         cmd = 'insert into {} values (%d, %s, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d)'.format(self.offlineTableName)
    #         self.db.executemany(cmd, dataList)
    #     else:
    #         cmd = '''
    #         insert into {} (ID, Date, LowPrice, HighPrice, OpenPrice, closePrice, TodayPrice, YesterdayPrice, Volume, Value, Number)
    #         values (%d, %s, %d, %d, %d, %d, %d, %d, %d, %d, %d)
    #         '''.format(self.offlineTableName)
    #         self.db.executemany(cmd, dataList)
    #     self.db.commit()

    # def read_last_N_OfflineData(self, *selectedColumns: str, Num: int, IDList: list, outPutType = 'DictDict'):
    #     '''returns last n data'''

    #     if len(selectedColumns) == 1 and selectedColumns[0] == 'all':
    #         XcolumnsStr = '*'
    #         columnsStr = '*, '
    #     else:
    #         XcolumnsStr = 'x.ID, '
    #         for thisColumn in selectedColumns:
    #             XcolumnsStr += 'x.' + thisColumn + ', '

    #         XcolumnsStr = XcolumnsStr[:-2]

    #         columnsStr = 'ID, '
    #         for thisColumn in selectedColumns:
    #             columnsStr += thisColumn + ', '

    #     # query
    #     cmd = f'''
    #     select ''' + XcolumnsStr +\
    #     f''' from
    #     (
    #     select ''' + columnsStr +\
    #     f''' RANK() over (Partition BY ID ORDER BY Date DESC) as rank from {self.offlineTableName}
    #     where ID in {tuple(IDList)}
    #     ) x
    #     where rank <= {Num} order by ID 
    #     '''
    #     print(cmd)
        
    #     # get data
    #     self.db.execute(cmd)
    #     result = self.db.fetchall()

    #     if outPutType == 'DictDict':
    #         return create_ID_dict(result)
    #     elif outPutType == 'ListDict':
    #         return result

    # onlineData repository *************************************************************************
    # def read_online_by_ID_and_time(self, *selectedColumns: str, ID: int, fromTime, toTime) -> dict:
    #     """ Returns online data filtered by ID and time """
    #     return self.read_general(*selectedColumns, table= self.onlineTableName, filter= f"ID = {ID} and Time between '{fromTime}' and '{toTime}' order by Time asc")

    # def read_online_by_farsiTicker_and_time(self, *selectedColumns: str, tickerFarsi: str, fromTime, toTime) -> dict:
    #         """ Returns online data filtered by Farsi ticker and time """
    #         ID = self.read_tickerID_by_name(tickerFarsi)
    #         if ID == None:
    #             return None
    #         return self.read_general(*selectedColumns, table= self.onlineTableName, filter= f"ID = {ID} and Time between '{fromTime}' and '{toTime}' order by Time asc")

    # def write_onlineData(self, dataList: list):
    #     """Inserts priceData into OnlineData Table. Gets a list of tuples """
    #     cmd = 'insert into {} values (%d, %s, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d)'.format(self.onlineTableName)
    #     self.db.executemany(cmd, dataList)
    #     self.db.commit()

    # def read_online_lastData(self, *selectedColumns: str, IDList: list) -> dict:
    #     """returns last onlineData by ID list in dict that its keys is IDs and values is a dict again that Keys is selectedColumns. Do not select 'ID' column in selected columns"""
    #     lastDataDict = self.read_general(*selectedColumns, 'ID', table= self.onlineTableName, filter= f'time = (select top 1 time from OnlineData order by time desc) and ID in {tuple(IDList)}', outPutType= 'DictDict')
    #     return lastDataDict
    
    # def read_last_N_OnlineData(self, *selectedColumns: str, Num: int, IDList: list, outPutType = 'DictDict') -> dict:
    #     '''returns last n data'''

    #     if len(selectedColumns) == 1 and selectedColumns[0] == 'all':
    #         XcolumnsStr = '*'
    #         columnsStr = '*, '
    #     else:
    #         XcolumnsStr = 'x.ID, '
    #         for thisColumn in selectedColumns:
    #             XcolumnsStr += 'x.' + thisColumn + ', '

    #         XcolumnsStr = XcolumnsStr[:-2]

    #         columnsStr = 'ID, '
    #         for thisColumn in selectedColumns:
    #             columnsStr += thisColumn + ', '

    #     # query
    #     cmd = f'''
    #     select ''' + XcolumnsStr +\
    #     f''' from
    #     (
    #     select ''' + columnsStr +\
    #     f''' RANK() over (Partition BY ID ORDER BY Time DESC) as rank from {self.onlineTableName}
    #     where ID in {tuple(IDList)}
    #     ) x
    #     where rank <= {Num} order by ID 
    #     '''
        
    #     # get data
    #     self.db.execute(cmd)
    #     result = self.db.fetchall()
        
    #     if outPutType == 'DictDict':
    #         return create_ID_dict(result)
    #     elif outPutType == 'ListDict':
    #         return result

    # OrdersBoard repository *************************************************************************
    def write_OrdersBoard(self, dataList: list):
        """Inserts priceData into OnlineData Table. Gets a list of tuples """
        cmd = 'insert into {} values (%d, %s, %d, %d, %d, %d, %d, %d, %d)'.format(self.ordersBoardTableName)
        self.db.executemany(cmd, dataList)
        self.db.commit()


    # MockOfflineData repository *************************************************************************

    # def delete_MockOfflineData_all_rows(self) -> None:
    #     '''deletes all MockOfflineData rows'''
    #     self.db.execute("delete from MockOfflineData")
    #     self.db.commit()

    # def read_last_N_OfflineData_by_date(self, Num: int, IDList: list, date: str) -> list:
    #     '''returns last n offlineData as a list, date id gregorian mode'''

    #     # query
    #     cmd = f'''
    #     select * from
    #     (
    #     select *, RANK() over (Partition BY ID ORDER BY Date DESC) as rank from offlineData
    #     where ID in {tuple(IDList)} and Date < '{date}'
    #     ) x
    #     where rank <= {Num} order by ID 
    #     '''
    #     # get data
    #     self.db.execute(cmd)
    #     return self.db.fetchall()
        