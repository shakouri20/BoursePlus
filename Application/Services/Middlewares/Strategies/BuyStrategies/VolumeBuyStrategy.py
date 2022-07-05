from Application.Services.Middlewares.MiddlewareFramework.MiddlewareOrganizer import *
from Infrastructure.Repository.TickerRepository import ticker_repo
from Domain.Enums import *


class volumeBuyStrategy(middleware_organizer):
    def __init__(self, name, daysBack):
        super(volumeBuyStrategy, self).__init__(name, daysBack)

    def generate_tickers(self) -> list:
        # Generating sample tickers list
        db = ticker_repo()
        Ids = db.read_list_of_tickers(tickerTypes= [1])['ID']
        return Ids

    def configure(self):
        self.set_strategy_order_type(orderType.Buy)
        self.set_strategy_time_span(orderTimeSpan.Daily)
        self.set_minimum_order_score(60)
        self.use_middleware('realPowerMiddleware', name='RealPowerMiddleware', weight= 1)
        # self.use_middleware('volumeBuyMiddleware', name='VolumeMiddlewareJitDisabled', weight= 1)
        # self.use_middleware('volumeBuyMiddleware2', name='VolumeMiddlewareJitEnabled', weight= 1)

    def get_strategy_name():
        return 'volumeBuyStrategy'



