from datetime import date
import DefaultParams
from typing import List
import pymssql 
import DefaultParams
import os
from request_session import requests_retry_session
# from Old.request_session import requests_retry_session

# database connection class
#################################################################################################
class DatabaseConnection:
    def __init__(self) -> None:
        pass

    def connect(self):
        # self.conn = pymssql.connect(host= DefaultParams.host, user=DefaultParams.user, password= DefaultParams.password, database= DefaultParams.database) 
        self.conn = pymssql.connect(server= DefaultParams.server, database= DefaultParams.database)  
        self.cursor = self.conn.cursor(as_dict= True) 

    def execute(self, cmd: str):
        self.cursor.execute(cmd)

    def executemany(self, cmd: str, DataList: List):
        self.cursor.executemany(cmd, DataList)

    def commit(self):
        self.conn.commit()

    def close(self):
        self.conn.close()

    def fetchall(self):
        return self.cursor.fetchall()

# this Function removes all the existing tables and then creates the desired tables from the beginning
#################################################################################################
def CreateTables():
    
    DB= DatabaseConnection()

    DB.connect()

    # delete Foreign Keys Dependencies
    cmd = '''
    ALTER TABLE Tickers  
    DROP CONSTRAINT FK_Tickers_MarketTypes; 

    ALTER TABLE Tickers  
    DROP CONSTRAINT FK_Tickers_TickerTypes;

    ALTER TABLE Tickers  
    DROP CONSTRAINT FK_Tickers_IndustryTypes;
    '''
    DB.execute(cmd)
    print('Foreign Keys Dependencies Deleted.\n')

    # selects existing tables and then removes them
    DB.execute('SELECT * FROM information_schema.tables;')  

    cmd = ''
    for row in DB.cursor:
        cmd += 'drop table ' + row['TABLE_NAME'] + '\n'
        print(row['TABLE_NAME'], 'Table Deleted.')
    print()
    DB.execute(cmd)

    # create table TickerTypes
    cmd = '''
    SET ANSI_NULLS ON
    SET QUOTED_IDENTIFIER ON
    CREATE TABLE [dbo].[TickerTypes](
        [ID] [int] NOT NULL,
        [Name] [nvarchar](30) NOT NULL,
    CONSTRAINT [PK_TickerTypes] PRIMARY KEY CLUSTERED 
    (
        [ID] ASC
    )WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
    ) ON [PRIMARY]
    '''
    DB.execute(cmd)
    print('TickerTypes Table Created.')

    # create table MarketTypes
    cmd = '''
    SET ANSI_NULLS ON
    SET QUOTED_IDENTIFIER ON
    CREATE TABLE [dbo].[MarketTypes](
        [ID] [int] NOT NULL,
        [Name] [nvarchar](30) NOT NULL,
    CONSTRAINT [PK_MarketTypes] PRIMARY KEY CLUSTERED 
    (
        [ID] ASC
    )WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
    ) ON [PRIMARY]
    '''
    DB.execute(cmd)
    print('MarketTypes Table Created.')

    # create table IndustryTypes
    cmd = '''
    SET ANSI_NULLS ON
    SET QUOTED_IDENTIFIER ON
    CREATE TABLE [dbo].[IndustryTypes](
	    [ID] [int] NOT NULL,
	    [Name] [nvarchar](100) NOT NULL,
    CONSTRAINT [PK_IndustryTypes] PRIMARY KEY CLUSTERED 
    (
	    [ID] ASC
    )WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
    ) ON [PRIMARY]
    '''
    DB.execute(cmd)
    print('IndustryTypes Table Created.')

    # create table Tickers
    cmd = '''
    SET ANSI_NULLS ON
    SET QUOTED_IDENTIFIER ON
    CREATE TABLE [dbo].[Tickers](
        [ID] [bigint] NOT NULL,
        [IR1] [nvarchar](50) NOT NULL,
        [IR2] [nvarchar](50) NOT NULL,
        [FarsiTicker] [nvarchar](50) NOT NULL,
        [FarsiName] [nvarchar](100) NOT NULL,
        [TickerTypeID] [int] NULL,
        [MarketTypeID] [int] NULL,
        [IndustryTypeID] [int] NULL,
    CONSTRAINT [PK_Tickers] PRIMARY KEY CLUSTERED 
    (
        [ID] ASC
    )WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY],
    CONSTRAINT [IR1_Table_1] UNIQUE NONCLUSTERED 
    (
        [IR1] ASC
    )WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY],
    CONSTRAINT [IR2_Table_1] UNIQUE NONCLUSTERED 
    (
        [IR2] ASC
    )WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
    ) ON [PRIMARY]

    ALTER TABLE [dbo].[Tickers]  WITH CHECK ADD  CONSTRAINT [FK_Tickers_IndustryTypes] FOREIGN KEY([IndustryTypeID])
    REFERENCES [dbo].[IndustryTypes] ([ID])

    ALTER TABLE [dbo].[Tickers] CHECK CONSTRAINT [FK_Tickers_IndustryTypes]

    ALTER TABLE [dbo].[Tickers]  WITH CHECK ADD  CONSTRAINT [FK_Tickers_MarketTypes] FOREIGN KEY([MarketTypeID])
    REFERENCES [dbo].[MarketTypes] ([ID])

    ALTER TABLE [dbo].[Tickers] CHECK CONSTRAINT [FK_Tickers_MarketTypes]

    ALTER TABLE [dbo].[Tickers]  WITH CHECK ADD  CONSTRAINT [FK_Tickers_TickerTypes] FOREIGN KEY([TickerTypeID])
    REFERENCES [dbo].[TickerTypes] ([ID])

    ALTER TABLE [dbo].[Tickers] CHECK CONSTRAINT [FK_Tickers_TickerTypes]
    '''
    DB.execute(cmd)
    print('Tickers Table Created.')

    # create table Data
    cmd = '''
    SET ANSI_NULLS ON
    SET QUOTED_IDENTIFIER ON
    CREATE TABLE [dbo].[Data](
        [ID] [bigint] NOT NULL,
        [Date] [date] NOT NULL,
        [LowPrice] [bigint] NOT NULL,
        [HighPrice] [bigint] NOT NULL,
        [OpenPrice] [bigint] NOT NULL,
        [ClosePrice] [bigint] NOT NULL,
        [ClosePricePRC]  AS (case when [YesterdayPrice]=(0) then (0) else ((CONVERT([float],[ClosePrice])-CONVERT([float],[YesterdayPrice]))/CONVERT([float],[YesterdayPrice]))*(100) end),
        [TodayPrice] [bigint] NOT NULL,
        [TodayPricePRC]  AS (case when [YesterdayPrice]=(0) then (0) else ((CONVERT([float],[TodayPrice])-CONVERT([float],[YesterdayPrice]))/CONVERT([float],[YesterdayPrice]))*(100) end),
        [YesterdayPrice] [bigint] NOT NULL,
        [Volume] [bigint] NOT NULL,
        [Value] [bigint] NOT NULL,
        [Number] [int] NOT NULL,
        [RealBuyNumber] [int] NOT NULL,
        [CorporateBuyNumber] [int] NOT NULL,
        [RealSellNumber] [int] NOT NULL,
        [CorporateSellNumber] [int] NOT NULL,
        [RealBuyVolume] [bigint] NOT NULL,
        [CorporateBuyVolume] [bigint] NOT NULL,
        [RealSellVolume] [bigint] NOT NULL,
        [CorporateSellVolume] [bigint] NOT NULL,
        [RealBuyValue] [bigint] NOT NULL,
        [CorporateBuyValue] [bigint] NOT NULL,
        [RealSellValue] [bigint] NOT NULL,
        [CorporateSellValue] [bigint] NOT NULL,
        [RealPower]  AS (case when [RealSellNumber]=(0) OR [RealBuyNumber]=(0) OR [RealSellValue]=(0) then (1) else (CONVERT([float],[RealBuyValue])/CONVERT([float],[RealBuyNumber]))/(CONVERT([float],[RealSellValue])/CONVERT([float],[RealSellNumber])) end)
    ) ON [PRIMARY]
    ALTER TABLE [dbo].[Data] ADD  CONSTRAINT [DF_Data_RealBuyNumber]  DEFAULT ((0)) FOR [RealBuyNumber]
    ALTER TABLE [dbo].[Data] ADD  CONSTRAINT [DF_Data_CorporateBuyNumber]  DEFAULT ((0)) FOR [CorporateBuyNumber]
    ALTER TABLE [dbo].[Data] ADD  CONSTRAINT [DF_Data_RealSellNumber]  DEFAULT ((0)) FOR [RealSellNumber]
    ALTER TABLE [dbo].[Data] ADD  CONSTRAINT [DF_Data_CorporateSellNumber]  DEFAULT ((0)) FOR [CorporateSellNumber]
    ALTER TABLE [dbo].[Data] ADD  CONSTRAINT [DF_Data_RealBuyVolume]  DEFAULT ((0)) FOR [RealBuyVolume]
    ALTER TABLE [dbo].[Data] ADD  CONSTRAINT [DF_Data_CorporateBuyVolume]  DEFAULT ((0)) FOR [CorporateBuyVolume]
    ALTER TABLE [dbo].[Data] ADD  CONSTRAINT [DF_Data_RealSellVolume]  DEFAULT ((0)) FOR [RealSellVolume]
    ALTER TABLE [dbo].[Data] ADD  CONSTRAINT [DF_Data_CorporateSellVolume]  DEFAULT ((0)) FOR [CorporateSellVolume]
    ALTER TABLE [dbo].[Data] ADD  CONSTRAINT [DF_Data_RealBuyValue]  DEFAULT ((0)) FOR [RealBuyValue]
    ALTER TABLE [dbo].[Data] ADD  CONSTRAINT [DF_Data_CorporateBuyValue]  DEFAULT ((0)) FOR [CorporateBuyValue]
    ALTER TABLE [dbo].[Data] ADD  CONSTRAINT [DF_Data_RealSellValue]  DEFAULT ((0)) FOR [RealSellValue]
    ALTER TABLE [dbo].[Data] ADD  CONSTRAINT [DF_Data_CorporateSellValue]  DEFAULT ((0)) FOR [CorporateSellValue]
    '''
    DB.execute(cmd)
    print('Data Table Created.')

    # create table online data
    cmd = '''
    SET ANSI_NULLS ON
    SET QUOTED_IDENTIFIER ON
    CREATE TABLE [dbo].[OnlineData](
        [ID] [bigint] NOT NULL,
        [Time] [datetime] NOT NULL,
        [TodayPrice] [bigint] NOT NULL,
        [LastPrice] [bigint] NOT NULL,
        [LastPricePRC] [float] NOT NULL,
        [Number] [int] NOT NULL,
        [Volume] [bigint] NOT NULL,
        [RealBuyNumber] [int] NOT NULL,
        [CorporateBuyNumber] [int] NOT NULL,
        [RealBuyVolume] [bigint] NOT NULL,
        [CorporateBuyVolume] [bigint] NOT NULL,
        [RealSellNumber] [int] NOT NULL,
        [CorporateSellNumber] [int] NOT NULL,
        [RealSellVolume] [bigint] NOT NULL,
        [CorporateSellVolume] [bigint] NOT NULL
    ) ON [PRIMARY]
    '''
    DB.execute(cmd)
    print('OnlineData Table Created.')

    print()

    DB.commit()
    DB.close()


