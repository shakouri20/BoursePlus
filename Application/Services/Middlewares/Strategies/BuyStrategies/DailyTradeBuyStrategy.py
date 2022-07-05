from Application.Services.Middlewares.MiddlewareFramework.MiddlewareOrganizer import *
from Infrastructure.Repository.TickerRepository import ticker_repo
from Domain.Enums import *


class dailyTradeBuyStrategy(middleware_organizer):
    def __init__(self, name):
        super(dailyTradeBuyStrategy, self).__init__(name)

    def generate_groups_list(self):
        return [marketGroupType.TotalMarket.value]

    def generate_tickers(self) -> list:
        # Generating sample tickers list
        db = ticker_repo()
        Ids = db.read_list_of_tickers(tickerTypes = [1], marketTypes= [1, 2, 3, 4, 5 ,6, 9] )['ID']
        return Ids

    def configure(self):
        self.set_strategy_order_type(orderType.Buy)
        self.set_strategy_time_span(orderTimeSpan.Daily)
        self.set_order_price_margin(1.5)
        self.set_minimum_order_score(74)
            
        self.use_middleware('marketLastIndexDailyBuyMiddleware', name='marketLastIndex', weight= 1.1, jitMode = True)
        self.use_middleware('corporateVolumeDifDailyBuyMiddleware', name='cVolumeDif', weight= 4.2, jitMode = True)
        self.use_middleware('realPowerDifDailyBuyMiddleware', name='realPowerDif', weight= 0.9, jitMode = True)
        self.use_middleware('buyPerCapitaDailyBuyMiddleware', name='buyPerCapita', weight= 1.4, jitMode = True)
        
        self.use_middleware('timeCheckDailyBuyMiddleware', name='timeCheck', weight= 0, jitMode = True)
        self.use_middleware('priceCheckDailyBuyMiddleware', name='priceCheck', weight= 0, jitMode = True)
        self.use_middleware('sellQueueCheckDailyBuyMiddleware', name='sellQueueCheck', weight= 0, jitMode = True)
        self.use_middleware('rpvHistoryDailyBuyMiddleware', name='rpvHistory', weight= 1.6, jitMode = True)

        self.use_middleware('marketMADifDailyBuyMiddleware100', name='marketMADif100', weight= 1, jitMode = True)

    def get_strategy_name():
        return 'Daily Trade Buy Strategy'



