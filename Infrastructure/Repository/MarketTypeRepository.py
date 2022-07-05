from Infrastructure.DbContext.DbContext import dbContext
from Domain.ImportEnums import *
from Application.Utility.DateConverter import *

class marketType_repo(dbContext):

    def __init__(self) -> None:

        # Call parent init method
        super(marketType_repo, self).__init__()

    def read_list_of_marketTypes(self) -> list:
        """ Returns list of all market types. if there is no result return None"""
        marketTypes = self.read_general('Name', table= tableType.MarketTypes.value)
        return marketTypes['Name']

    def read_marketTypeID_by_name(self, marketTypeName: str) -> int:
        """ Return Id of market type. if there is no result return None"""
        marketTypeID_dict = self.read_general('ID', 'Name', table= tableType.MarketTypes.value, filter= f"Name like '%{marketTypeName}%'")
        if marketTypeID_dict == None:
            return None
        elif len(marketTypeID_dict['ID']) > 1:
            print('select maeket type:')
            for i in range(len(marketTypeID_dict['ID'])):
                print(i+1, '\t', marketTypeID_dict['Name'][i])
            selectedIndustry = int(input())
            return marketTypeID_dict['ID'][selectedIndustry-1]
        return marketTypeID_dict['ID'][0]

    def feed_marketTypes_table(self) -> None:
        """feed MarketType table"""
        tableName = tableType.MarketTypes.value
        cmd = f'''
        DELETE FROM {tableName}
        INSERT INTO {tableName} VALUES (1, 'بورس اول اصلی')
        INSERT INTO {tableName} VALUES (2, 'بورس اول فرعی')
        INSERT INTO {tableName} VALUES (3, 'بورس دوم')
        INSERT INTO {tableName} VALUES (4, 'بورس نامعلوم')
        INSERT INTO {tableName} VALUES (5, 'فرابورس اول')
        INSERT INTO {tableName} VALUES (6, 'فرابورس دوم')
        INSERT INTO {tableName} VALUES (7, 'فرابورس سوم')
        INSERT INTO {tableName} VALUES (8, 'فرابورس پایه نارنجی')
        INSERT INTO {tableName} VALUES (9, 'فرابورس پایه زرد')
        INSERT INTO {tableName} VALUES (10, 'فرابورس پایه قرمز')
        INSERT INTO {tableName} VALUES (11, 'فرابورس کوچک و متوسط')
        INSERT INTO {tableName} VALUES (12, 'فرابورس نامعلوم')
        '''
        self.connect()
        self.execute(cmd)
        self.commit()
        self.close()
    