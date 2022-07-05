import requests
from Application.Services.Middlewares.MiddlewareFramework.Policy import dailyTakeProfitBuyPolicy
from Application.Services.Middlewares.MiddlewareFramework.MiddlewareOrganizer import *
from Infrastructure.Repository.OfflineDataRepository import offlineData_repo
from Infrastructure.Repository.TickerRepository import ticker_repo
from Domain.Enums import *


class ordersBoardSellQueueDailyBuyStrategy(middleware_organizer):
    def __init__(self, name):
        super(ordersBoardSellQueueDailyBuyStrategy, self).__init__(name)

    def generate_groups_list(self):
        return [marketGroupType.TotalMarket.value]

    def generate_tickers(self) -> list:
        # Generating sample tickers list
        IDs = ticker_repo().read_list_of_tickers(tickerTypes= [1], marketTypes= [1, 2, 3, 4, 5, 6])['ID']
        data = offlineData_repo().read_last_N_offlineData('HighPrice', 'LowPrice', Num= 1, IDList= IDs)
        finalIDs = []
        for ID in data:
            if data[ID]['HighPrice'][0] != data[ID]['LowPrice'][0]:
                finalIDs.append(ID)

        return finalIDs

    def configure(self):
        self.set_strategy_order_type(orderType.Buy)
        self.set_strategy_time_span(orderTimeSpan.Daily)
        self.set_policy(dailyTakeProfitBuyPolicy)
        self.set_order_price_margin(1.5)
        self.set_minimum_order_score(40)
        
        self.use_middleware('priceCheckDailyBuyMiddleware', name='priceCheck', weight= 0, jitMode = True)
        self.use_middleware('sellQueueCheckDailyBuyMiddleware', name='sellQueueCheck', weight= 0, jitMode = True)
        self.use_middleware('obSellPerCapitaDailyBuyMiddleware', name='obSellPerCapita', weight= 1, jitMode = True)
        
        self.use_middleware('timeCheckDailyBuyMiddleware', name='timeCheck', weight= 0, jitMode = True)
        self.use_middleware('marketLastIndexDailyBuyMiddleware', name='marketLastIndex', weight= 0, jitMode = True)


    def calculate_order_price(self, Id) -> int:
        priceDif = 10
        minAllowedPrice = self.dataHandler.minAllowedPrice([Id])[Id]
        maxAllowedPrice = self.dataHandler.maxAllowedPrice([Id])[Id]
        minPrice = self.dataHandler.minPrice(num= 1, IDList= [Id])[Id][0]
        maxPrice = self.dataHandler.maxPrice(num= 1, IDList= [Id])[Id][0]
        
        if minAllowedPrice % 10 != 0 or maxAllowedPrice % 10 != 0 or\
           minPrice % 10 != 0 or maxPrice % 10 != 0:
            priceDif = 1

        if minAllowedPrice % 50 == 0 or maxAllowedPrice % 50 == 0:
            if minPrice % 50 == 0 or maxPrice % 50 == 0:
                priceDif = 50
            
        return minAllowedPrice + 2 * priceDif
        

    def get_strategy_name():
        return 'Orders Board Sell Queue Buy Strategy'