# this code insert TickertTypes, MarketTypes, IndustryTypes and Tickers Tables all values
#################################################################################################
def InsertBasicTables():

    DB = DatabaseConnection()

    DB.connect()

    cmd = '''
    DELETE FROM Tickers
    DELETE FROM MarketTypes
    DELETE FROM TickerTypes
    DELETE FROM IndustryTypes
    
    INSERT INTO TickerTypes VALUES (1, 'سهام')
    INSERT INTO TickerTypes VALUES (2, 'شاخص')

    INSERT INTO MarketTypes VALUES (1, 'بورس اول اصلی')
    INSERT INTO MarketTypes VALUES (2, 'بورس اول فرعی')
    INSERT INTO MarketTypes VALUES (3, 'بورس دوم')
    INSERT INTO MarketTypes VALUES (4, 'بورس نامعلوم')
    INSERT INTO MarketTypes VALUES (5, 'فرابورس اول')
    INSERT INTO MarketTypes VALUES (6, 'فرابورس دوم')
    INSERT INTO MarketTypes VALUES (7, 'فرابورس سوم')
    INSERT INTO MarketTypes VALUES (8, 'فرابورس پایه نارنجی')
    INSERT INTO MarketTypes VALUES (9, 'فرابورس پایه زرد')
    INSERT INTO MarketTypes VALUES (10, 'فرابورس پایه قرمز')
    INSERT INTO MarketTypes VALUES (11, 'فرابورس کوچک و متوسط')
    INSERT INTO MarketTypes VALUES (12, 'فرابورس نامعلوم')

    INSERT INTO IndustryTypes VALUES (1, 'زراعت و خدمات وابسته')
    INSERT INTO IndustryTypes VALUES (2, 'استخراج زغال سنگ')
    INSERT INTO IndustryTypes VALUES (3, 'استخراج نفت گاز و خدمات جنبی جز اکتشاف')
    INSERT INTO IndustryTypes VALUES (4, 'استخراج کانه هاي فلزی')
    INSERT INTO IndustryTypes VALUES (5, 'استخراج ساير معادن')
    INSERT INTO IndustryTypes VALUES (6, 'منسوجات')
    INSERT INTO IndustryTypes VALUES (7, 'دباغی، پرداخت چرم و ساخت انواع پاپوش')
    INSERT INTO IndustryTypes VALUES (8, 'محصولات چوبی')
    INSERT INTO IndustryTypes VALUES (9, 'محصولات کاغذی')
    INSERT INTO IndustryTypes VALUES (10, 'انتشار، چاپ و تکثیر')
    INSERT INTO IndustryTypes VALUES (11, 'فرآورده های نفتی، کک و سوخت هسته ای')
    INSERT INTO IndustryTypes VALUES (12, 'لاستیک و پلاستیک')
    INSERT INTO IndustryTypes VALUES (13, 'تولید محصولات کامپیوتری الکترونیکی و نوری')
    INSERT INTO IndustryTypes VALUES (14, 'فلزات اساسی')
    INSERT INTO IndustryTypes VALUES (15, 'ساخت محصولات فلزی')
    INSERT INTO IndustryTypes VALUES (16, 'ماشین آلات و تجهیزات')
    INSERT INTO IndustryTypes VALUES (17, 'ماشین آلات و دستگاه های برقی')
    INSERT INTO IndustryTypes VALUES (18, 'ساخت دستگاه ها و وسایل ارتباطی')
    INSERT INTO IndustryTypes VALUES (19, 'خودرو و ساخت قطعات')
    INSERT INTO IndustryTypes VALUES (20, 'قند و شکر')
    INSERT INTO IndustryTypes VALUES (21, 'شرکت های چند رشته ای صنعتی')
    INSERT INTO IndustryTypes VALUES (22, 'عرضه برق، گاز، بخار و آب گرم')
    INSERT INTO IndustryTypes VALUES (23, 'محصولات غذایی و آشامیدنی به جز قند و شکر')
    INSERT INTO IndustryTypes VALUES (24, 'مواد و محصولات دارویی')
    INSERT INTO IndustryTypes VALUES (25, 'محصولات شیمیایی')
    INSERT INTO IndustryTypes VALUES (26, 'پیمانکاری صنعتی')
    INSERT INTO IndustryTypes VALUES (27, 'تجارت عمده فروشی به جز وسایل نقلیه موتور')
    INSERT INTO IndustryTypes VALUES (28, 'خرده فروشی، به استثنای وسایل نقلیه موتوری')
    INSERT INTO IndustryTypes VALUES (29, 'کاشی و سرامیک')
    INSERT INTO IndustryTypes VALUES (30, 'سیمان، آهک و گچ')
    INSERT INTO IndustryTypes VALUES (31, 'سایر محصولات کانی غیرفلزی')
    INSERT INTO IndustryTypes VALUES (32, 'هتل و رستوران')
    INSERT INTO IndustryTypes VALUES (33, 'سرمایه گذاری ها')
    INSERT INTO IndustryTypes VALUES (34, 'بانک ها و موسسات اعتباری')
    INSERT INTO IndustryTypes VALUES (35, 'سایر واسطه گری های مالی')
    INSERT INTO IndustryTypes VALUES (36, 'حمل و نقل، انبارداری و ارتباطات')
    INSERT INTO IndustryTypes VALUES (37, 'حمل و نقل آبی')
    INSERT INTO IndustryTypes VALUES (38, 'مخابرات')
    INSERT INTO IndustryTypes VALUES (39, 'واسطه گری های مالی و پولی')
    INSERT INTO IndustryTypes VALUES (40, 'بیمه و صندوق بازنشستگی به جز تامین اجتماعی')
    INSERT INTO IndustryTypes VALUES (41, 'فعالیت های کمکی به نهاد های مالی واسط')
    INSERT INTO IndustryTypes VALUES (42, 'صندوق سرمایه گذاری قابل معامله')
    INSERT INTO IndustryTypes VALUES (43, 'انبوه سازی، املاک و مستغلات')
    INSERT INTO IndustryTypes VALUES (44, 'فعالیت مهندسی، تجزیه، تحلیل و آزمایش فنی')
    INSERT INTO IndustryTypes VALUES (45, 'رایانه و فعالیت های وابسته به آن')
    INSERT INTO IndustryTypes VALUES (46, 'اطلاعات و ارتباطات')
    INSERT INTO IndustryTypes VALUES (47, 'خدمات فنی و مهندسی')
    INSERT INTO IndustryTypes VALUES (48, 'فعالیت های هنری، سرگرمی و خلاقانه')
    '''
    DB.execute(cmd)

    # insert Tickers table
    myFile = open(DefaultParams.instrumentsPath, 'r', encoding='utf-8')
    str = myFile.readlines()

    ID = 0
    IR1 = 1
    TickerFarsi = 5
    NameFarsi = 6
    IR2 = 7
    Level1 = 12
    Index = 13
    Level2 = 14
    industry = 15
    Level0 = 17

    for i in range(len(str)):
        lineList = str[i].split(',')

        lineList[ID] = int(lineList[ID])
        lineList[IR1] = lineList[IR1].replace(' ', '').replace('\n', '').replace('\t', '')
        lineList[TickerFarsi] = convert_ar_characters(lineList[TickerFarsi]) 
        lineList[NameFarsi] = convert_ar_characters(lineList[NameFarsi])   
        lineList[IR2] = lineList[IR2].replace(' ', '').replace('\n', '').replace('\t', '')
        lineList[Level1] = lineList[Level1].replace(' ', '').replace('\n', '').replace('\t', '')    
        lineList[Index] = lineList[Index].replace(' ', '').replace('\n', '').replace('\t', '')
        lineList[Level2] = lineList[Level2].replace(' ', '').replace('\n', '').replace('\t', '')
        lineList[industry] = lineList[industry].replace(' ', '').replace('\n', '').replace('\t', '')
        lineList[Level0] = lineList[Level0].replace(' ', '').replace('\n', '').replace('\t', '')
            
        TickerType = 0
        MarketType = 0
        industryType = 0

        # Index = NO means not index
        if lineList[Index] == 'NO':
            TickerType = 1
            #Determine market type of stocks
            if lineList[Level0] == '300':
                ## market = bourse 
                ## Determining submarket
                if lineList[Level1] == 'N1':
                    # bazar 1 bourse
                    #determining asli vs. farie
                    if lineList[Level2] == '1':
                        #bazar asli
                        MarketType = 1
                    elif lineList[Level2] == '3':
                        #bazar farie
                        MarketType = 2
                elif lineList[Level1] == 'N2':
                    #bazare 2 bourse
                    MarketType = 3
                else:
                    #bazar unknwon bourse ex. shasta
                    MarketType = 4
            elif lineList[Level0] == '303':
                ## market = farabourse 
                ## Determining submarket
                if lineList[Level1] == 'Z1':
                    # Farabourse 1 2 3
                    # determining number of market farabourse
                    if lineList[Level2] == '1':
                        #farabourse 1
                        MarketType = 5
                    elif lineList[Level2] == '3':
                        #farabourse 2
                        MarketType = 6
                    elif lineList[Level2] == '5':   
                        #farabourse 3
                        MarketType = 7
                else:
                    #farabourse unknwon
                    MarketType = 12
            elif lineList[Level0] == '309':
                ## market Paye
                if lineList[Level1] == 'C1':
                    #narenji
                    MarketType = 8
                elif lineList[Level1] == 'P1':    
                    #zard
                    MarketType = 9
                elif lineList[Level1] == 'L1':      
                    #germez
                    MarketType = 10
                else:
                    #farabourse unknwon
                    MarketType = 12
            elif lineList[Level0] == '313':
                #small businesses
                if lineList[Level1] == 'V1' or lineList[Level1] == 'W1':
                    #small business
                    MarketType = 11
                else:
                    #farabourse unknwon
                    MarketType = 12
            if MarketType != 0:
            # now determining the industry
                industryDict = {'01': 1, '10': 2, '11': 3, '13': 4, '14': 5, '17': 6, '19': 7, '20': 8, '21': 9, '22': 10,\
                    '23': 11, '25': 12, '26': 13, '27': 14, '28': 15, '29': 16, '31': 17, '32': 18, '34': 19, '38': 20,\
                    '39': 21, '40': 22, '42': 23, '43': 24, '44': 25, '45': 26, '46': 27, '47': 28, '49': 29, '53': 30,\
                    '54': 31, '55': 32, '56': 33, '57': 34, '58': 35, '60': 36, '61': 37, '64': 38, '65': 39, '66': 40,\
                    '67': 41, '68': 42, '70': 43, '71': 44, '72': 45, '73': 46, '74': 47, '90': 48}
                if lineList[industry] in industryDict.keys():
                    industryType = industryDict[lineList[industry]]
                
                if industryType != 0:
                    cmd = '''
                    INSERT INTO Tickers VALUES ({}, '{}', '{}', '{}', '{}', '{}', '{}', '{}')
                    '''.format(lineList[ID], lineList[IR1], lineList[IR2], lineList[TickerFarsi], \
                        lineList[NameFarsi], TickerType, MarketType, industryType)
                    DB.execute(cmd)

        # Index = ID means Index
        elif lineList[Index] == 'ID':
            TickerType = 2
            cmd = '''
            INSERT INTO Tickers
            (ID, IR1, IR2, FarsiTicker, FarsiName, TickerTypeID)
            VALUES ({}, '{}', '{}', '{}', '{}', '{}');
            '''.format(lineList[ID], lineList[IR1], lineList[IR2], lineList[TickerFarsi], \
                lineList[NameFarsi], TickerType)
            DB.execute(cmd)
    print('Basic Tables Inserted.\n')

    DB.commit()
    DB.close()

