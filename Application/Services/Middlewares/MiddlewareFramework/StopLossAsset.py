

from Domain.Enums.StopLossStatus import stopLossStatus


class stopLossAsset():

    def __init__(self, tickerId, buyPrice, stopLoss, trailingMargin) -> None:
        self.tickerId = tickerId
        self.buyPrice = buyPrice
        self.isTrailingStopLossActivated = False
        self.stopLossPrice = stopLoss
        self.trailingStopLossMargin = trailingMargin

    def get_ticker_stoploss_status(self, price):
        if price <= self.stopLossPrice:
            return stopLossStatus.Broken

        # trailedStopLoss = (1 - self.trailingStopLossMargin/100) * price
        # trailingStopLossTriggerPrice = (1 + self.trailingStopLossMargin/100) * price
        if self.isTrailingStopLossActivated:
            if price > self.stopLossPrice * (1 + self.trailingStopLossMargin / 100):
                self.stopLossPrice = price * (1 - self.trailingStopLossMargin / 100)
            return stopLossStatus.Holding

        if price > self.buyPrice * (1 + self.trailingStopLossMargin / 100):
            self.activate_trailing_stoploss()
            self.stopLossPrice = price * (1 - self.trailingStopLossMargin / 100)
            return stopLossStatus.Holding


    def activate_trailing_stoploss(self):
        if self.isTrailingStopLossActivated:
            raise Exception('Trailing stop loss already activated!1 Can not activate again.')
        self.isTrailingStopLossActivated = True

    def get_tickerId(self):
        return self.tickerId