from enum import Enum   


class policyResult(Enum):
    DoNothing = 0
    IterateToFirstSupply = 1
    CancelBuy = 2
    CancelSell = 3
    SendSellOrder = 4
    EditPrice = 5

