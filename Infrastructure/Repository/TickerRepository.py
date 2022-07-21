from Infrastructure.DbContext.DbContext import dbContext
from Domain.ImportEnums import *
from Application.Utility.DateConverter import *
import DefaultParams
import datetime, time, json, requests


class ticker_repo(dbContext):

    def __init__(self) -> None:

        # Call parent init method
        super(ticker_repo, self).__init__()
        
    def read_list_of_tickers(self, tickerTypes: list = 'all', industryTypes: list = 'all', marketTypes: list = 'all', IPO: int = 2, outPutType= queryOutPutType.DictList) -> dict:
        """Returns list of tickers determined by filters as argument inclduing tickerType, marketType and industry names\n
        IPO = 0 - is not IPO\n
        IPO = 1 - is IPO\n
        IPO = 2 - no matter"""

        tickers: list[dict] = []
        result = self.read_general('all', table= tableType.Tickers.value, outPutType= queryOutPutType.ListDict)
        for row in result:
            if tickerTypes == 'all' or row['TickerTypeID'] in tickerTypes:
                if industryTypes == 'all' or row['IndustryTypeID'] in industryTypes:
                    if marketTypes == 'all' or row['MarketTypeID'] in marketTypes:
                        if IPO == 2 or row['isIPO'] == IPO:
                            tickers.append(row)
        # tickersDict = {}
        # for thisKey in tickers[0].keys():
        #     tickersDict[thisKey] = [tickers[i][thisKey] for i in range(len(tickers))]
        # return tickersDict

        if len(tickers) == 0:
                return None

        if outPutType == queryOutPutType.ListDict:
            return tickers
        elif outPutType == queryOutPutType.DictList:
            resultDict = {}
            for thisKey in tickers[0].keys():
                resultDict[thisKey] = [tickers[i][thisKey] for i in range(len(tickers))]
            return resultDict
        elif outPutType == queryOutPutType.DictDict:
            resultDict = {}
            for i in range(len(tickers)):
                ID = tickers[i]['ID']
                resultDict[ID] = {}
                for column in tickers[i].keys():
                    if column != 'ID':
                        resultDict[ID][column] = tickers[i][column]
            return resultDict
        else:
            raise Exception ('Wrong outPutType!')

    def read_by_ID(self, ID: int) -> dict:
        """ Return tickerInfo by Id. if there is no result return None"""
        result = self.read_general('all', table= tableType.Tickers.value, filter= f"ID = {ID}", outPutType= queryOutPutType.ListDict)
        if result == None:
            return None
        else:
            return result[0]

    def read_by_name(self, farsiTicker: str) -> dict:
        """ Return tickerInfo by farsi ticker. if there is no result return None"""
        result = self.read_general('all', table= tableType.Tickers.value, filter= f"FarsiTicker = '{farsiTicker}'", outPutType= queryOutPutType.ListDict)
        if result == None:
            return None
        else:
            return result[0]

    def read_by_IR(self, IR: str) -> dict:
        """Returns tickerInfo by it's IR. if there is no result return None"""
        result = self.read_general('all', table= tableType.Tickers.value, filter= f"IR1 = '{IR}' or IR2 = '{IR}'", outPutType= queryOutPutType.ListDict)
        if result == None:
            return None
        else:
            return result[0]

    def insert_basic_tables(self):

        self.connect()

        cmd = '''
        DELETE FROM Tickers
        DELETE FROM MarketTypes
        DELETE FROM TickerTypes
        DELETE FROM IndustryTypes
        
        INSERT INTO TickerTypes VALUES (1, 'سهام')
        INSERT INTO TickerTypes VALUES (2, 'شاخص')
        INSERT INTO TickerTypes VALUES (3, 'صندوق سهام')
        INSERT INTO TickerTypes VALUES (4, 'صندوق درآمد ثابت')

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
        self.execute(cmd)

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
        Level3 = 16

        industriesIndexesList = {
            34408080767216529: 1,
            19219679288446732: 2,
            65675836323214668: 3,
            13235969998952202: 4,
            62691002126902464: 5,
            59288237226302898: 6,
            69306841376553334: 7,
            58440550086834602: 8,
            30106839080444358: 9,
            25766336681098389: 10,
            12331083953323969: 11,
            36469751685735891: 12,

            32453344048876642: 14,
            1123534346391630: 15,
            11451389074113298: 16,
            33878047680249697: 17,
            24733701189547084: 18,
            20213770409093165: 19,
            21948907150049163: 20,
            40355846462826897: 21,
            54843635503648458: 22, 
            15508900928481581: 23,
            3615666621538524: 24,
            33626672012415176: 25,


            65986638607018835: 28,
            57616105980228781: 29,
            70077233737515808: 30,
            14651627750314021: 31,

            34295935482222451: 33,
            72002976013856737: 34,
            25163959460949732: 35,
            24187097921483699: 36,

            41867092385281437: 38,

            59105676994811497: 40,
            61985386521682984: 41,

            4654922806626448: 43,

            8900726085939949: 45,
            18780171241610744: 46,
            47233872677452574: 47

        }

        for i in range(len(str)):
            lineList = str[i].split(',')

            lineList[ID] = int(lineList[ID])
            lineList[IR1] = lineList[IR1].replace(' ', '').replace('\n', '').replace('\t', '')
            lineList[TickerFarsi] = self.convert_ar_characters(lineList[TickerFarsi]) 
            lineList[NameFarsi] = self.convert_ar_characters(lineList[NameFarsi])   
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
                #Determine market type of stocks
                if lineList[Level0] == '300':
                    TickerType = 1
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
                    TickerType = 1
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
                    TickerType = 1
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
                    TickerType = 1
                    #small businesses
                    if lineList[Level1] == 'V1' or lineList[Level1] == 'W1':
                        #small business
                        MarketType = 11
                    else:
                        #farabourse unknwon
                        MarketType = 12
                elif lineList[Level0] == '305':
                    if lineList[Level3] == '6811':
                        TickerType = 3
                    if lineList[Level3] == '6812':
                        TickerType = 4
                    
                    #sandogh
            # Index = ID means Index
            elif lineList[Index] == 'ID':
                TickerType = 2

            # write in db
            if TickerType == 1 :
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
                        INSERT INTO Tickers
                        (ID, IR1, IR2, FarsiTicker, FarsiName, TickerTypeID, MarketTypeID, IndustrytypeID) 
                        VALUES ({}, '{}', '{}', '{}', '{}', '{}', '{}', '{}')
                        '''.format(lineList[ID], lineList[IR1], lineList[IR2], lineList[TickerFarsi], \
                            lineList[NameFarsi], TickerType, MarketType, industryType)
                        self.execute(cmd)

            if TickerType == 2 or TickerType == 3 or TickerType == 4:
                if lineList[ID] in industriesIndexesList:
                    industryTypeID = industriesIndexesList[lineList[ID]]
                    cmd = '''
                    INSERT INTO Tickers
                    (ID, IR1, IR2, FarsiTicker, FarsiName, TickerTypeID, IndustryTypeID)
                    VALUES ({}, '{}', '{}', '{}', '{}', {}, {});
                    '''.format(lineList[ID], lineList[IR1], lineList[IR2], lineList[TickerFarsi], \
                        lineList[NameFarsi], TickerType, industryTypeID)    
                else:
                    cmd = '''
                        INSERT INTO Tickers
                        (ID, IR1, IR2, FarsiTicker, FarsiName, TickerTypeID)
                        VALUES ({}, '{}', '{}', '{}', '{}', {});
                        '''.format(lineList[ID], lineList[IR1], lineList[IR2], lineList[TickerFarsi], \
                            lineList[NameFarsi], TickerType)
                self.execute(cmd)

        self.commit()
        self.close()
        print('Basic Tables Inserted.\n')

    def delete_empty_tickers(self):

        # ID generator
        IDs = ticker_repo().read_list_of_tickers()['ID']

        self.connect()

        for ID in IDs:
            cmd = f'''
            select count(ID) as cnt from {tableType.OfflineData.value} where ID = {ID}
            '''
            self.execute(cmd)
            result= self.fetchall()
            thisCnt = result[0]['cnt']
            if thisCnt == 0:
                print(ID)
                cmd = f'''
                delete from {tableType.Tickers.value} where ID = {ID}
                '''
                self.execute(cmd)

        self.commit()
        self.close()

    def delete_first_days(self):

        # ID generator
        IDs = ticker_repo().read_list_of_tickers()['ID']

        self.connect()

        for ID in IDs:
            print(ID)
            # select first date
            cmd = f'''
            select top 1 Time from {tableType.OfflineData.value} where ID = {ID} order by time asc
            '''
            self.execute(cmd)
            result = self.fetchall()

            if len(result) != 0:

                date = result[0]['Time']

                # delete first date
                cmd = f'''
                delete from {tableType.OfflineData.value} where ID = {ID} and Time = '{date}'
                '''
                self.execute(cmd)
        
        self.commit()
        self.close()
    
    def delete_old_tickers(self):
        
        # ID generator
        IDs = ticker_repo().read_list_of_tickers()['ID']

        self.connect()

        for ID in IDs:
            cmd = f'''
            select max(Time) as maxTime from {tableType.OfflineData.value} where ID = {ID}
            '''
            self.execute(cmd)
            result= self.fetchall()
            
            maxTime = result[0]['maxTime']

            if maxTime < datetime.date(2018, 1, 1):
                print(ID)
                cmd = f'''
                delete from {tableType.Tickers.value} where ID = {ID}
                '''
                self.execute(cmd)
      
        self.commit()
        self.close()

    @staticmethod
    def get_asset_number(name, tickerTypeID):
        url = f"https://rahavard365.com/api/search/items/real?keyword={name}"
        while True:
            try:
                headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36'}
                response = requests.get(url, timeout=1, headers= headers)
                break
            except:
                time.sleep(2)
                pass
        data = json.loads(response.text)['data']
        for item in data:
            if item['trade_symbol'] == name:
                if tickerTypeID == 1 and item['type'] == 'سهام' or tickerTypeID == 3 and item['type'] == 'صندوق':
                    return item['entity_id']
        else:
            return None

    def write_rahavard_entity_ID(self):

        tickersData = ticker_repo().read_list_of_tickers(tickerTypes= [1, 3], outPutType= queryOutPutType.DictDict)
        IDs = list(tickersData.keys())[:]

        self.connect()

        for ID in IDs:
            print(ID)
            entityID = self.get_asset_number(tickersData[ID]['FarsiTicker'], tickersData[ID]['TickerTypeID'])
            if entityID != None:
                self.execute(f'update {tableType.Tickers.value} set RahavardEntityID = {int(entityID)} where ID = {ID}')

        self.commit()
        self.close()

# 1) insert_basic_tables
# 2) update offlineDataTable
# 3) write_isIPO_in_tickers_table
    # write_rahavard_entity_ID
# 4) delete_empty_tickers
# 5) delete_first_days
# 6) delete_old_tickers