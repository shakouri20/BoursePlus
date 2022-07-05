from Application.Services.Middlewares.MiddlewareFramework.Policy import policy
from Domain.Enums.OrderTimeSpan import orderTimeSpan
from Domain.Enums.OrderType import orderType
from Domain.Enums.OrderStatus import orderStatus
from datetime import datetime, timedelta
from Settings import SettingsService

portfoUpdateTimeSpan = SettingsService.realTime.get_portfo_update_timespan()

class registeredOrder():
    def __init__(self, decisionPolicy) -> None:
        self.registerTime: datetime = datetime.now()
        self.orderStatus: orderStatus = orderStatus.Active
        self.name = None
        self.id = None
        self.orderType: orderType = None
        self.sellStrategyName = None
        self.count = None
        self.minAllowedPrice = None
        self.registerPrice = None
        self.timeSpan :orderTimeSpan = None
        self.policy:policy = decisionPolicy
        self.policy.initialize_policy_asset(self)

    def has_portfo_update_time_passed(self):
        now = datetime.now()
        timeDif: timedelta = now - self.registerTime
        if timeDif.seconds > portfoUpdateTimeSpan:
            return True
        return False

    def make_order_partial(self):
        self.orderStatus = orderStatus.PartialSuccess

    def make_order_success(self):
        self.orderStatus = orderStatus.Success

    def is_valid_order(self):
        attributes = [a for a in dir(self) if not a.startswith('__') and not callable(getattr(self, a))]
        for attribute in attributes:
            result = self.__getattribute__(attribute)
            if result is None:
                return False
        
        return True