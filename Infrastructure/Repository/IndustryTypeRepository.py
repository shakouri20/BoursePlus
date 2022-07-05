from Infrastructure.DbContext.DbContext import dbContext
from Domain.ImportEnums import *

class industryType_repo(dbContext):

    def __init__(self) -> None:

        # Call parent init method
        super(industryType_repo, self).__init__()

    def read_list_of_industryTypes(self) -> list:
        """ Returns list of all industries. if there is no result return None"""
        industriesDict = self.read_general('Name', table= tableType.IndustryTypes.value)
        return industriesDict['Name']

    def read_industryID_by_name(self, industryName: str) -> int:
        """ Return Id of industryName. if there is no result return None"""
        industryID_dict = self.read_general('ID', 'Name', table= tableType.IndustryTypes.value, filter= f"Name like '%{industryName}%'")
        if industryID_dict == None:
            return None
        elif len(industryID_dict['ID']) > 1:
            print('select industry:')
            for i in range(len(industryID_dict['ID'])):
                print(i+1, '\t', industryID_dict['Name'][i])
            selectedIndustry = int(input())
            return industryID_dict['ID'][selectedIndustry-1]
        return industryID_dict['ID'][0]

    def feed_industryTypes_table(self) -> None:
        """feed IndustryType table"""
        tableName = tableType.IndustryTypes.value
        cmd = f'''
        INSERT INTO {tableName} VALUES (1, 'زراعت و خدمات وابسته')
        INSERT INTO {tableName} VALUES (2, 'استخراج زغال سنگ')
        INSERT INTO {tableName} VALUES (3, 'استخراج نفت گاز و خدمات جنبی جز اکتشاف')
        INSERT INTO {tableName} VALUES (4, 'استخراج کانه هاي فلزی')
        INSERT INTO {tableName} VALUES (5, 'استخراج ساير معادن')
        INSERT INTO {tableName} VALUES (6, 'منسوجات')
        INSERT INTO {tableName} VALUES (7, 'دباغی، پرداخت چرم و ساخت انواع پاپوش')
        INSERT INTO {tableName} VALUES (8, 'محصولات چوبی')
        INSERT INTO {tableName} VALUES (9, 'محصولات کاغذی')
        INSERT INTO {tableName} VALUES (10, 'انتشار، چاپ و تکثیر')
        INSERT INTO {tableName} VALUES (11, 'فرآورده های نفتی، کک و سوخت هسته ای')
        INSERT INTO {tableName} VALUES (12, 'لاستیک و پلاستیک')
        INSERT INTO {tableName} VALUES (13, 'تولید محصولات کامپیوتری الکترونیکی و نوری')
        INSERT INTO {tableName} VALUES (14, 'فلزات اساسی')
        INSERT INTO {tableName} VALUES (15, 'ساخت محصولات فلزی')
        INSERT INTO {tableName} VALUES (16, 'ماشین آلات و تجهیزات')
        INSERT INTO {tableName} VALUES (17, 'ماشین آلات و دستگاه های برقی')
        INSERT INTO {tableName} VALUES (18, 'ساخت دستگاه ها و وسایل ارتباطی')
        INSERT INTO {tableName} VALUES (19, 'خودرو و ساخت قطعات')
        INSERT INTO {tableName} VALUES (20, 'قند و شکر')
        INSERT INTO {tableName} VALUES (21, 'شرکت های چند رشته ای صنعتی')
        INSERT INTO {tableName} VALUES (22, 'عرضه برق، گاز، بخار و آب گرم')
        INSERT INTO {tableName} VALUES (23, 'محصولات غذایی و آشامیدنی به جز قند و شکر')
        INSERT INTO {tableName} VALUES (24, 'مواد و محصولات دارویی')
        INSERT INTO {tableName} VALUES (25, 'محصولات شیمیایی')
        INSERT INTO {tableName} VALUES (26, 'پیمانکاری صنعتی')
        INSERT INTO {tableName} VALUES (27, 'تجارت عمده فروشی به جز وسایل نقلیه موتور')
        INSERT INTO {tableName} VALUES (28, 'خرده فروشی، به استثنای وسایل نقلیه موتوری')
        INSERT INTO {tableName} VALUES (29, 'کاشی و سرامیک')
        INSERT INTO {tableName} VALUES (30, 'سیمان، آهک و گچ')
        INSERT INTO {tableName} VALUES (31, 'سایر محصولات کانی غیرفلزی')
        INSERT INTO {tableName} VALUES (32, 'هتل و رستوران')
        INSERT INTO {tableName} VALUES (33, 'سرمایه گذاری ها')
        INSERT INTO {tableName} VALUES (34, 'بانک ها و موسسات اعتباری')
        INSERT INTO {tableName} VALUES (35, 'سایر واسطه گری های مالی')
        INSERT INTO {tableName} VALUES (36, 'حمل و نقل، انبارداری و ارتباطات')
        INSERT INTO {tableName} VALUES (37, 'حمل و نقل آبی')
        INSERT INTO {tableName} VALUES (38, 'مخابرات')
        INSERT INTO {tableName} VALUES (39, 'واسطه گری های مالی و پولی')
        INSERT INTO {tableName} VALUES (40, 'بیمه و صندوق بازنشستگی به جز تامین اجتماعی')
        INSERT INTO {tableName} VALUES (41, 'فعالیت های کمکی به نهاد های مالی واسط')
        INSERT INTO {tableName} VALUES (42, 'صندوق سرمایه گذاری قابل معامله')
        INSERT INTO {tableName} VALUES (43, 'انبوه سازی، املاک و مستغلات')
        INSERT INTO {tableName} VALUES (44, 'فعالیت مهندسی، تجزیه، تحلیل و آزمایش فنی')
        INSERT INTO {tableName} VALUES (45, 'رایانه و فعالیت های وابسته به آن')
        INSERT INTO {tableName} VALUES (46, 'اطلاعات و ارتباطات')
        INSERT INTO {tableName} VALUES (47, 'خدمات فنی و مهندسی')
        INSERT INTO {tableName} VALUES (48, 'فعالیت های هنری، سرگرمی و خلاقانه')
        '''
        self.connect()
        self.execute(cmd)
        self.commit()
        self.close()