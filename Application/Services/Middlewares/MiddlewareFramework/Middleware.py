from Application.Services.ReadData.ReadOnline.MarketWatchDataHandler import marketWatchDataHandler
from Application.Services.ReadData.ReadOnline.OnlineDataHandler import onlineDataHandler
from Domain.ImportEnums import *
from numba import jit
from numba.types import float64, unicode_type, ListType, DictType, int64
from numba.typed import Dict, List
import time
from threading import Lock


cache = {}
def get_numba_types(type, caching:bool):
    if caching and type in cache:
        return cache[type]
        
    if type=='List':
        core_list_type = ListType(float64)
        core_list = List.empty_list(float64)

        inner_dict_type = DictType(unicode_type, core_list_type)
        inner_dict = Dict.empty(unicode_type, core_list_type)
        
        dataDict = Dict.empty(
            key_type = int64,
            value_type= inner_dict_type,)
        if caching:
            cache['List'] = (core_list, inner_dict, dataDict)
        return (core_list, inner_dict, dataDict)

    elif type == 'Float':
        inner_dict_type = DictType(unicode_type, float64)
        inner_dict = Dict.empty(unicode_type, float64)
        
        dataDict = Dict.empty(
         key_type = int64,
         value_type= inner_dict_type,)
        if caching:
            cache['Float'] = (inner_dict, dataDict)
        return (inner_dict, dataDict)

def cast_list_to_numba(numbaList, ordinaryList):
    numbaList.clear()
    for item in ordinaryList:
        numbaList.append(item)
    return numbaList

