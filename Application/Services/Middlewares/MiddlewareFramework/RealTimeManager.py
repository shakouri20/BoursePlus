from datetime import datetime
from Domain.Enums.PolicyResult import policyResult
from Application.Services.Middlewares.MiddlewareFramework.Policy import policy, policyGetActionResult
from math import ceil
from Application.Services.Middlewares.MiddlewareFramework.RegisteredOrder import registeredOrder
from Application.Services.Middlewares.MiddlewareFramework.ExpirableMessage import expirableMessage
from Application.Services.Middlewares.MiddlewareFramework.AgahBrokerTradeInterface import agahBrokerTradeInterface, agahOrderDetail, agahOrders
from Application.Services.Middlewares.MiddlewareFramework.RealTimePortfolio import realTimePortfolio
from Application.Services.Middlewares.MiddlewareFramework.Manager import manager
from Domain.Enums.QueryOutPutType import queryOutPutType
from Domain.Models.OrderMessageToManager import orderMessageToManager
from Domain.Enums.OrderStatus import orderStatus
from Domain.Enums.OrderType import orderType
from Infrastructure.Repository.TickerRepository import ticker_repo
from Settings import SettingsService
from threading import Thread, Lock
import requests
import time
import logging
logging.getLogger("requests").setLevel(logging.ERROR)
logging.getLogger("urllib3").setLevel(logging.ERROR)


monitor_portfo_interval = SettingsService.realTime.get_monitor_portfo_interval()

