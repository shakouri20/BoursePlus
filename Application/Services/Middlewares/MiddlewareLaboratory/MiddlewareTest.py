from Domain.Enums.MarketGroups import marketGroupType
from Application.Services.ReadData.ReadOnline.MarketWatchDataHandler import marketWatchDataHandler
from Application.Services.Middlewares.MiddlewareLaboratory.PlotData import plot_daily
from Application.Services.DataProcess import backTest_data_process
import multiprocessing
from Application.Services.Middlewares.MiddlewareFramework.Middleware import middleware
from Application.Services.ReadData.ReadOnline.OnlineDataHandler import onlineDataHandler
import time as ti
from Domain.Enums.OnlineColumns import onlineColumns

class middlewareTest():
    def __init__(self, middlewareClass, idList, date, timeLimit, **middlewareArgs) -> None:
        self.tickersList = idList
        self.date = date
        self.timeLimit = timeLimit
        self.middlewareObject:middleware = middlewareClass
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
            self.timeTickersDict[id] = {'Score':plotData(-10, 100, 0),
                                        # 'RealPowerDif':plotData(None, None, 1),
                                        # 'MarketRealPowerDif':plotData(None, None, 1),
                                        # 'Volume':plotData(None, None, None),
                                        # 'perCapitaBuy':plotData(0, 150, 30),
                                        'Index':plotData(-100, 100, 0),
                                        # 'MADif':plotData(None, None, None),
                                        # 'Price':plotData(), 
                                        'Time':plotData()}


    def start_test(self):
        finishEventFromDataProcess = multiprocessing.Event()
        dataUpdateQueue = multiprocessing.Queue()
        parentData, childData = multiprocessing.Pipe()
        backTestDataPrcess = multiprocessing.Process(target= backTest_data_process,
                                                args= (self.date, {"1": parentData}, {"1":childData}
                                                , dataUpdateQueue, 1, finishEventFromDataProcess))
        backTestDataPrcess.start()

        module:middleware = self.middlewareObject(self.dataHandler,self.marketWatchHandler, self.tickersList, self.middlewareArgs)

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
            # t0 = ti.perf_counter()
            resultTickersDict = module.run_forward(tickersDict)
            # print('Elapsed Time:\t',ti.perf_counter()-t0)

            t = 0
            # Writing results of middleware in a dictionary
            for id in self.tickersList:
                if id in resultTickersDict:
                    for moduleName in resultTickersDict[id]:
                        idScore = resultTickersDict[id][moduleName]
                    self.timeTickersDict[id]['Score'].data.append(idScore)
                else:
                    self.timeTickersDict[id]['Score'].data.append(-10)

                # Getting Data from data handler
                if id in self.dataHandler.time(num= 1):
                    # realPowerDif = self.dataHandler.realPowerDif(decNum= 4, num= 1)[id][-1]
                    # marketRealPowerDif = self.marketWatchHandler.realPowerDif(num= 1, length= 30)[marketGroupType.TotalMarket.value][-1]
                    index = self.marketWatchHandler.lastPricePRCAverge(num= 1)[marketGroupType.TotalMarket.value][0]
                    # MADif = self.marketWatchHandler.lastPricePRCAverge_MA_dif(num= 1, maLength= 100)[marketGroupType.TotalMarket.value][-1]
                    # volumes = self.dataHandler.clientVolumeDif(decNum= 4, num= 1)[id][-1]
                    # perCapitaBuy = self.dataHandler.perCapitaBuyDif(decNum= 4, num= 1)[id][-1]
                    # price = self.dataHandler.lastPricePRC(num= 1)[id][0]
                    # price = self.dataHandler.row1(num= 1)[onlineColumns.DemandPrice1.value][id][0]
                    time1 = self.dataHandler.time(num= 1)[id][0].strftime('%H%M')
                    # print(f'Time:\t{time}')
                    t = time1

                    # self.timeTickersDict[id]['RealPowerDif'].data.append(realPowerDif)
                    # self.timeTickersDict[id]['MarketRealPowerDif'].data.append(marketRealPowerDif)
                    # self.timeTickersDict[id]['Volume'].data.append(volumes)
                    self.timeTickersDict[id]['Index'].data.append(index)
                    # self.timeTickersDict[id]['MADif'].data.append(MADif)
                    # self.timeTickersDict[id]['perCapitaBuy'].data.append(perCapitaBuy)
                    # self.timeTickersDict[id]['Price'].data.append(price)
                    self.timeTickersDict[id]['Time'].data.append(time1)

            if int(t) > self.timeLimit:
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

            