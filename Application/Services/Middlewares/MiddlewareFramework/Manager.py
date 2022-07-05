from Application.Services.Middlewares.MiddlewareFramework.ExpirableMessage import expirableMessage
from Application.Services.Middlewares.MiddlewareFramework.FundInfo import fundInfo
from Domain.Models.OrderResultMessageToStrategy import orderResultMessageToStrategy
from Domain.Models.Order import Order, order_validation
from Domain.ImportEnums import *
from Settings import SettingsService
from threading import Thread
import multiprocessing
from math import floor, ceil
import logging


class manager():
    '''Base class for managing and orchestrating other Processes.\n
        Functions to override in child class:
        1. initialize_portfolio
        2. initialize_fund_info
        3. get_balance
        4. update_portfolio_from_master
        5. execut_create_order
        '''

    # Logging setup
    operationMode = SettingsService.operation.get_runType_setting().value
    extra = {'operationMode': operationMode}

    logger = logging.getLogger('Manager')
    syslog = logging.FileHandler(filename='Manager.log', mode = 'a')
    formatter = logging.Formatter('%(asctime)s %(operationMode)s %(levelname)s : %(message)s')
    syslog.setFormatter(formatter)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(syslog)
    logger = logging.LoggerAdapter(logger, extra)

    def __init__(self, orderQueue, messagePipes, strategiesGraph, finishEventFromDataProcess) -> None:
        # Connections setup
        self.messagePipes:dict = messagePipes # dictionary of pipes specified by strategy Name
        self.orderQueue = orderQueue
        self.strategiesGraph = strategiesGraph
        self.finishEvent:multiprocessing.Event = finishEventFromDataProcess
        
        self.start_listen_to_queue()

    

    @order_validation
    def send_message_to_sell_strategy(self, strategyName: str, message):
        '''Sends a message to strategy specified by name through pipe messaging. '''
        if strategyName in self.messagePipes:
            self.messagePipes[strategyName].send()
        else:
            raise Exception('Strategy name not found in dictionary of pipes.')

    def get_money_amount_for_order(self, _timeSpan, _assetType):
        '''Calculates the possibility of creating order according to settings file and provided settings.\n
            If not enough money is available returns None. '''
        minBuyValue = SettingsService.trade.get_minimum_buy_value()
        # Check whether minimum money is available
        timeSpanFreeMargin = self.fundInfo.get_time_span_free_margin(_timeSpan)
        if minBuyValue > timeSpanFreeMargin:
            return None

        percentOfMajor, maxBuyValue, percentOfMinor = SettingsService.trade\
                                                        .get_trade_settings_for_order(_timeSpan, _assetType)
        balance =  self.fundInfo.get_balance()
        requiredMoney = ceil(balance * percentOfMajor/100 * percentOfMinor/100)
        
        if requiredMoney < minBuyValue:
            return minBuyValue
        elif requiredMoney > maxBuyValue:
            return min(maxBuyValue,timeSpanFreeMargin)
        else:
            return min(requiredMoney,timeSpanFreeMargin)

    #********** Procedure: order_queue_listen => pre_process_create_order => execute_order => update_portfolio & fund_info => order_queue_listen *******************************
    #*****************************************=> pre_process_terminate_order =^^
    # ==================================<< Queue Listener Functions >>=============================================== #
    def start_listen_to_queue(self):
        #  Create thread for message queue 
        self.logger.info('Creating Thread for messaging purpose with self.orderQueue.')
        queueThread = Thread(target= self.order_queue_listen)
        queueThread.start()
    
    def order_queue_listen(self):
        raise NotImplementedError('Not implemented in parent class.')     

    @order_validation
    def pre_process_order(self, order:Order):
        # Check type of order (buy: create an order, sell: end an order)
        if order.get_order_type() == orderType.Buy:
            self.process_create_order(order)
        elif order.get_order_type() == orderType.Sell:
            self.process_terminate_order(order)

    def process_create_order(self, order):
        pass

    def process_terminate_order(self, order):
        pass
    
    # =================================<< Create Order Functions >>=========================================== #
    def calculate_create_order_volume(self, price, moneyAmount):
        '''Calculates and returns the volume of order based on price and money amount.'''
        volume = floor(moneyAmount / price)
        return volume
        # return floor(volume/10) * 10

    # ==================================<< Abstract Functions >>=============================================== #
    def initialize_portfolio(self):
        self.logger.info('Initializing portfolio.')
        raise NotImplementedError('initialize portfolio has not been implemented!\nOverride this function in child class.')

    def initialize_fund_info(self):
        self.logger.info('Initializing fund info.')
        raise NotImplementedError('initialize fund info has not been implemented!\nOverride this function in child class.')

    def get_balance(self):
        '''gets the balance money. In real-time trading is the money available for trading and should 
            be obtained from trading account.\n
            In back-test mode is an imaginary amount of money available.\n
            Notice!!\n
            Override this in child class. '''

        print('Getting balance ...')
        raise NotImplementedError('get_balance is not implemented in parent class.')

    def update_portfolio_from_master(self):
        print('Updating potfolio from origin(browser ,etc.)')
        raise not NotImplementedError('update portfolio from master has not been implemented!\nOverride this function in child class.')

    def execute_create_order(self, tickerId, volume, price):
        '''Executes the create order with provided volume and price for tickerId specified.\n Override this function in child class of manager. '''
        raise NotImplementedError('This function has not been implemented!!\n inherit from manager class and implement execute_create_order.')
    
    def execute_terminate_order(self, tickerId, volume, price):
        '''Executes the terminate order with provided volume and price for tickerId specified.\n Override this function in child class of manager. '''
        raise NotImplementedError('This function has not been implemented!!\n inherit from manager class and implement execute_terminate_order.')

