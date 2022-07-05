from Application.Services.Middlewares.MiddlewareFramework.MiddlewareOrganizer import *
from Domain.Enums.OrderTimeSpan import orderTimeSpan


class volumeSellStrategy(middleware_organizer):
    def __init__(self, name):
        super(volumeSellStrategy, self).__init__(name)

    def configure(self):
        self.set_strategy_order_type(orderType.Sell)
        self.set_strategy_time_span(orderTimeSpan.daily)
        self.set_minimum_order_score(80)
        self.use_middleware('volumeBuyMiddleware', name='VolumeMiddlewareJitDisabled', weight= 2)

    @staticmethod
    def get_strategy_name():
        return 'volumeSellStrategy'
        
    def generate_tickers(self) -> list:
        # Generating sample tickers list
        db = database_repo()
        db.connect()
        Ids = db.read_list_of_tickers(marketTypes= [1])['ID']
        return Ids