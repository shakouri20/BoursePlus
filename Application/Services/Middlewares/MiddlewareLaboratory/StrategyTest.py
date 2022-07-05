from Domain.Enums.MarketGroups import marketGroupType
from Application.Services.ReadData.ReadOnline.MarketWatchDataHandler import marketWatchDataHandler
from Application.Services.Middlewares.MiddlewareLaboratory.PlotData import plot_daily
from Application.Services.DataProcess import backTest_data_process
from Application.Services.Middlewares.RegisterMiddlewares import *
import multiprocessing
from Application.Services.Middlewares.MiddlewareFramework.Middleware import middleware
from Application.Services.ReadData.ReadOnline.OnlineDataHandler import onlineDataHandler
import time as ti

class strategyTest():
    def __init__(self, idList, date, **middlewareArgs) -> None:
        self.tickersList = idList
        self.date = date
        # self.middlewareObject:middleware = middlewareClass
        self.middlewareArgs = middlewareArgs
        self.dataHandler = onlineDataHandler(self.tickersList)
        self.marketWatchHandler = marketWatchDataHandler([marketGroupType.TotalMarket.value])
        self.timeTickersDict = {}
        self.create_time_tickers_dict()


    def populate_tickersDict(self):
        '''Creates a dictionary from tickers list with tickers' ids as key.'''
        tickersDict = {}
        for Id in self.tickersList:
            tickersDict[Id] = {}
        return tickersDict

    def create_time_tickers_dict(self):
        for id in self.tickersList:
            # self.timeTickersDict[id] = {'Score':[], 'RealPowerDif':[],\
            #              'VolumeDif':[], 'Price':[], 'Time':[]}

            self.timeTickersDict[id] = {'FinalScore':plotData(None, None, 50),
                                        'VolumeDifScore':plotData(None, None, 50),
                                        'RealPowerDifScore':plotData(None, None, 50),
                                        'LastIndexScore':plotData(None, None, 50),
                                        'IndexMADifScore':plotData(None, None, 50),
                                        'BuyPerCapitaScore':plotData(None, None, 50),

                                        'RealPowerDif':plotData(-0.1, 3, 1),
                                        # 'Volume':plotData(None, None, None),
                                        'perCapitaBuy':plotData(0, 150, 30),
                                        'Index':plotData(-100, 100, 0),
                                        'MADif':plotData(-4, 4, 0),
                                        'Price':plotData(), 
                                        'Time':plotData()}


    def start_test(self):
        finishEventFromDataProcess = multiprocessing.Event()
        dataUpdateQueue = multiprocessing.Queue()
        parentData, childData = multiprocessing.Pipe()
        backTestDataPrcess = multiprocessing.Process(target= backTest_data_process,
                                                args= (self.date, {"1": parentData}, {"1":childData}
                                                , dataUpdateQueue, 1, finishEventFromDataProcess))
        backTestDataPrcess.start()

        modules = []
        middlewares= [
            timeCheckBuyMiddleware,
            priceCheckBuyMiddleware,
            marketLastIndexBuyMiddleware,
            marketMADifBuyMiddleware,
            realPowerDifBuyMiddleware,
            volumeDifBuyMiddleware,
            buyPerCapitaBuyMiddleware
        ]

        for item in middlewares:
            module:middleware = item(self.dataHandler,self.marketWatchHandler, self.tickersList, self.middlewareArgs)
            modules.append(module)

        counter = 0
        while True:
            tickersDict = self.populate_tickersDict()
            dataUpdateQueue.put(10)
            if finishEventFromDataProcess.is_set():
                print('Event set. Breaking')
                break
            newData = childData.recv()
            self.dataHandler.update(newData['TickersData'])
            self.marketWatchHandler.update(newData['MarketWatchData'])
            t0 = ti.perf_counter()
            for module in modules:
                if len(tickersDict.keys()) > 0:
                    print(f'Number of  tickers:\t{len(self.tickersDict.keys())}')
                    tickersDict = module.run_forward(tickersDict)
                else:
                    return

            print('Elapsed Time:\t',ti.perf_counter()-t0)

            t = 0
            # Writing results of middleware in a dictionary
            for id in self.tickersList:
                if id in tickersDict:
                    for moduleName in tickersDict[id]:
                        idScore = tickersDict[id][moduleName]
                    self.timeTickersDict[id]['Score'].data.append(idScore)

                    # Getting Data from data handler
                    realPowerDif = self.dataHandler.realPowerDif(decNum= 4, num= 1)[id][-1]
                    index = self.marketWatchHandler.lastPricePRCAverge(num= 1)[marketGroupType.TotalMarket.value][0]
                    MADif = self.marketWatchHandler.get_LastPricePRCAverge_MA_dif(1, 14 ,14)[marketGroupType.TotalMarket.value][-1]
                    volumes = self.dataHandler.clientVolumeDif(decNum= 4, num= 1)[id][-1]
                    perCapitaBuy = self.dataHandler.perCapitaBuyDif(decNum= 4, num= 1)[id][-1]
                    price = self.dataHandler.lastPricePRC(num= 1)[id][0]
                    time = self.dataHandler.time(num= 1)[id][0].strftime('%H%M%S')
                    # print(f'Time:\t{time}')
                    t = time

                    self.timeTickersDict[id]['RealPowerDif'].data.append(realPowerDif)
                    self.timeTickersDict[id]['Volume'].data.append(volumes)
                    self.timeTickersDict[id]['Index'].data.append(index)
                    self.timeTickersDict[id]['MADif'].data.append(MADif)
                    self.timeTickersDict[id]['perCapitaBuy'].data.append(perCapitaBuy)
                    self.timeTickersDict[id]['Price'].data.append(price)
                    self.timeTickersDict[id]['Time'].data.append(time)

            if int(t) > 123000:
                print('Time Passed, Exiting...')
                break
            if finishEventFromDataProcess.is_set():
                print('Event set. Breaking')
                break

        # backTestDataPrcess.join()
        backTestDataPrcess.terminate()


        
    def draw_results(self):
        for id in self.timeTickersDict:
            print(f'Id:\t{id}')
            # print(self.timeTickersDict[id].data)
            print('================================================================\n')
            plot_daily(id, self.timeTickersDict[id]['Time'], **self.timeTickersDict[id])
            userInput = input('Next ID? (y/n)')
            if userInput == 'y':
                continue
            elif userInput == 'n':
                break
            else:
                continue
        print('Exiting...')
        return

class plotData():
    def __init__(self, min=None, max=None, constLine = None) -> None:
        self.data = []
        self.min = min
        self.max = max
        self.constLine = constLine

            