# This function downloads the Prices of selected Instruments list with TseClient2.0 
#################################################################################################
def DownloadPrices(Instruments: List = 'all'):

    DB = DatabaseConnection()

    DB.connect()

    IDs = ''
    if Instruments == 'all':
        cmd = '''
            select ID from tickers
        ''' 
        DB.execute(cmd)

        for row in DB.cursor:
            IDs += str(row['ID']) + '\n'

        DB.commit()
    else:
        for this_ID in Instruments:
            IDs += str(this_ID) + '\n'

    # write the Ids to SelectedInstruments.csv
    path = DefaultParams.selectedInstrumentsPath
    file = open(path, 'w', encoding = 'utf-8')
    file.write(IDs)
    file.close()

    # delete all files in DownloadPath
    dir = DefaultParams.downloadPath
    for f in os.listdir(dir):
        os.remove(os.path.join(dir, f))
    print('DownLoading Files...')
    # download csv files From Tsetmc
    os.system('cmd /c "C: & cd {} & TseClient.exe fast"'.format(DefaultParams.tseClientExePath))
    print('Prices downloaded.')

# This function updates Daily Record of Data Table
#################################################################################################
def UpdateDailyRecordsOfDataTable(Instruments: List = 'all', download= True):

    DB = DatabaseConnection()

    DB.connect()

    # download the files
    if download:
        DownloadPrices(Instruments)

    # read all files
    path = DefaultParams.downloadPath

    # Prices
    PricesHeaderNum = 10

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

    # client types
    ClientHeaderNum = 13

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

    FilesList = os.listdir(path)
    Nfiles = len(os.listdir(path))

    ChangesNum = 0
    DeletedTickers = []

    for j in range(Nfiles):
        os.system('cls')
        print('Importing To SQL Server ... %.2f' % ((j+1) / Nfiles * 100), '% Completed!') 
        if FilesList[j].endswith(".csv"):
            file_path = f"{path}\{FilesList[j]}"
            myFile = open(file_path, 'r', encoding = 'utf-8')

            # find IR from file name
            IR = FilesList[j].replace('.csv', '')
            if '-a' in IR:
                IR = IR.replace('-a', '')

            # find ID from IR
            cmd = '''
            SELECT ID, TickerTypeID FROM Tickers WHERE IR1 = '{}' OR IR2 = '{}'
            '''.format(IR, IR)
            DB.execute(cmd)
            for row in DB.cursor:
                ID = row['ID']
                TickerTypeID = row['TickerTypeID']

            if TickerTypeID == 1: # Not Index
                while True:
                    try:
                        # Download ClientTypes File
                        url = r'http://www.tsetmc.com/tsev2/data/clienttype.aspx?i={}'.format(ID)
                        session = requests_retry_session()
                        response = session.get(url, timeout=5)
                        break
                    except:
                        continue

                # read ClientTypes file
                ClientTypesData = response.text.split(";")
                ClientTypesData = [row.split(",") for row in ClientTypesData]

            # read Prices file file
            PricesData = myFile.readlines()
            PricesData = [row.split(",") for row in PricesData]

            # Query for find the last date data
            cmd = '''
                SELECT Date, TodayPrice FROM Data WHERE ID = {} ORDER BY Date DESC
            '''.format(ID)
            DB.execute(cmd)

            lastDate = ''

            for row in DB.cursor:
                lastDate = row['Date']
                lastDate = lastDate.strftime("%Y-%m-%d")
                lastToadyPrice = row['TodayPrice']
                break

            firstLineNumToWrite = 1

            if lastDate != '':
                for LineNum in range(len(PricesData)-1, -1, -1):
                    if len(PricesData[LineNum]) == PricesHeaderNum:
                        tempDate = PricesData[LineNum][Date].replace(' ', '').replace('\n', '').replace('\t', '')
                        tempDate = PricesData[LineNum][Date][:4] + '-' + PricesData[LineNum][Date][4:6] + '-' + PricesData[LineNum][Date][6:8]
                        tempTodayPrice = int(float(PricesData[LineNum][TodayPrice].replace(' ', '').replace('\n', '').replace('\t', '')))
                        if lastDate == tempDate:
                            if lastToadyPrice == tempTodayPrice:
                                firstLineNumToWrite = LineNum + 1
                            else:
                                cmd = '''
                                DELETE FROM Data WHERE ID = {}
                                '''.format(ID)
                                DB.execute(cmd)
                                DeletedTickers.append(ID)
                            break

            if TickerTypeID == 1: # Not Index
                LastClientTypeLineNum = len(ClientTypesData)  

            if firstLineNumToWrite != len(PricesData):
                for LineNum in range(firstLineNumToWrite, len(PricesData)):
                    # Prices Values
                    #reform elements
                    for i in range(LowPrice, Number+1):
                        PricesData[LineNum][i] = int(float(PricesData[LineNum][i].replace(' ', '').replace('\n', '').replace('\t', '')))
                    PricesData[LineNum][Date] = PricesData[LineNum][Date].replace(' ', '').replace('\n', '').replace('\t', '')
                    PricesData[LineNum][Date] = PricesData[LineNum][Date][:4] + '-' + PricesData[LineNum][Date][4:6] + '-' + PricesData[LineNum][Date][6:8]
                    
                    foundRow = False
                    
                    if TickerTypeID == 1: # Not Index

                        # ClientTypes Values
                        for k in range(LastClientTypeLineNum-1, -1 , -1):
                            tempDate = ClientTypesData[k][Date].replace(' ', '').replace('\n', '').replace('\t', '')
                            tempDate = ClientTypesData[k][Date][:4] + '-' + ClientTypesData[k][Date][4:6] + '-' + ClientTypesData[k][Date][6:8]
                            if tempDate == PricesData[LineNum][Date]:
                                foundRow = True
                                LastClientTypeLineNum = k
                                #reform elements
                                for i in range(RealBuyNumber, CorporateSellValue+1):
                                    ClientTypesData[k][i] = int(float(ClientTypesData[k][i].replace(' ', '').replace('\n', '').replace('\t', '')))
                                break
                    # insert into Data Table
                    if foundRow == True and TickerTypeID == 1: # Not Index
                        cmd = '''
                        INSERT INTO Data VALUES ({}, '{}', {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {})
                        '''.format(ID, PricesData[LineNum][Date], PricesData[LineNum][LowPrice], PricesData[LineNum][HighPrice], PricesData[LineNum][OpenPrice], \
                            PricesData[LineNum][ClosePrice], PricesData[LineNum][TodayPrice], PricesData[LineNum][YesterdayPrice], PricesData[LineNum][Volume], \
                            PricesData[LineNum][Value], PricesData[LineNum][Number], ClientTypesData[k][RealBuyNumber], ClientTypesData[k][CorporateBuyNumber],
                            ClientTypesData[k][RealSellNumber], ClientTypesData[k][CorporateSellNumber], ClientTypesData[k][RealBuyVolume], ClientTypesData[k][CorporateBuyVolume],\
                            ClientTypesData[k][RealSellVolume], ClientTypesData[k][CorporateSellVolume], ClientTypesData[k][RealBuyValue], ClientTypesData[k][CorporateBuyValue],\
                            ClientTypesData[k][RealSellValue], ClientTypesData[k][CorporateSellValue])
                    else:
                        cmd = '''
                        INSERT INTO Data (ID, Date, LowPrice, HighPrice, OpenPrice, closePrice, TodayPrice, YesterdayPrice, Volume, Value, Number)
                        VALUES ({}, '{}', {}, {}, {}, {}, {}, {}, {}, {}, {})
                        '''.format(ID, PricesData[LineNum][Date], PricesData[LineNum][LowPrice], PricesData[LineNum][HighPrice], PricesData[LineNum][OpenPrice], \
                            PricesData[LineNum][ClosePrice], PricesData[LineNum][TodayPrice], PricesData[LineNum][YesterdayPrice], PricesData[LineNum][Volume], \
                            PricesData[LineNum][Value], PricesData[LineNum][Number])
                    ChangesNum += 1

                    DB.execute(cmd)
            myFile.close()
        
    print('Number Of Total Changes In Database:', ChangesNum)
    print(DeletedTickers)
    DB.commit()
    DB.close()

# convert Arabic Characters To Persian 
#################################################################################################
def convert_ar_characters(input_str):
    mapping = {
        'ك': 'ک',
        'دِ': 'د',
        'بِ': 'ب',
        'زِ': 'ز',
        'ذِ': 'ذ',
        'شِ': 'ش',
        'سِ': 'س',
        'ى': 'ی',
        'ي': 'ی'
    }
    output = ''
    keys = mapping.keys()
    for i in range(len(input_str)):
        found = False
        for key in keys:
            if input_str[i] == key:
                found = True
                output += mapping[key]
                break
        if found == False:
            output += input_str[i]    
    return output
