from Domain.Models.Setting import settingModel
from Domain.Models.Setting import dailyTradeModel, stockTradeModel
from Domain.ImportEnums import *


class tradeSettings():
    def __init__(self, settingObject: settingModel) -> None:
        self.trade = settingObject.trade

    def get_minimum_buy_value(self):
        return self.trade.minimumBuyValue

    def get_trade_settings_for_order(self, _timeSpan:orderTimeSpan, _assetType:assetType):
        '''Reads the settings and rturns items according to provided time span and asset type.\n
            Returns 3 values:\n
            1. percent of major
            2. max buy value
            3. percent of minor'''

        timeSpanSetting:dailyTradeModel = self.trade.__dict__[_timeSpan.value]
        percentOfMajor = timeSpanSetting.percentOfMajor
        tradeSettings:stockTradeModel = timeSpanSetting.__dict__[_assetType.value]
        percentOfMinor = tradeSettings.percentOfMinor
        maxBuyValue = tradeSettings.maximumBuyValue

        return percentOfMajor, maxBuyValue, percentOfMinor

    def get_broker_fee(self):
        '''Returns the percent of broker fee from settings. '''
        brokerFee = self.trade.brokerFee
        if brokerFee >= 0 and brokerFee <= 100:
            return brokerFee
        else:
            raise Exception('Broker fee is not valid!')

    def get_time_span_major_ratios(self):
        '''Returns a dictionary where keys are time spans and values are corresponding major ratio.'''
        ratios = {}
        sum = 0
        for timeSpan in orderTimeSpan:
            value = self.trade.__dict__[timeSpan.value].percentOfMajor / 100
            ratios[timeSpan] =  value
            sum += value

        if sum != 1:
            raise Exception('Sum of percent of major ratios is not equal to 100!')

        return ratios

        
