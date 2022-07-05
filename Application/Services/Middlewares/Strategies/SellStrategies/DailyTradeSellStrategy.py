from Domain.Enums.MarketGroups import marketGroupType
from Application.Services.Middlewares.MiddlewareFramework.MiddlewareOrganizer import middleware_organizer
from Domain.Enums.OrderTimeSpan import orderTimeSpan
from Domain.Enums.OrderType import orderType
from Infrastructure.Repository.TickerRepository import ticker_repo


class dailyTradeSellStrategy(middleware_organizer):

    def __init__(self, name):
        super(dailyTradeSellStrategy, self).__init__(name)

    def generate_groups_list(self):
        return [marketGroupType.TotalMarket.value]

    def generate_tickers(self) -> list:
        return []
        
    def configure(self):
        self.set_strategy_order_type(orderType.Sell)
        self.set_strategy_time_span(orderTimeSpan.Daily)
        self.set_order_price_margin(1.5)
        self.set_minimum_order_score(70)
        self.set_trailing_stoploss(10)
        self.set_stoploss(10)
        # self.use_middleware('rangePriceCheckDailySellMiddleware', name='rangePriceCheck', weight= 1)
        self.use_middleware('timeCheckDailySellMiddleware', name='timeCheck', weight= 1)
        self.use_middleware('sellQueueSellDailySellMiddleware', name='sellQueueSell', weight= 1)
        self.use_middleware('rangeDemToSupDailySellMiddleware', name='triggerConfirmer', weight= 1)
        # self.use_middleware('demandPowerDailySellMiddleware', name='demandPower', weight= 1)
        # self.use_middleware('marketLastIndexDailySellMiddleware', name='marketLastIndex', weight= 1)
        # self.use_middleware('maxProfitDailySellMiddleware', name='maxProfit', weight= 1)

    @staticmethod
    def get_strategy_name():
        return 'Daily Trade Sell Strategy'
