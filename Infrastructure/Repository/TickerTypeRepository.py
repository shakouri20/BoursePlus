from Infrastructure.DbContext.DbContext import dbContext
from Domain.ImportEnums import *

class tickerType_repo(dbContext):

    def __init__(self) -> None:

        # Call parent init method
        super(tickerType_repo, self).__init__()

    def read_list_of_tickerTypes(self) -> list:
        """ Returns list of all Ticker types. if there is no result return None"""
        tickerTypes = self.read_general('Name', table= tableType.TickerTypes.value)
        return tickerTypes['Name']

    def read_tickerTypeID_by_name(self, TickerTypeName: str) -> int:
        """ Return Id of Ticker type. if there is no result return None"""
        tickerTypeID_dict = self.read_general('ID', table= tableType.TickerTypes.value, filter= f"Name like '%{TickerTypeName}%'")
        if tickerTypeID_dict == None:
            return None
        else:
            return tickerTypeID_dict['ID'][0]

    def feed_tickerTypes_table(self) -> None:
        """feed TickerType table"""
        tableName = tableType.TickerTypes.value
        cmd = f'''
        DELETE FROM {tableName}
        INSERT INTO {tableName} VALUES (1, 'سهام')
        INSERT INTO {tableName} VALUES (2, 'شاخص')
        INSERT INTO {tableName} VALUES (2, 'صندوق')
        '''.format
        self.connect()
        self.execute(cmd)
        self.commit() 
        self.close()