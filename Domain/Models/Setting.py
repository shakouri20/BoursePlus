import os
import json

# ******************************<<    operation   >>********************************************
class operationModel():
    def __init__(self, runType) -> None:
        self.runType = runType

# ******************************<<    backTest   >>********************************************
class backTestModel():
    def __init__(self, initialBalance) -> None:
        self.initialBalance = initialBalance * 10**7

# ******************************<<    realTime   >>********************************************
class realTimeModel():
    def __init__(self, monitorPortfoInterval, AgahApiDefaultTimeOut, monitorChromePeriod, registerCancelTimeSpan, portfoUpdateTimeSpan, initialBalance) -> None:
        self.monitorPortfoInterval = monitorPortfoInterval
        self.AgahApiDefaultTimeOut = AgahApiDefaultTimeOut
        self.monitorChromePeriod = monitorChromePeriod
        self.registerCancelTimeSpan = registerCancelTimeSpan
        self.portfoUpdateTimeSpan = portfoUpdateTimeSpan
        self.initialBalance = initialBalance * 10**7

# ******************************<<    trade   >>********************************************
class stockTradeModel():
    def __init__(self, maximumBuyValue, percentOfMinor) -> None:
        self.maximumBuyValue = maximumBuyValue * 10**7
        self.percentOfMinor = percentOfMinor

class dailyTradeModel():
    def __init__(self, percentOfMajor, stock, option) -> None:
        self.percentOfMajor = percentOfMajor
        self.stock = stockTradeModel(**stock)
        self.option = stockTradeModel(**option)

class tradeModel():
    def __init__(self, minimumBuyValue, brokerFee, daily, shortTerm, midTerm, longTerm) -> None:
        self.minimumBuyValue = minimumBuyValue * 10**7
        self.brokerFee = brokerFee

        self.daily = dailyTradeModel(**daily)
        self.shortTerm = dailyTradeModel(**shortTerm)
        self.midTerm = dailyTradeModel(**midTerm)
        self.longTerm = dailyTradeModel(**longTerm)

class accountModel():
    def __init__(self, agahCustomerId) -> None:
        self.agahCustomerId = agahCustomerId

# ******************************<<    settings   >>********************************************
class settingModel():
    def __init__(self, operation, trade, backTest, realTime, account) -> None:
        self.operation = operationModel(**operation)
        self.trade = tradeModel(**trade)
        self.backTest = backTestModel(**backTest)
        self.realTime = realTimeModel(**realTime)
        self.account = accountModel(**account)

    @classmethod
    def from_json(cls):
        cwd = os.getcwd()
        file = r'{0}\Settings.json'.format(cwd)
        data = open(file,'r')
        data_dict = json.loads(data.read())
        obj = cls(**data_dict)
        return obj
