from Application.Services.Middlewares.MiddlewareFramework.FundInfo import fundInfo
from Application.Services.Middlewares.MiddlewareFramework.ExpirableMessage import expirableMessage
from Application.Services.Middlewares.MiddlewareFramework.TradeHistory import tradeHistory
from Application.Services.Middlewares.MiddlewareFramework.Portfolio import portfolio 
from Application.Services.Middlewares.MiddlewareFramework.Asset import asset
from Application.Services.Middlewares.MiddlewareFramework.Manager import manager
from Application.Services.Middlewares.MiddlewareFramework.Position import position
from Domain.Models.OrderResultMessageToStrategy import orderResultMessageToStrategy
from Domain.Models.OrderMessageToManager import orderMessageToManager
from Domain.ImportEnums import *
from Settings import SettingsService


class backTestManager(manager):
    def __init__(self, orderQueue, messagePipes, strategiesGraph, finishEventFromDataProcess) -> None:
        super(backTestManager, self).__init__(orderQueue, messagePipes, strategiesGraph, finishEventFromDataProcess)
        self.fundInfo = fundInfo()
        self.initialize_fund_info()
        self.portfolio = portfolio()
        self.tradeHistory = tradeHistory()
        self.initialize_portfolio()

    def procude_report(self):
        print('Creating manager report...')
        data = self.tradeHistory.get_trade_history_data()
        text = '================================================================\n'
        text += f'Total Profit:{data[1]}\tTotal Trade Count:{data[2]}\tClosed Count:{data[3]}\n'
        for position in data[0]:
            text += str(position)+'\n'
        path = 'TradeReport.txt'
        file = open(path, 'w', encoding = 'utf-8')
        file.write(text)
        file.close()
        return


    def order_queue_listen(self):
        while not self.finishEvent.is_set():
            try:
                message: expirableMessage = self.orderQueue.get(timeout = 5)
                if message.is_expired():
                    continue
                order = message.get_message()
                self.logger.info("got a message in manager.")
                self.pre_process_order(order)
            except Exception as e :
                # print(e)
                continue
        self.procude_report() 
        return   

    # =================================<< Override functions >>=======================================#
    def initialize_portfolio(self):
        # initialize no asset mode for back test run
        self.fundInfo.set_all_time_span_balance_to_zero()

    def initialize_fund_info(self):
        initBalance = SettingsService.backTest.get_initial_balance()
        self.fundInfo.set_balance(initBalance)
        self.fundInfo.set_free_margin(initBalance)
        self.fundInfo.set_equity(initBalance)
        return

    def get_balance(self):
        return super().get_balance()

    def process_create_order(self, order:orderMessageToManager):
        self.logger.info(f'processing new create order. tickerId:  {order.tickerId}\
            \tstrategy name:  {order.strategyName}')
        # Check whether ordered asset is in portfolio or not
        if self.portfolio.is_order_in_portfolio(order):
            self.logger.warning("order is in portfolio. Aborting. ")
            return
        self.logger.debug("order is not in portfolio. Continuing.")
        
        # Check money available for new order
        # moneyAmount = self.get_money_amount_for_order(order.get_time_span(), order.get_asset_type())
        moneyAmount = 10 * 10**7
        if moneyAmount is None: #Not enough money is available ... aborting
            self.logger.warning("Not enough money available. Aborting.")
            return
        price = order.get_order_price()
        orderVolume = self.calculate_create_order_volume(price, moneyAmount)
        self.logger.info(f'order volume = {orderVolume}\t order price = {price} ')
        (result , update) = self.execute_create_order(order.get_tickerId(), orderVolume, price)
        # Checking results from execution and post processing
        if result == orderStatus.Fail:
            self.logger.warning("order execution failed. Aborting.")
            return
        if update == True:
            self.logger.warning("update has been returned as True => updating portfolio.")
            self.update_portfolio_from_master()
            return
        
        print(f'\n===<< Id: {order.get_tickerId()}\tPrice:{order.get_order_price()} >>===\n')
        # db = ticker_repo()
        # name:str =  db.read_by_ID(order.get_tickerId())['ID']
        # strDecoded = name.encode('utf8').decode()
        self.logger.warning(f'Buyed {order.get_tickerId()}')

        # Order status is Success and update is False => Fully completed order
        orderResultMessage = orderResultMessageToStrategy()
        orderResultMessage.set_order_type(order.get_order_type())
        orderResultMessage.set_order_status(orderStatus.Success)
        orderResultMessage.set_tickerId(order.get_tickerId())
        orderResultMessage.set_time_span(order.get_time_span())
        orderResultMessage.set_asset_price(order.get_order_asset_price())
        self.messagePipes[self.strategiesGraph[order.get_strategyName()]].send(orderResultMessage)

        _asset = asset(order.get_asset_type(), order.get_tickerId(), orderVolume,\
                        order.get_time_span(), order.get_order_type())
        self.logger.debug("order execution was succesful. updating portfolio and fund info.")
                
        # Update portfolio, fundinfo, Trade History
        _position = position()
        _position.create_position(order.get_tickerId(), order.get_strategyName(), order.get_order_type(),\
                                    order.get_time_span(), order.get_asset_type(), order.get_order_asset_price(),\
                                        orderVolume, SettingsService.trade.get_broker_fee()/100, order.get_order_time())
        self.tradeHistory.add_position_to_history(_position.get_position_id().__str__(),_position)
        self.portfolio.add_asset_to_portfolio(_asset)
        self.logger.debug('asset added to portfolio.')
        moneyAmount = order.get_order_asset_price() * orderVolume
        self.fundInfo.increase_time_span_balance(order.get_time_span(), moneyAmount)
        self.logger.debug('fund info updated.')
        return

    def execute_create_order(self, tickerId, volume, price):
        self.logger.info(f'Executing create order: tickerId:\t{tickerId}\tvolume:\t{volume}\tprice:\t{price}')
        return (orderStatus.Success , False)

    def process_terminate_order(self, order:orderMessageToManager):
        self.logger.info(f'processing new terminate order. tickerId:  {order.tickerId}\
            \tstrategy name:  {order.strategyName}')
        # Check whether ordered asset is in portfolio or not
        # Check whether ordered asset is in portfolio or not
        if not self.portfolio.is_order_in_portfolio(order):
            return
            # raise Exception('Provided order asset for being terminated is not in portfolio!!\nCan not terminate the order!')
    
        # Get asset from portfolio
        _asset = self.portfolio.get_asset_from_portfolio(order)
        price = order.get_order_price()
        orderVolume = _asset.get_amount()
        self.logger.info(f'order volume = {orderVolume}\t order price = {price} ')
        (result , update) = self.execute_terminate_order(order.get_tickerId(), orderVolume, price)
        # Checking results from execution and post processing
        if result == orderStatus.Fail:
            self.logger.warning("order execution failed. Aborting.")
            return

        if update == True:
            self.logger.warning("update has been returned as True => updating portfolio.")
            self.update_portfolio_from_master()
            return

        # Order status is Success and update is False => Fully completed order
        orderResultMessage = orderResultMessageToStrategy()
        orderResultMessage.set_order_type(order.get_order_type())
        orderResultMessage.set_order_status(orderStatus.Success)
        orderResultMessage.set_tickerId(order.get_tickerId())
        orderResultMessage.set_time_span(order.get_time_span())
        self.messagePipes[order.get_strategyName()].send(orderResultMessage)

        _asset = asset(order.get_asset_type(), order.get_tickerId(), orderVolume,\
                        order.get_time_span(), orderType.Buy)
        self.logger.debug("order execution was succesful. updating portfolio and fund info.")
                
        # Update portfolio, fundinfo, Trade History
        _position:position = self.tradeHistory.get_position_by_order(order.get_tickerId(), order.get_time_span())
        _position.terminate_position(order.get_strategyName(), order.get_order_asset_price(), orderVolume, order.get_order_time())
        profit = _position.get_profit()
        price = _position.get_start_price()
        self.portfolio.remove_asset_from_portfolio(_asset)
        self.logger.debug('asset added to portfolio.')
        moneyAmount = price * orderVolume
        self.fundInfo.decrease_time_span_balance(order.get_time_span(), moneyAmount)
        self.fundInfo.modify_balance(profit)
        self.fundInfo.set_max_time_span_balance()
        return

    def execute_terminate_order(self, tickerId, volume, price):
        self.logger.info(f'Executing terminate order: tickerId:\t{tickerId}\tvolume:\t{volume}\tprice:\t{price}')
        return (orderStatus.Success , False)

    @classmethod
    def start(cls, OrderQueue, sellStrategiesParentPipes, strategiesGraph, finishEventFromDataProcess):
        managerObj = cls(OrderQueue, sellStrategiesParentPipes, strategiesGraph, finishEventFromDataProcess)