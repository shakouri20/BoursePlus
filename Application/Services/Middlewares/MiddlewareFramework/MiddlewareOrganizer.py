from matplotlib import pyplot as plt
from Infrastructure.Repository.TickerRepository import ticker_repo
from Application.Services.ReadData.ReadOnline.MarketWatchDataHandler import marketWatchDataHandler
from Domain.Enums.StopLossStatus import stopLossStatus
from Application.Services.Middlewares.MiddlewareFramework.StopLossAsset import stopLossAsset
from math import ceil, floor
from Application.Services.ReadData.ReadOnline.OnlineDataHandler import onlineDataHandler
from Application.Services.Middlewares.MiddlewareFramework.Middleware import middleware
from Application.Services.Middlewares.MiddlewareFramework.ExpirableMessage import expirableMessage
from Domain.ImportEnums import *
from Settings import SettingsService 
from Application.Services.Middlewares.RegisterMiddlewares import *
from Domain.Models.OrderMessageToManager import *
from Domain.Models.OrderResultMessageToStrategy import *
from Colors import bcolors
from threading import Thread
import logging
import time
import datetime

class middleware_organizer():
    '''This is the parent class for strategies including buy and sell ones. Inherit from this class and override the following methods\n
        1. generate_tickers
        2. configure
        3. get_strategy_name : Static Method '''

    def __init__(self, name):
        self.strategyName = name
        self.daysBack = None
        self.orderType = None
        self.timeSpan = None
        self.policy = None

        # Middlewares Setup
        self.middlewares = {}
        self.middlewaresNumber = 0
        self.middlewareModules:list[middleware] = []
        self.middlewaresWeight = {}
        self.middlewaresWeightsSum = 0

        # Logging setup
        operationMode = SettingsService.operation.get_runType_setting().value
        extra = {'app_name': self.strategyName, 'operationMode': operationMode}

        self.logger = logging.getLogger(__name__)
        syslog1 = logging.FileHandler('Strategy' + f'{name}'+ '.log', 'a')
        # formatter = logging.Formatter('%(asctime)s %(operationMode)s %(app_name)s %(levelname)s : %(message)s')
        formatter = logging.Formatter(' %(levelname)s :: %(message)s')
        syslog1.setFormatter(formatter)
        self.logger.setLevel(logging.WARNING)
        self.logger.addHandler(syslog1)
        # self.logger = logging.LoggerAdapter(self.logger, extra)

        # Tickers data structure setup
        self.tickersList = self.generate_tickers()
        self.tickersDict = {}
        self.continueFlag = True  #If True the startSystem function continues next loop of middlewares else it stops.
        self.minOrderScore = 0
        self.priceMargin = None

        # Data Handler
        self.dataHandler = None 
        self.marketWatchHandler = None

        # Specific to sell strategies
        self.stopLossTickers:list[stopLossAsset] = []

        # Specific to testing strategies
        self.timeTickersResult = {}

    # ====================================>> Configuration functions <<===============================
    def use_middleware(self, middlewareName, weight, **kargs):
        self.middlewares[middlewareName] = kargs
        self.middlewaresWeight[middlewareName] = weight
        return

    def set_strategy_order_type(self, _orderType):
        if isinstance(_orderType, orderType):
            self.orderType = _orderType
        else:
            raise Exception('Strategy order type is not correct.')

    def set_strategy_time_span(self, _timeSpan):
        if isinstance(_timeSpan, orderTimeSpan):
            self.timeSpan = _timeSpan
        else:
            raise Exception('Time span is not correct.')

    def set_policy(self, policy):
        self.policy = policy

    def set_minimum_order_score(self, score):
        ''' Sets the minimum score that a ticker should obtain in order to get ordered\n
            Score should be between 1 and 100. '''
        if score >= 1 and score <= 100 :
            self.minOrderScore = score
        else:
            raise Exception('minimum order score is not in interval [1,100]')

    def set_stoploss(self, stopLossMargin):
        self.stopLossMargin = stopLossMargin
    
    def set_trailing_stoploss(self, trailingStopLossMargin):
        self.trailingStopLossMargin = trailingStopLossMargin

    def set_order_price_margin(self, margin)->None:
        '''Sets maximum absolute margin percent between ticker current price and order price.\n
            Automatically adjusts for pos/neg sign.'''
        if margin > 10 or margin < 0:
            raise Exception('Provided margin is not valid!! It should be between 0 and 10 percent.')
        self.priceMargin = margin

    # ====================================>> Abstract functions <<=====================================
    def generate_groups_list(self):
        """ Returns a list of groups Ids.\n
             Override the definition in the child class."""
        return None

    def generate_tickers(self)-> list:
        """ Returns a list of tickers Ids.\n
             Override the definition in the child class."""
        raise NotImplementedError(''' 'generate_tickers' has not been implemented in child class. Define
                                        'generate_tickers' in child class and override the base class definiton.''')

    def configure(self):
        '''Configuration of child strategy should be defined here. Override in child class and configure the behaviour of strategy. '''
        raise NotImplementedError('This function should be overriden in child class!')
    
    # =====================================>> Utility functions<<======================================
    def log_data(self, time:datetime.datetime, message):
        text = time.strftime('%Y-%m-%d %H:%M:%S') + '\t' + message
        self.logger.warning(text)
        return
    
    def populate_tickersDict(self):
        '''Creates a dictionary from tickers list with tickers' ids as key.'''
        self.tickersDict = {}
        for Id in self.tickersList:
            self.tickersDict[Id] = {}
        return

    def initialize_middlewares(self):
        self.logger.info('Initializing middlewares.')
        if len(self.middlewares.keys()) == 0 :
            raise Exception('There is no middleware submitted to organizer. Please subscribe middlewares by "use_middleware" function')
        # deleting all objects in middlewareModules list
        if len(self.middlewareModules) > 0:
            for module in self.middlewareModules:
                del module
        self.middlewareModules = []
        for middlewareName in self.middlewares:
            settings = self.middlewares[middlewareName].copy()
            module = globals()[middlewareName](self.dataHandler, self.marketWatchHandler, self.tickersList, settings)
            self.middlewareModules.append(module)
            self.logger.info('middleware %s added to strategy.' % middlewareName)
        self.middlewaresNumber = len(self.middlewares)

    def send_order_to_manager(self, tickerId, assetPrice, orderPrice, score, orderQueue):
        orderMsg = orderMessageToManager()
        orderMsg.set_order_type(self.orderType)
        orderMsg.set_time_span(self.timeSpan)               
        orderMsg.set_asset_type(assetType.Stock) # Warning: assetType.Stock is hard-coded.
        orderMsg.set_order_asset_price(assetPrice)
        orderMsg.set_tickerId(tickerId)
        orderMsg.set_score(score)
        orderMsg.set_strategyName(self.strategyName)
        orderMsg.set_order_price(orderPrice)
        orderMsg.set_minimum_allowed_price(self.dataHandler.minAllowedPrice()[tickerId])
        time = self.dataHandler.time(num= 1)[tickerId][0]
        orderMsg.set_order_time(time)
        if self.policy is not None:
            orderMsg.policy = self.policy(self.marketWatchHandler.lastPricePRCAverge(num= 1)[marketGroupType.TotalMarket.value])
        # Sending to order Queue
        self.log_data(self.dataHandler.time(1,1)[tickerId][-1] ,f'Sending ticker {tickerId} to order queue.')
        print(f'Sending ticker {tickerId} to order queue.  Strategy: {self.strategyName}')
        exMessage = expirableMessage(orderMsg, 10)
        orderQueue.put(exMessage)

    def postProcess_run(self, tickersDict: dict):
        # Check if tickers dictionary is not empty
        if len(tickersDict.keys()) == 0:
            # raise Exception('Empty tickers dictionary has been sent to decision maker')
            return
        
        # Getting average of score for tickers
        weightedScoreSum = 0

        self.logger.info('Analysing output of middlewares.')
        for thisTickerId in tickersDict:
            for thisMiddlewareName in self.middlewares:
                name = self.middlewares[thisMiddlewareName]['name']
                weightedScoreSum += tickersDict[thisTickerId][name] *  self.middlewaresWeight[thisMiddlewareName]
            averageWeightedScoreSum = weightedScoreSum / self.middlewaresWeightsSum
            tickersDict[thisTickerId]['Total_Score'] = averageWeightedScoreSum
            weightedScoreSum = 0

    def run_warmup(self):
        if self.orderType == orderType.Buy:
            self.dataHandler = onlineDataHandler(self.tickersList)
            if self.generate_groups_list() is None:
                self.marketWatchHandler = None
            else:
                self.marketWatchHandler = marketWatchDataHandler(self.generate_groups_list())
        else:
            self.dataHandler = onlineDataHandler(None)
            if self.generate_groups_list() is None:
                self.marketWatchHandler = None
            else:
                self.marketWatchHandler = marketWatchDataHandler(self.generate_groups_list())

        self.logger.info('Running strategy.')
        # Checking validity of minimum buy score
        if  self.minOrderScore < 1 or self.minOrderScore > 100 :
            raise Exception('minimum order score is not in interval [1,100]')

        # Checking validity of order time span
        if not isinstance(self.timeSpan, orderTimeSpan):
            raise Exception('Time span is not set.')

        # Checking validity of order type
        if not isinstance(self.orderType, orderType):
            raise Exception('Order type is not set.')

        # Calculating sum of weights of middlewares
        weightSum = 0
        for thisMiddlewareName in self.middlewaresWeight:
            weightSum += self.middlewaresWeight[thisMiddlewareName]
        self.middlewaresWeightsSum = weightSum
        del weightSum

        # Waiting for online data update event
        print(f'{bcolors.WARNING}Waiting for Event ...{bcolors.ENDC}')
        self.initialize_middlewares()

        return

    def run_modules(self):
        for module in self.middlewareModules:
            if len(self.tickersDict.keys()) > 0:
                # print(f'Number of  ticker]s:\t{len(self.tickersDict.keys())}')
                self.tickersDict = module(self.tickersDict)
            else:
                # print('Ending running middlewares. No ticker left for analysis')
                return
        
        self.logger.info('Loop Finished.')
        self.logger.info(f'Number of final tickers:\t{len(self.tickersDict.keys())}')
        self.logger.info(self.tickersDict)
        return

    def warmup_middlewares(self):
        for module in self.middlewareModules:
            module(self.tickersDict)
        print('Warmup Done.')

    # =====================================>> Strategy Test functions<<===============================
    def test_run(self, dataUpdateQueue, dataPipe):
        time.sleep(60)
        self.create_time_tickers_dict()
        self.run_warmup()
        self.continueFlag = True
        time1 = 0
        while self.continueFlag:
            dataUpdateQueue.put(10)
            newData = dataPipe.recv()
            self.dataHandler.update(newData['TickersData'])
            self.marketWatchHandler.update(newData['MarketWatchData'])
            times = self.dataHandler.time(num= 1)
            for id in times:
                time1 = times[id][0].strftime('%H%M%S')
                break
            if int(time1) > 123000:
                print('Time Passed, Exiting...')
                break    
            # Checking Stoploss hit and trailing SL adjustment
            if self.orderType == orderType.Sell:
                self.stoploss_check()
                    
            self.populate_tickersDict()
            self.run_modules()
            self.postProcess_run(self.tickersDict)
            self.update_time_tickers_dict(self.tickersDict, self.dataHandler,\
                         self.marketWatchHandler, self.timeTickersResult)

        return

    def update_time_tickers_dict(self,tickersDict, dataHandler, marketWatchHandler, resultTickers):
        pass

    def create_time_tickers_dict(self):
        pass

    def log_test_result(self, tickersDict) -> None:
        path = 'StrategyTest.txt'
        file = open(path, 'a', encoding = 'utf-8')
        for thisTickerId in tickersDict:
            score = tickersDict[thisTickerId]['Total_Score']
            if  score >= self.minOrderScore:
                # Sending Order to manager
                file.write(text)

        file.close()
        return

    def plot_test_result(self):
        for id in self.timeTickersResult:
            print(f'Id:\t{id}')
            # print(self.timeTickersDict[id].data)
            print('================================================================\n')
            plot_strategy_daily(id, self.timeTickersResult[id]['Time'], **self.timeTickersResult[id])
            userInput = input('Next ID? (y/n)')
            if userInput == 'y':
                continue
            elif userInput == 'n':
                break
            else:
                continue
        print('Exiting...')
        return

    # =====================================>> RealTime & BackTest functions<<=========================
    def decision_maker(self, tickersDict: dict, orderQueue) -> None:
        # Deciding which tickers to order
        for thisTickerId in tickersDict:
            score = tickersDict[thisTickerId]['Total_Score']
            if  score >= self.minOrderScore:
                # Sending Order to manager
                self.logger.warning(f'Ticker info:\t{self.tickersDict[thisTickerId]}')
                self.logger.warning(f'Score is:\t{score}')
                self.send_order_to_manager(thisTickerId, self.dataHandler.lastPrice(num= 1)[thisTickerId][0],\
                                self.calculate_order_price(thisTickerId), score, orderQueue)
                # self.send_order_to_manager(thisTickerId, self.dataHandler.row1(num= 1)[onlineColumns.DemandPrice1.value][thisTickerId][0],\
                #                 self.calculate_order_price(thisTickerId), score, orderQueue)
        return

    def calculate_order_price(self, Id)-> int:
        if self.orderType == orderType.Buy:
            maxAllowedPrice = self.dataHandler.maxAllowedPrice()[Id]
            minAllowedPrice = self.dataHandler.minAllowedPrice()[Id]
            # pricePRC = self.dataHandler.lastPricePRC(num=1)[Id]       
            # supply1Price = self.dataHandler.row1[onlineColumns.SupplyPrice1.value][Id]
            # demand1Price = self.dataHandler.row1[onlineColumns.DemandPrice1][Id]
            marginPrice = minAllowedPrice * (100 + 0.5) / 100
            marginPrice = ceil(marginPrice / 10) * 10
            return floor(min(maxAllowedPrice, marginPrice))

        if self.orderType == orderType.Sell:
            minAllowedPrice = self.dataHandler.minAllowedPrice()[Id]
            marginPrice = self.dataHandler.row1(num=1)[onlineColumns.SupplyPrice1.value][Id][0]
            return max(minAllowedPrice, marginPrice)

    def run(self, dataUpdateQueue, orderQueue, dataPipe):
        self.run_warmup()
        self.continueFlag = True
        warmUp = 1
        while self.continueFlag:
            dataUpdateQueue.put(10)
            newData = dataPipe.recv()
            # print('Going...')
            self.dataHandler.update(newData['TickersData'])
            self.marketWatchHandler.update(newData['MarketWatchData'])
            # Checking Stoploss hit and trailing SL adjustment
            if self.orderType == orderType.Sell:
                self.stoploss_check()
                    
            self.populate_tickersDict()
            if warmUp < 3:
                self.warmup_middlewares()
                warmUp += 1
            else:
                # t = time.perf_counter()
                self.run_modules()
                # print('strategy:', round(time.perf_counter()-t, 2))
                self.postProcess_run(self.tickersDict)
                self.decision_maker(self.tickersDict, orderQueue)

    # =====================================>> Sell Strategy functions<<===============================
    def add_tickerId_to_strategy(self, tickerId):
        '''Adds a ticker id to list and calls middlewares to update. '''
        if not tickerId in self.tickersList:
            # inserting in list
            self.tickersList.append(tickerId)
            # calling middlewares to update
            for module in self.middlewareModules:
                module.update_tickers(self.tickersList)

    def remove_tickerId_form_strategy(self, tickerId):
        '''Removes a ticker id from list and calls middlewares to update.'''
        # inserting in list
        if tickerId in self.tickersList:
            self.tickersList.remove(tickerId)
            # calling middlewares to update
            for module in self.middlewareModules:
                module.update_tickers(self.tickersList)

    def update_tickers_list(self, newList):
        # Added tickers
        addedTickers = []
        for ticker in newList:
            if ticker not in self.tickersList:
                addedTickers.append(ticker)
                self.tickersList.append(ticker)
                price = self.dataHandler.lastPrice(num= 1)[ticker][0]
                stopLoss = price * (1 - self.stopLossMargin/100)
                SLAsset = stopLossAsset(ticker, price, stopLoss, self.trailingStopLossMargin)
                self.stopLossTickers.append(SLAsset)

        # Removed tickers
        removedTickers = []
        for ticker in self.tickersList:
            if ticker not in newList:
                removedTickers.append(ticker)
                for asset in self.stopLossTickers:
                    if asset.get_tickerId() == ticker:
                        self.stopLossTickers.remove(asset)
        for ticker in removedTickers:
            self.tickersList.remove(ticker)

        if len(addedTickers) + len(removedTickers) > 0:
            for module in self.middlewareModules:
                module.update_tickers(self.tickersList)

    def stoploss_check(self):
        for asset in self.stopLossTickers:
            Id = asset.get_tickerId()
            price = self.dataHandler.lastPrice(num= 1)[Id][0]
            status = asset.get_ticker_stoploss_status(price)
            if status == stopLossStatus.Broken:
                print(f'{bcolors.WARNING}Stoploss hit. Id:{Id}\tPrice:{price}{bcolors.ENDC}')
                self.logger.warning(f'Stoploss hit. Id:{Id}\tPrice:{price}')
                self.send_order_to_manager(Id, price, self.calculate_order_price(Id), 100, orderQueue)
        return
    
    def run_manager_messanger_realTime(self, messagePipe):
        '''This function is ran in separate thread if strategy orderType is Sell. '''
        while True:
            # Receive messages from manager with pipe
            newTickersList = messagePipe.recv()
            # print('Got new ticekrs list in sell stategy.')
            self.update_tickers_list(newTickersList)
            # write to file for live watching
            path = 'SellStrategyTickers.txt'
            with open(path, 'w') as f:
                f.write('Ids in sell strategy:\n')
                for id in self.tickersList:
                    f.write(str(id) + '\n')

    def run_manager_messanger_backTest(self, messagePipe):
        '''This function is ran in separate thread if strategy orderType is Sell. '''
        while True:
            # Receive messages from manager with pipe
            msg: orderResultMessageToStrategy = messagePipe.recv()
            if not isinstance(msg, orderResultMessageToStrategy):
                continue

            # Perfrom process on message
            if msg.get_order_status() == orderStatus.Fail:
                continue
            if msg.get_time_span() != self.timeSpan:
                raise Exception('Time span conflict!! Time span of order and strategy do not match!')

            # Should be revised.
            if msg.get_order_type() == orderType.Buy:
                self.add_tickerId_to_strategy(msg.get_tickerId())
                price = msg.get_asset_price()
                stopLoss = price * (1 - self.stopLossMargin/100)
                SLAsset = stopLossAsset(msg.get_tickerId(), price, stopLoss, self.trailingStopLossMargin)
                self.stopLossTickers.append(SLAsset)
                # print(f'{msg.get_tickerId()} added to list.')
            elif msg.get_order_type() == orderType.Sell:
                self.remove_tickerId_form_strategy(msg.get_tickerId())
                for asset in self.stopLossTickers:
                    if asset.get_tickerId() == msg.get_tickerId():
                        self.stopLossTickers.remove(asset)
                        # print(f'{msg.get_tickerId()} removed from list.')

    # =====================================>> Static & Class functions<<======================================
    @staticmethod
    def get_strategy_name():
        '''Defines the name of strategy when messaging with manager. Override in child class'''
        raise NotImplementedError('This function has not been implemented. Override this function in child class.')

    @classmethod
    def start(cls, _name, orderQueue, dataUpdateQueue, dataPipe, messagePipe= None):
        time.sleep(60)
        strategyObj = cls(_name)
        strategyObj.logger.info('Configuring %s.'% _name)
        strategyObj.configure()
        # Checking whether a pipe to manager is available and running it in a separate thread
        if messagePipe is not None:
            runType = SettingsService.operation.get_runType_setting()
            if runType == runType.BackTest:
                messangerThread = Thread(target = strategyObj.run_manager_messanger_backTest,
                                            args = (messagePipe, ))
                messangerThread.start() 
            else:
                messangerThread = Thread(target = strategyObj.run_manager_messanger_realTime,
                                            args = (messagePipe, ))
                messangerThread.start() 
        
        # Running the strategy
        strategyObj.run(dataUpdateQueue, orderQueue, dataPipe)

        if messagePipe is not None:
            messangerThread.join()


