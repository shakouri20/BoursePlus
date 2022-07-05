from Domain.Enums.MarketGroups import marketGroupType
from Application.Services.Middlewares.MiddlewareFramework.MiddlewareOrganizer import middleware_organizer
from Domain.Enums.OrderTimeSpan import orderTimeSpan
from Domain.Enums.OrderType import orderType
from Infrastructure.Repository.TickerRepository import ticker_repo


class constantChangeSellStrategy(middleware_organizer):

    def __init__(self, name):
        super(constantChangeSellStrategy, self).__init__(name)

    def generate_groups_list(self):
        return [marketGroupType.TotalMarket.value]

    def configure(self):
        self.set_strategy_order_type(orderType.Sell)
        self.set_strategy_time_span(orderTimeSpan.Daily)
        self.set_order_price_margin(1.5)
        self.set_minimum_order_score(60)
        self.set_trailing_stoploss(2)
        self.set_stoploss(1)
        self.use_middleware('constantChangeSellMiddleware', name='constantChangeJitDisabled', weight= 1)

    @staticmethod
    def get_strategy_name():
        return 'ConstantChangeSellStrategy'

    def generate_tickers(self) -> list:
        return []