import datetime

class tradeInfo:
    def __init__(self) -> None:

        self.ID = None
        self.name = None
        self.buyTime: datetime.datetime = None
        self.sellTime: datetime.datetime = None
        self.buyPrice = None
        self.sellPrice = None
        self.profit = None
        self.buyMiddleware = None
        self.sellMiddleware = None
        self.buyType = None
        self.sellType = None

    