class middleware():
    '''Methods to override:\n
        1. single_ticker_calculation
        2. read_offline_data (Offline)
        3. get_online_data
        4. run_preprocess (Optional) '''

    def __init__(self, dataHandler, marketWatchHandler, mainTickersList: list, kargs):
        # self.lock = Lock()

        self.name = kargs['name']
        self.dataHandler = dataHandler
        self.marketWatchHandler = marketWatchHandler
        self.mainTickersList = mainTickersList.copy()
        # print(f'ticker count:\t{len(self.mainTickersList)}')
        self.offlineData = self.read_offline_data(mainTickersList)
        self.historyData = None if len(mainTickersList) == 0 else self.create_history_data(mainTickersList,self.dataHandler, self.marketWatchHandler)

        if 'parallelMode' in kargs:
            if kargs['parallelMode'] == True:
                self.parallelMode = True
            elif kargs['parallelMode'] == False:
                self.parallelMode = False
            else:
                raise Exception('''Could not resolve parallelMode. parallelMode can have following values:\n
                                    True\n
                                    False''')
        else:
            self.parallelMode = False #If true, the computations on the data in the 2nd step will be performed in parllel mode. else it will perform them in serial mode

        if 'noGil' in kargs:
            if kargs['noGil'] == True:
                self.noGil = True
                self.jitMode = True
            elif kargs['noGil'] == False:
                self.noGil = False
            else:
                raise Exception('''Could not resolve noGil. noGil can have following values:\n
                                    True\n
                                    False''')
        else:
            self.noGil = False #If true, the computations on the data in the 2nd step will be performed in parllel mode. else it will perform them in serial mode  

        if 'jitMode' in kargs:
            if kargs['jitMode'] == True:
                self.jitMode = True
                self.jit_single_ticker_calculation = jit(nogil = self.noGil)(self.single_ticker_calculation)
            elif kargs['jitMode'] == False:
                self.jitMode = False
            else:
                raise Exception('''Could not resolve jitMode. jitMode can have following values:\n
                                    True\n
                                    False''')
        else:
            self.jitMode = False #If true, the computations on the data in the 2nd step will be performed in parllel mode. else it will perform them in serial mode    

    def __call__(self,*args):
        result = self.run_forward(args[0])
        return result

    # Utility functions for middlewares
    def extract_id_list(self, tickersDict: dict)-> list:
        '''Returns the keys of a dictionary as a list''' 
        idList = []
        for tickerId in tickersDict:
            idList.append(tickerId)
        return idList

    # Procedure: readOfflineData -> ReadOnlineData -> Preprocess -> iterate over tickers by singleTickerCalculation
    def update_tickers(self, newMainTickersList: list):                      
        '''Used in sell strategies where list of tickers change. '''
        
        # Added tickers
        addedTickers = []
        for ticker in newMainTickersList:
            if ticker not in self.mainTickersList:
                addedTickers.append(ticker)
        if len(addedTickers)!=0:
            newHistoryData = self.create_history_data(addedTickers, self.dataHandler, self.marketWatchHandler)
            if self.historyData is None:
                self.historyData = self.create_history_data(newMainTickersList, self.dataHandler, self.marketWatchHandler)
            else:
                self.historyData.update(newHistoryData)

        # Removed tickers
        removedTickers = []
        for ticker in self.mainTickersList:
            if ticker not in newMainTickersList:
                removedTickers.append(ticker)
        self.mainTickersList = newMainTickersList.copy()
        if len(removedTickers) != 0:
            for id in removedTickers:
                try:
                    del self.historyData[id]
                except:
                    continue
        
        # updating offline date
        self.offlineData = self.read_offline_data(newMainTickersList)

    def read_offline_data(self, mainTickersList: list)-> dict:
        """reads and returns offline data for all tickers and maintains data for the whole up time of middleware.\n
            Returns None for default. To change behaviour override this in child class.\n """
        return None

    def create_history_data(self, idList:list, dataHandler:onlineDataHandler, marketWatchHandler:marketWatchDataHandler) -> dict:
        """Returns history data for all tickers and can be changed in ticker calculations.\n
            Returns None for default. To change behaviour override this in child class.\n """
        return None

    def get_online_data(self, tickersList: list, dataHandler: onlineDataHandler, marketWatchHandler:marketWatchDataHandler):
        """ Gets the online data for tickersDict using provided data handler and returns data as a dictionary.\n
            Notice!!
                This function should be overriden in child class."""
        raise NotImplementedError(''' 'get_online_data' has not been implemented in child class. Define
                                        'get_online_data' in child class and override the base class definiton.''')

    def run_preprocess(self, tickersDict, tickersFloatData, tickersListData, offlineData)-> dict:
        """This process is performed after database process and before process of single tickers.\n
           This function can be ignored at the implementation of middlewares.\n
           Override and use this function if a process on all or a part of tickers as a group is required. """
        return (tickersDict, tickersFloatData, tickersListData) 
    
    @staticmethod
    def single_ticker_calculation(tickerFloatOnlineData: dict, tickerListOnlineData:dict, tickerOfflineData: dict, tickerHistoryData:dict, tickerId:int):
        """Performs calculations on a single ticker provided with related data.
            Sholud return followings:
            1. 'delete' => 'Value' = True/False
            2. 'score' => 'Value' = numeric score of ticker\n
            Notice!!
                This function should be overriden in child class."""
        raise NotImplementedError(''' 'single_ticker_calculation' has not been implemented in child class. Define
                                        'single_ticker_calculation' in child class and override the base class definiton.''')

    def run(self, processorFunction, tickersDict:dict, tickersFloatData:dict, tickersListData:dict):
        outputTickersDict = tickersDict.copy()
        # with self.lock:
        for tickerId in tickersDict:
            tickerDict = tickersDict[tickerId]#.copy()
            # if self.historyData is None or tickerId in self.historyData:
            if (tickersFloatData is not None and tickerId in tickersFloatData) or\
                (tickersListData is not None and tickerId in tickersListData):
                if self.offlineData is None or tickerId in self.offlineData:
                    tickerFloatOnlineData = None if tickersFloatData is None else tickersFloatData[tickerId]#.copy()
                    tickerListOnlineData = None if tickersListData is None else tickersListData[tickerId]#.copy()
                    tickerOfflineData = None if self.offlineData is None else self.offlineData[tickerId]#,copy()
                    try:
                        tickerHistoryData = None if self.historyData is None else self.historyData[tickerId]#.copy()
                    except:
                        tickerHistoryData = None
                    # tickerOfflineData = self.offlineData[tickerId]#.copy()
                    # try:
                    (delete, score) = processorFunction(tickerFloatOnlineData, tickerListOnlineData, tickerOfflineData, tickerHistoryData, tickerId)
                    # except:
                    #     print(tickerId, self.name)
                    if delete:
                        # Deleting ticker from tickers dictionary
                        del outputTickersDict[tickerId]
                    elif not delete:
                        # Check if score is in range(0,100)
                        if score >= 0 and score <= 100 :
                            tickerDict[self.name] = score
                            # Replacing ticker dict in tickers dict
                            outputTickersDict[tickerId] = tickerDict.copy()
                        else:
                            raise Exception('Score out of range!! Score should be in range [0:100].')
                    else:
                        raise Exception('Undefined value for delete parameter!! delete is a boolean and accepts True/False values.')
                else: #tickerId not in data -> deleting from tickersDict
                    del outputTickersDict[tickerId]
            else: #tickerId not in data -> deleting from tickersDict
                del outputTickersDict[tickerId]

        return outputTickersDict

    def run_serial(self, tickersDict: dict, tickersFloatData:dict, tickersListData:dict)-> dict:
        ''' Runs the ticker calculation function for tickers provided in serial mode.'''
        # Check for jitMode and call run function
        if self.jitMode:
            outputTickersDict = self.run(self.jit_single_ticker_calculation, tickersDict, tickersFloatData, tickersListData)
        else:
            outputTickersDict = self.run(self.single_ticker_calculation, tickersDict, tickersFloatData, tickersListData)

        # Returning output of tickersDict
        return outputTickersDict

    def run_parallel(self, tickersDict: dict, tickersData: dict)-> dict:
        pass
        
    def run_forward(self, tickersDict: dict):
        #Initial check of tickers dictionary
        if len(tickersDict.keys()) == 0 :
            return {}

        # Running Db operation
        tickersList = self.extract_id_list(tickersDict)
        # t = time.perf_counter()
        (tickersFloatData, tickersListData) = self.get_online_data(tickersList, self.dataHandler, self.marketWatchHandler)
        # print(self.name, 'getOnlineData:', round(time.perf_counter()-t, 2))
        if tickersFloatData is None and tickersListData is None\
            or tickersFloatData is None and len(tickersListData.keys()) == 0\
                or len(tickersFloatData.keys()) == 0 and tickersListData is None\
                    or len(tickersFloatData.keys()) == 0 and len(tickersListData.keys()) == 0:
            return {}

        # Running preProcess
        (tickersDict, tickersFloatData, tickersListData) = self.run_preprocess(tickersDict, tickersFloatData, tickersListData, self.offlineData)
        if len(tickersDict.keys()) == 0 :
            return {}

        # t1 = time.perf_counter()
        #Running main process
        if self.parallelMode :
            tickersDict = self.run_parallel(tickersDict, tickersFloatData, tickersListData)
        else:
            # t = time.perf_counter()
            tickersDict = self.run_serial(tickersDict, tickersFloatData, tickersListData)
            # print(self.name, 'jit:', round(time.perf_counter()-t, 2))
        if len(tickersFloatData.keys()) == 0 and len(tickersListData.keys()) == 0 :
            return {}
        # t2 = time.perf_counter()
        # print(f'Elapsed time for calculation is:\t{round(t2-t1,2)} seconds\n')
        # Returning data to middleware organizer
        return tickersDict
