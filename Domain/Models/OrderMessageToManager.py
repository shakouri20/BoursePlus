from Domain.Models.Order import Order


class orderMessageToManager(Order):
    def __init__(self) -> None:
        self.strategyName = None
        self.score = None
        self.minAllowedPrice = None
        super(orderMessageToManager, self).__init__()

    def set_score(self, score):
        self.score = score
    
    def set_minimum_allowed_price(self, price):
        self.minAllowedPrice = price

    def set_strategyName(self, name):
        self.strategyName = name

    def get_score(self):
        return self.score

    def get_minimum_allowed_price(self):
        return self.minAllowedPrice

    def get_strategyName(self):
        return self.strategyName

    
    