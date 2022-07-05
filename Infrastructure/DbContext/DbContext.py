from Infrastructure.DbContext.DbSession import database_session
from Application.Utility.General import create_ID_dict
from Domain.ImportEnums import *

class dbContext(database_session):

    def __init__(self) -> None:

        # Call parent init method
        super(dbContext, self).__init__()
    
    def read_general(self, *selectedColumns: str, table: tableType, filter: str= 'None', outPutType= queryOutPutType.DictList) -> dict:
        '''General Read of Tables. if there is no result return None. outPutType in ListDict or DictDict or DictList
        \n ListDict mode: every element is each query row in dict
        \n DictDict mode: {key: ID, value: {key: column, value: dataList}}
        \n DictList mode: {key: column, value: dataList}'''
        # check if 'all' exists in args
        if len(selectedColumns) == 1 and selectedColumns[0] == 'all':
            cmd = 'select *'
        else:
            cmd = 'select '
            for thisColumn in selectedColumns:
                cmd += thisColumn + ', '
            # remove ', ' characters from end of cmd
            cmd = cmd[:-2]
        cmd += ' from ' + table
        if filter != 'None':
            cmd += ' where ' + filter
        # print(cmd)
        
        # cmd exection
        self.connect()
        self.execute(cmd)
        result = self.fetchall()
        self.close()

        if len(result) == 0:
                return None

        for i in range(len(result)):
            if 'FarsiTicker' in result[i]:
                result[i]['FarsiTicker'] = self.convert_ar_characters(result[i]['FarsiTicker'])

        if outPutType == queryOutPutType.ListDict:
            return result
        elif outPutType == queryOutPutType.DictList:
            resultDict = {}
            for thisKey in result[0].keys():
                resultDict[thisKey] = [result[i][thisKey] for i in range(len(result))]
            return resultDict
        elif outPutType == queryOutPutType.DictDict:
            resultDict = {}
            for i in range(len(result)):
                ID = result[i]['ID']
                resultDict[ID] = {}
                for column in result[i].keys():
                    if column != 'ID':
                        resultDict[ID][column] = result[i][column]
            return resultDict
        else:
            raise Exception ('Wrong outPutType!')

    def read_last_N_data_rank(self, *selectedColumns: str, table: str, Num: int, IDList: list, outPutType = queryOutPutType.DictDict):
            '''returns last n data from selected table in selected outPutType format'''

            if len(selectedColumns) == 1 and selectedColumns[0] == 'all':
                XcolumnsStr = '*'
                columnsStr = '*, '
            else:
                XcolumnsStr = 'x.ID, '
                for thisColumn in selectedColumns:
                    XcolumnsStr += 'x.' + thisColumn + ', '

                XcolumnsStr = XcolumnsStr[:-2]

                columnsStr = 'ID, '
                for thisColumn in selectedColumns:
                    columnsStr += thisColumn + ', '

            # query
            cmd = f'''
            select ''' + XcolumnsStr +\
            f''' from
            (
            select ''' + columnsStr +\
            f''' RANK() over (Partition BY ID ORDER BY Time DESC) as rank from {table}
            where ID in {tuple(IDList)}
            ) x
            where rank <= {Num} order by ID 
            '''

            # get data
            self.connect()
            self.execute(cmd)
            result = self.fetchall()
            self.close()
            
            if outPutType == queryOutPutType.DictDict:
                return create_ID_dict(result)
            elif outPutType == queryOutPutType.ListDict:
                return result

    def read_last_N_data(self, *selectedColumns: str, table: str, Num: int, IDList: list, outPutType = queryOutPutType.DictDict):
            '''returns last n data from selected table in selected outPutType format'''

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
                    f'''from {table} where ID = {ID} order by Time desc
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

    def enable_indexes(self, table: tableType) -> None:
        '''enable indexes of table'''
        self.connect()
        self.execute(f'ALTER INDEX ALL ON {table} REBUILD;')
        self.close()

    def disable_indexes(self, table: tableType) -> None:
        '''disable indexes of table'''
        self.connect()
        self.execute(f'ALTER INDEX ALL ON {table} DISABLE;')
        self.close()

    def convert_ar_characters(self, input_str):
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