def plot_strategy_daily(tickerId, time, **kargs):
    tr = ticker_repo()
    ID = tickerId

    Name = tr.read_by_ID(ID)['FarsiTicker']
    rowNum = len(kargs.keys())//2
    colNum = 2

    fig, ax = plt.subplots(rowNum, colNum, sharex=True, figsize=(20,20), num= Name) # (width, height) in inchese)

    counter = 0
    i = 0
    j = 0
    for item in kargs:
        if counter != len(kargs.keys())-1:
            ax[i][j].set_ylabel(item)
            if item == 'Price':
                ax[i][j].plot(time.data, kargs[item].data)#, color='green')
            else:
                ax[i][j].bar(time.data, kargs[item].data)#, color='green')
            if kargs[item].constLine is not None:
                ax[i][j].axhline(y= kargs[item].constLine, color='r')
            if kargs[item].min is not None:
                mini = kargs[item].min
                maxi = kargs[item].max
                ax[i][j].set_ylim(mini, maxi)
            counter += 1
            i = counter // 2
            j = counter - i *2

    fig.tight_layout()
    mng = plt.get_current_fig_manager()
    mng.window.state('zoomed')

    xline = [[0 for i in range(colNum)] for j in range(rowNum)]
    for i in range(rowNum):
        for j in range(colNum):
            yMin, yMax = ax[i][j].get_ylim()
            xline[i][j], = ax[i][j].plot([min(time.data), min(time.data)],[yMin,yMax])

    def on_click(event):
        # get the x and y pixel coords
        if event.inaxes:
            for i in range(rowNum):
                for j in range(colNum):
                    xline[i][j].set_xdata(event.xdata)
            fig.canvas.draw()
            fig.canvas.flush_events()

    fig.canvas.mpl_connect('button_press_event', on_click)

    plt.show()

    return
