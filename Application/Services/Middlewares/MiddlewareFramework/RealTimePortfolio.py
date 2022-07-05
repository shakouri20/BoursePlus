from Application.Services.Middlewares.MiddlewareFramework.FundInfo import fundInfo
from datetime import datetime
from Domain.Enums.QueryOutPutType import queryOutPutType
from Domain.Enums.OrderType import orderType
from Domain.Enums.OrderTimeSpan import orderTimeSpan
from Domain.Models.Order import Order
from Application.Services.Middlewares.MiddlewareFramework.RegisteredOrder import registeredOrder
from Infrastructure.Repository.TickerRepository import ticker_repo



class realTimePortfolio():

    def __init__(self) -> None: # InComplete
        self.tickers = ticker_repo().read_list_of_tickers(IPO= 2, outPutType= queryOutPutType.DictDict)
        self.activeSellOrders  :list[registeredOrder] = []
        self.activeBuyOrders   :list[registeredOrder] = []
        self.partialSellOrders :list[registeredOrder] = []
        self.partialBuyOrders  :list[registeredOrder] = []
        # There is not any open sell orders
        self.openBuyOrders     :list[registeredOrder] = []
        
        self.fundInfo = fundInfo()

    #Todo: edit the __Str__ to show all orders to show in log file
    def __str__(self): # InComplete
        data = []
        # data.append(f'Last Updated:\t{datetime.now()}\n')
        counter = 0
        data.append('=============================<< Open Orders >>===========================\n')
        for asset in self.openBuyOrders:
            counter += 1
            data.append(f'\t{counter}  ' + self.order_to_str(asset) + '\n')
        data.append('==========================<< Active Buy Orders >>========================\n')
        counter = 0
        for asset in self.activeBuyOrders:
            counter += 1
            data.append(f'\t{counter}  ' + self.order_to_str(asset) + '\n')
        data.append('==========================<< Active Sell Orders >>=======================\n')
        counter = 0
        for asset in self.activeSellOrders:
            counter += 1
            data.append(f'\t{counter}  ' + self.order_to_str(asset) + '\n')
        data.append('==========================<< Partial Buy Orders >>=======================\n')
        counter = 0
        for asset in self.partialBuyOrders:
            counter += 1
            data.append(f'\t{counter}  ' + self.order_to_str(asset) + '\n')
        data.append('==========================<< Partial Sell Orders >>======================\n')
        counter = 0
        for asset in self.partialSellOrders:
            counter += 1
            data.append(f'\t{counter}  ' + self.order_to_str(asset) + '\n')
        return data

    def order_to_str(self, order: registeredOrder):
        return f'name: {self.tickers[order.id]["FarsiTicker"]}\t Count:{order.count}\
            Time: {order.registerTime.strftime("%H:%M:%S")}\
            Price: {order.registerPrice}'

    def is_buy_order_in_portfolio(self, id):
        for asset in self.activeBuyOrders:
            if asset.id == id:
                return True

        for asset in self.partialBuyOrders:
            if asset.id == id:
                return True

        for asset in self.openBuyOrders:
            if asset.id == id:
                return True

        return False

    def is_sell_order_in_portfolio(self, id):
        for asset in self.activeSellOrders:
            if asset.id == id:
                return True

        for asset in self.partialSellOrders:
            if asset.id == id:
                return True

        return False

    def get_buy_order_from_active_and_partial_list(self, name):
        ''' Checks whether asset with same tickerId and order type exists in portfolio .
                 If asset is not in the portfolio returns False.'''
        for asset in self.partialBuyOrders:
            if asset.name == name:
                return asset

        for asset in self.activeBuyOrders:
            if asset.name == name:
                return asset

        return None

    def get_sell_order_from_active_and_partial_list_by_name(self, name):
        for asset in self.partialSellOrders:
            if asset.name == name:
                return asset

        for asset in self.activeSellOrders:
            if asset.name == name:
                return asset

        return None

    def get_sell_order_from_active_and_partial_list_by_id(self, id):
        for asset in self.partialSellOrders:
            if asset.id == id:
                return asset

        for asset in self.activeSellOrders:
            if asset.id == id:
                return asset

        return None

    def get_buyed_asset_from_portfolio(self, id):
        ''' Checks whether asset with same tickerId and order type exists in portfolio .
                 If asset is not in the portfolio returns False.'''
        for asset in self.openBuyOrders:
            if asset.id == id:
                return asset
        
        for asset in self.partialBuyOrders:
            if asset.id == id:
                return asset

        return None

    def is_order_in_open_list(self, name):
        for asset in self.openBuyOrders:
            if asset.name == name:
                return True
        return False

    def add_order_to_active_buy_orders(self, order: registeredOrder):
        for asset in self.activeBuyOrders:
            if asset.id == order.id and asset.orderType == order.orderType:
                return
                # raise Exception('Order already in active orders list!!')
        self.activeBuyOrders.append(order)

    def add_order_to_partial_buy_orders(self, order: registeredOrder):
        for asset in self.activeBuyOrders:
            if asset.id == order.id and asset.orderType == order.orderType:
                return
                # raise Exception('Order already in active orders list!!')
        order.registerTime = datetime.now()
        order.make_order_partial()
        self.partialBuyOrders.append(order)

    def add_order_to_active_sell_orders(self, order: registeredOrder):
        for asset in self.activeSellOrders:
            if asset.id == order.id:
                raise Exception('Order already in active orders list!!')
        self.activeSellOrders.append(order)

    def remove_order_from_active_buy_orders(self, id):
        for asset in self.activeBuyOrders:
            if asset.id == id:
                self.activeBuyOrders.remove(asset)
                return True
        return None

    def remove_order_from_active_sell_orders(self, id):
        for asset in self.activeSellOrders:
            if asset.id == id:
                self.activeSellOrders.remove(asset)
                return True
        return None

    def remove_order_from_partial_buy_orders(self, id):
        for asset in self.partialBuyOrders:
            if asset.id == id:
                self.activeBuyOrders.remove(asset)
                return True
        return None

    def remove_order_from_partial_sell_orders(self, id):
        for asset in self.partialSellOrders:
            if asset.id == id:
                self.partialSellOrders.remove(asset)
                return True
        return None

    def add_order_to_open_orders(self, order: registeredOrder):
        for asset in self.openBuyOrders:
            if asset.id == order.id:
                return
                # raise Exception('Order already in active orders list!!')
        order.registerTime = datetime.now()
        self.openBuyOrders.append(order)

    def move_active_sell_order_to_partial_list(self, id):
        for asset in self.activeSellOrders:
            if asset.id == id:
                asset.make_order_partial()
                asset.registerTime = datetime.now()
                self.partialSellOrders.append(asset)
                self.activeSellOrders.remove(asset)
                return True
        return None

    def get_order_from_active_orders(self, ordertype, name):
        if ordertype == orderType.Buy:
            for order in self.activeBuyOrders:
                if order.name == name:
                    return order
        else:
            for order in self.activeSellOrders:
                if order.name == name:
                    return order

        return None

    def update_timespan_balances(self):
        Balance = 0
        for timeSpan in orderTimeSpan:
            balance = 0
            # Active Orders
            for buyOrder in self.activeBuyOrders:
                if buyOrder.timeSpan == timeSpan:
                    balance += buyOrder.count * buyOrder.registerPrice

            for buyOrder in self.partialBuyOrders:
                if buyOrder.timeSpan == timeSpan:
                    balance += buyOrder.count * buyOrder.registerPrice

            for buyOrder in self.openBuyOrders:
                if buyOrder.timeSpan == timeSpan:
                    balance += buyOrder.count * buyOrder.registerPrice
                
            # Updating balances
            self.fundInfo.set_time_span_balance(timeSpan, balance)
            Balance += balance
        
        newBalance = self.fundInfo.get_free_margin() + Balance
        self.fundInfo.set_balance(newBalance)

    def updateLog(self):
        self.update_timespan_balances()
        path = 'Portfolio.txt'
        with open(path, 'w',encoding="utf-8") as f:
            f.writelines(self.fundInfo.get_report())
            f.writelines(self.__str__())