class realTimeManager(manager):
    
    def __init__(self, orderQueue, messagePipes, strategiesGraph, finishEventFromDataProcess) -> None:
        self.managerWorkFlag = Lock()
        
        self.tickers = ticker_repo().read_list_of_tickers(IPO= 2, outPutType= queryOutPutType.DictDict)
        self.portfolio = realTimePortfolio()
        self.broker = agahBrokerTradeInterface()
        time.sleep(10)
        self.initialize_fund_info()
        Thread(target= self.monitor_portfolio).start()
        super(realTimeManager, self).__init__(orderQueue, messagePipes, strategiesGraph, finishEventFromDataProcess)

    def order_queue_listen(self):
        while True:
            try:
                message: expirableMessage = self.orderQueue.get()
                if message.is_expired():
                    continue
                order = message.get_message()
                self.logger.info("got a message in manager.")
                # print(f'Got message Time: {datetime.now()}')
                self.pre_process_order(order)
                print(f'Finish Time: {datetime.now()}')
            except Exception as e :
                print('Warning!! Error at order_queue listen!!')
                print(e)
                continue
        return 

    def initialize_fund_info(self):
        self.portfolio.fundInfo.set_balance(0)
        self.portfolio.fundInfo.set_free_margin(0)
        self.portfolio.fundInfo.set_equity(0)
        self.portfolio.fundInfo.set_all_time_span_balance_to_zero()
        freeMargin = self.broker.get_account_balance()
        if freeMargin is not None:
            self.portfolio.fundInfo.set_free_margin(freeMargin)
        self.portfolio.updateLog()
        return

    def get_balance(self):
        return super().get_balance()

    def get_money_amount_for_order(self, _timeSpan, _assetType):
        '''Calculates the possibility of creating order according to settings file and provided settings.\n
            If not enough money is available returns None. '''
        minBuyValue = SettingsService.trade.get_minimum_buy_value()
        # Check whether minimum money is available
        timeSpanFreeMargin = self.portfolio.fundInfo.get_time_span_free_margin(_timeSpan)
        if minBuyValue > timeSpanFreeMargin:
            return None

        percentOfMajor, maxBuyValue, percentOfMinor = SettingsService.trade\
                                                        .get_trade_settings_for_order(_timeSpan, _assetType)
        # balance =  self.fundInfo.get_balance()
        balance =  SettingsService.realTime.get_realTime_initial_balance()
        requiredMoney = ceil(balance * percentOfMajor/100 * percentOfMinor/100)
        
        if requiredMoney < minBuyValue:
            return minBuyValue
        elif requiredMoney > maxBuyValue:
            return min(maxBuyValue,timeSpanFreeMargin)
        else:
            return min(requiredMoney,timeSpanFreeMargin)

    def process_create_order(self, order:orderMessageToManager):
        self.logger.info(f'processing new create order. tickerId:  {order.tickerId}\
            \tstrategy name:  {order.strategyName}')
        with self.managerWorkFlag:
            self.create_order(order)
        return

    def create_order(self, order:orderMessageToManager):
        # Check whether ordered asset is in portfolio or not
        if self.portfolio.is_buy_order_in_portfolio(order.get_tickerId()):
            self.logger.warning("order is in portfolio. Aborting. ")
            return
        self.logger.debug("order is not in portfolio. Continuing.")
        
        # Check money available for new order
        moneyAmount = self.get_money_amount_for_order(order.get_time_span(), order.get_asset_type())
        if moneyAmount is None: #Not enough money is available ... aborting
            self.logger.warning("Not enough money available. Aborting.")
            return
        price = order.get_order_price()
        orderVolume = self.calculate_create_order_volume(price, moneyAmount)
        self.logger.info(f'order volume = {orderVolume}\t order price = {price} ')
        success = self.execute_create_order(order.get_tickerId(), orderVolume, price)
        if success:
            self.logger.warning(f'Buyed {order.get_tickerId()}')
            self.logger.debug("order execution was succesful. updating portfolio and fund info.")
            ROrder = registeredOrder(order.policy)
            ROrder.count = orderVolume
            ROrder.id = order.get_tickerId()
            ROrder.name = self.tickers[ROrder.id]['FarsiTicker']
            ROrder.minAllowedPrice = order.get_minimum_allowed_price()
            ROrder.orderStatus = orderStatus.Active
            ROrder.sellStrategyName = self.strategiesGraph[order.get_strategyName()]
            ROrder.registerPrice = order.get_order_price()
            ROrder.orderType = orderType.Buy
            ROrder.timeSpan = order.get_time_span()
            self.portfolio.add_order_to_active_buy_orders(ROrder)
            self.portfolio.updateLog()
            # moneyAmount = order.get_order_asset_price() * orderVolume
            # self.fundInfo.increase_time_span_balance(order.get_time_span(), moneyAmount)
            self.logger.debug('fund info updated.')

    def execute_create_order(self, id, volume, price):
        self.logger.info(f'Executing create order: tickerId:\t{id}\tvolume:\t{volume}\tprice:\t{price}')
        print(f'Before execution Time: {datetime.now()}')
        return (self.broker.execute_order(orderType.Buy, id, price, volume))

    def process_terminate_order(self, order:orderMessageToManager):
        self.logger.info(f'processing new terminate order. tickerId:  {order.tickerId}\
            \tstrategy name:  {order.strategyName}')
        with self.managerWorkFlag:
            self.terminate_order(order)
        return

    def terminate_order(self, order:orderMessageToManager):
        # Check whether ordered asset is in portfolio or not
        if not self.portfolio.is_buy_order_in_portfolio(order.get_tickerId()):
            print('order is not in buy portfolio!')
            return

        if self.portfolio.is_sell_order_in_portfolio(order.get_tickerId()):
            _asset:registeredOrder = self.portfolio.get_sell_order_from_active_and_partial_list_by_id(order.get_tickerId())
            _asset.policy.sell_signal_issued(order)
            # print('is_sell_signal_issued flag raised!')
            return

        # Get asset from portfolio
        _asset:registeredOrder = self.portfolio.get_buyed_asset_from_portfolio(order.get_tickerId())
        if _asset is None:
            print('Asset not found in portfolio! Aborting sell order!')
            return

        price = order.get_order_price()
        orderVolume = _asset.count
        self.logger.info(f'order volume = {orderVolume}\t order price = {price} ')
        success = self.execute_terminate_order(order.get_tickerId(), orderVolume, price)
        if success:
            self.logger.warning(f'Sell registered {order.get_tickerId()}')  
            ROrder = registeredOrder(order.policy)  
            ROrder.count = orderVolume
            ROrder.id = order.get_tickerId()
            ROrder.name = self.tickers[ROrder.id]['FarsiTicker']
            ROrder.minAllowedPrice = order.get_minimum_allowed_price()
            ROrder.orderStatus = orderStatus.Active
            ROrder.sellStrategyName = order.get_strategyName()
            ROrder.registerPrice = order.get_order_price()
            ROrder.orderType = orderType.Sell
            ROrder.timeSpan = order.get_time_span()
            self.portfolio.add_order_to_active_sell_orders(ROrder)
            self.logger.debug("order execution was succesful.")
        return success

    def execute_terminate_order(self, tickerId, volume, price):
        self.logger.info(f'Executing terminate order: tickerId:\t{tickerId}\tvolume:\t{volume}\tprice:\t{price}')
        return (self.broker.execute_order(orderType.Sell, tickerId, price, volume))

    def update_strategies(self):
        strategyTickers = {}
        for item in self.strategiesGraph:
            strategyTickers[self.strategiesGraph[item]] = []
        
        for openOrder in self.portfolio.openBuyOrders:
            strategyTickers[openOrder.sellStrategyName].append(openOrder.id)

        for sellStrategy in strategyTickers:
            self.messagePipes[sellStrategy].send(strategyTickers[sellStrategy])

    def monitor_portfolio(self):
        while True:
            time.sleep(monitor_portfo_interval)
            try:
                with self.managerWorkFlag:
                    self.logger.info("Got lock for monitoring portfolio.")
                    freeMargin = self.broker.get_account_balance()
                    if freeMargin is not None:
                        self.portfolio.fundInfo.set_free_margin(freeMargin)

                    report:agahOrders = self.broker.analyze_orders_report()
                    if report is None:
                        self.portfolio.updateLog()
                        continue
                    self.broker.lower_error_flag()
                    self.analyze_active_orders(report)   
                    self.analyze_open_orders(report)   
                    self.analyze_partial_orders(report)   
                    self.analyze_closed_orders(report)   
                    report:agahOrders = self.broker.analyze_orders_report()
                    self.trim_active_and_partial_list_of_portfolio(report)
                    self.update_strategies()
                    self.portfolio.updateLog()
                    self.logger.info("Releasing lock of monitor portfolio.")
            except Exception as e:
                print('Warning!! Error at monitor_portfolio ==> raising error flag.')
                print(e)
                self.broker.raise_error_flag()
                time.sleep(5)

    def trim_active_and_partial_list_of_portfolio(self, report:agahOrders):
        # Active Buy Orders
        portfoActiveBuyOrders:list[registeredOrder] = self.portfolio.activeBuyOrders.copy()
        for buyOrder in self.portfolio.activeBuyOrders:
            # Check wheher it is in active list of report
            for buyReport in report.activeBuyOrders:
                if buyOrder.name == buyReport.name:
                    break
            else:
                if buyOrder.has_portfo_update_time_passed():
                    portfoActiveBuyOrders.remove(buyOrder)
        # Replace trimmed list in portfolio
        self.portfolio.activeBuyOrders = portfoActiveBuyOrders

        # Partial Buy Orders
        portfoPartialBuyOrders:list[registeredOrder] = self.portfolio.partialBuyOrders.copy()
        for buyOrder in self.portfolio.partialBuyOrders:
            # Check wheher it is in active list of report
            for buyReport in report.partialSuccessBuyOrders:
                if buyOrder.name == buyReport.name:
                    break
            else:
                if buyOrder.has_portfo_update_time_passed():
                    portfoPartialBuyOrders.remove(buyOrder)
        # Replace trimmed list in portfolio
        self.portfolio.partialBuyOrders = portfoPartialBuyOrders

        # # Open Buy Orders
        # portfoOpenBuyOrders:list[registeredOrder] = self.portfolio.openBuyOrders.copy()
        # for buyOrder in self.portfolio.openBuyOrders:
        #     # Check wheher it is in open list of report
        #     for buyReport in report.openOrders:
        #         if buyOrder.name == buyReport.name:
        #             break
        #     else:
        #         if buyOrder.has_portfo_update_time_passed():
        #             portfoOpenBuyOrders.remove(buyOrder)
        # # Replace trimmed list in portfolio
        # self.portfolio.openBuyOrders = portfoOpenBuyOrders

        # Active Sell Orders
        portfoActiveSellOrders = self.portfolio.activeSellOrders.copy()
        for SellOrder in self.portfolio.activeSellOrders:
            # Check wheher it is in active list of report
            for SellReport in report.activeSellOrders:
                if SellOrder.name == SellReport.name:
                    break
            else:
                if SellOrder.has_portfo_update_time_passed():
                    portfoActiveSellOrders.remove(SellOrder)
        # Replace trimmed list in portfolio
        self.portfolio.activeSellOrders = portfoActiveSellOrders

        # Partial Sell Orders
        portfoPartialSellOrders:list[registeredOrder] = self.portfolio.partialSellOrders.copy()
        for sellOrder in self.portfolio.partialSellOrders:
            # Check wheher it is in active list of report
            for SellReport in report.partialSuccessSellOrders:
                if sellOrder.name == SellReport.name:
                    break
            else:
                if sellOrder.has_portfo_update_time_passed():
                    portfoPartialSellOrders.remove(sellOrder)
        # Replace trimmed list in portfolio
        self.portfolio.partialSellOrders = portfoPartialSellOrders

    def apply_asset_policy_result(self, result:policyGetActionResult, asset:registeredOrder, order: agahOrderDetail):
        if result.policyDecision == policyResult.DoNothing:
            return
        if result.policyDecision == policyResult.CancelBuy:
            self.logger.info(f"Cancelling Buy order for {asset.id}.")
            wasSuccess = self.broker.cancel_order(asset.name)
            if wasSuccess:
                asset.make_order_success()
                asset.count = order.tradedQuantity
                self.portfolio.add_order_to_open_orders(asset)
                self.portfolio.remove_order_from_active_buy_orders(asset.id)
                self.portfolio.remove_order_from_partial_buy_orders(asset.id)
                self.logger.info(f"Successfully cancelled Buy order for {asset.id}.")
            return
        if result.policyDecision == policyResult.IterateToFirstSupply:
            self.logger.info(f"Checking to iterate to first supply for {asset.id}.")
            self.set_sell_order_price_as_first_supply_price(asset)
            return
        if result.policyDecision == policyResult.SendSellOrder:
            # Sell Ticker
            self.logger.info(f"Sending sell order for {asset.id}.")
            orderMessage = result.detail
            wasSuccess = self.terminate_order(orderMessage)
            if wasSuccess:
                asset.policy.sell_signal_registered()
                self.logger.info(f"Successfully sent sell order for {asset.id}.")
            return
        if result.policyDecision == policyResult.EditPrice:
            # Editing price of order
            self.logger.info(f"Editing sell order price for {asset.id}.")
            wasSuccess = self.broker.edit_order_price(asset.name, result.detail)
            self.logger.info(f"Result of editing sell order price for {asset.id}:\t{wasSuccess}.")
            return
        raise Exception('No valid result policy provided!')

    def analyze_active_orders(self, report:agahOrders):
        # Buy orders
        for buyOrder in report.activeBuyOrders:
            asset:registeredOrder = self.portfolio.get_order_from_active_orders(orderType.Buy, buyOrder.name)
            # Cancel if time has passed
            if asset is None:
                print(f'{buyOrder.name} was not found in portfolio buy!')
                continue
            asset.registerPrice = buyOrder.price
            result = asset.policy.get_action_command()
            self.apply_asset_policy_result(result, asset, buyOrder)

        # Sell orders
        for sellOrder in report.activeSellOrders:
            asset = self.portfolio.get_order_from_active_orders(orderType.Sell, sellOrder.name)
            # Cancel if time has passed
            if asset is None:
                # print(f'{sellOrder.name} was not found in portfolio sell!')
                continue
            asset.registerPrice = sellOrder.price
            result = asset.policy.get_action_command()
            self.apply_asset_policy_result(result, asset, sellOrder)

    def analyze_open_orders(self, report:agahOrders):
        # Open Buy Orders
        portfoOpenBuyOrders:list[registeredOrder] = self.portfolio.openBuyOrders.copy()
        for buyOrder in self.portfolio.openBuyOrders:
            # Check wheher it is in open list of report
            for buyReport in report.openOrders:
                if buyOrder.name == buyReport.name:
                    break
            else:
                if buyOrder.has_portfo_update_time_passed():
                    portfoOpenBuyOrders.remove(buyOrder)
        # Replace trimmed list in portfolio
        self.portfolio.openBuyOrders = portfoOpenBuyOrders
        
        for buyOrder in report.openOrders:
            asset:registeredOrder = self.portfolio.get_buy_order_from_active_and_partial_list(buyOrder.name)
            if asset is None:
                continue
            asset.make_order_success()
            self.portfolio.add_order_to_open_orders(asset)
            result = asset.policy.get_action_command()
            self.apply_asset_policy_result(result, asset, buyOrder)

    def analyze_partial_orders(self, report:agahOrders):
        for buyOrder in report.partialSuccessBuyOrders:
            asset:registeredOrder = self.portfolio.get_buy_order_from_active_and_partial_list(buyOrder.name)
            if asset is None:
                continue
            asset.make_order_partial()
            self.portfolio.add_order_to_partial_buy_orders(asset)
            result = asset.policy.get_action_command()
            self.apply_asset_policy_result(result, asset, buyOrder)

        for sellOrder in report.partialSuccessSellOrders:
            asset:registeredOrder = self.portfolio.get_sell_order_from_active_and_partial_list_by_name(sellOrder.name)
            if asset is None:
                continue
            asset.make_order_partial()
            self.portfolio.move_active_sell_order_to_partial_list(asset.id)
            result = asset.policy.get_action_command()
            self.apply_asset_policy_result(result, asset, sellOrder)

    def analyze_closed_orders(self, report):
        pass

    def set_sell_order_price_as_first_supply_price(self, sellOrder:registeredOrder):
        if sellOrder.minAllowedPrice == sellOrder.registerPrice:
            return

        orderBoardResult = self.get_ticker_ordersBoard_detail(sellOrder.id)
        if orderBoardResult is None:
            return

        (minSupplyPrice, priceDif) = orderBoardResult
        if sellOrder.registerPrice > minSupplyPrice:
            newPrice = minSupplyPrice - priceDif
            if newPrice < sellOrder.minAllowedPrice:
                newPrice = sellOrder.minAllowedPrice
            self.logger.info(f"Editing price of sell order to first supply price for {sellOrder.id}.")
            wasSuccess = self.broker.edit_order_price(sellOrder.name, newPrice)
            return
        return

    def get_ticker_ordersBoard_detail(self, id):
        priceDif = 50
        url = r'http://tsetmc.com/tsev2/data/instinfofast.aspx?i={}&c=25'.format(id)
        result = requests.get(url, timeout= 1, verify= False).text
        try:
            data = result.split(';')[2].split(';')[0].split(',')
            for row in data[0:5]:
                items = row.split('@')
                if int(items[2]) % 50 != 0 or int(items[3]) % 50 != 0:
                    priceDif = 10
                    break
            for row in data[0:5]:
                items = row.split('@')
                if int(items[2]) % 10 != 0 or int(items[3]) % 10 != 0:
                    priceDif = 1
                    break

            minSupplyPrice = int(data[0].split('@')[3])
            return(minSupplyPrice, priceDif)
        except Exception as e:
            return None

    @classmethod
    def start(cls, OrderQueue, sellStrategiesParentPipes, strategiesGraph, finishEventFromDataProcess):
        managerObj = cls(OrderQueue, sellStrategiesParentPipes, strategiesGraph, finishEventFromDataProcess)
