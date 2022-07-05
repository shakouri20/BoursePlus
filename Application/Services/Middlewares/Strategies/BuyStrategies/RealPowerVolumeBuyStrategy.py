from Application.Services.Middlewares.MiddlewareFramework.MiddlewareOrganizer import *
from Infrastructure.Repository.TickerRepository import ticker_repo
from Domain.Enums import *


class realPowerBuyStrategy(middleware_organizer):
    def __init__(self, name):
        super(realPowerBuyStrategy, self).__init__(name)

    def generate_tickers(self) -> list:
        # Generating sample tickers list
        db = ticker_repo()
        Ids = db.read_list_of_tickers('سهام')['ID']
        return Ids

    def configure(self):
        self.set_strategy_order_type(orderType.Buy)
        self.set_strategy_time_span(orderTimeSpan.Daily)
        self.set_order_price_margin(1.5)
        self.set_minimum_order_score(60)
        self.use_middleware('realPowerMiddleware', name='RealPowerMiddleware', weight= 1, jitMode = True)

    def get_strategy_name():
        return 'realPowerBuyStrategy'



