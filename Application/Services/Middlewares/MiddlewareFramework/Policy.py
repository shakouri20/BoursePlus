from math import floor
from Domain.Enums.AssetType import assetType
from Domain.Models.OrderMessageToManager import orderMessageToManager
from Domain.Enums.OrderStatus import orderStatus
from Domain.Enums.OrderState import orderState
from datetime import datetime, timedelta
# from Application.Services.Middlewares.MiddlewareFramework.RegisteredOrder import registeredOrder
from Domain.Enums.PolicyResult import policyResult
from Domain.Models.Order import Order
from Settings import SettingsService

registerCancelTimeSpan = SettingsService.realTime.get_register_cancel_timeSpan()


class policyGetActionResult():
    def __init__(self) -> None:
        self.policyDecision = None
        self.detail = None


class policy():
    def __init__(self) -> None:
        self.asset = None

    def initialize_policy_asset(self, asset):
        self.asset = asset

    def get_action_command(self):
        raise NotImplementedError('get_action_command has not been implemented!')


class dailyTakeProfitBuyPolicy(policy):
    def __init__(self, marketIndex) -> None:
        self.isSellRegistered = False
        self.marketIndex= marketIndex[-1]
        super(dailyTakeProfitBuyPolicy, self).__init__()

    def sell_signal_registered(self):
        self.isSellRegistered = True

    def get_action_command(self):
        if self.asset.orderStatus != orderStatus.Success:
            result = policyGetActionResult()
            if self.has_cancel_time_passed(self.asset):
                result.policyDecision = policyResult.CancelBuy
                return result
            else:
                result.policyDecision = policyResult.DoNothing
                return result 

        if self.asset.orderStatus == orderStatus.Success:
            result = policyGetActionResult()
            if not self.isSellRegistered:
                result.policyDecision = policyResult.SendSellOrder

                TP = 2.25 if self.marketIndex < 0 else 3
                print(f'Buy Policy ====> TP is:\t{TP}')
                orderMsg = orderMessageToManager()
                orderMsg.set_order_type(self.asset.orderType)
                orderMsg.set_time_span(self.asset.timeSpan)               
                orderMsg.set_asset_type(assetType.Stock) # Warning: assetType.Stock is hard-coded.
                orderMsg.set_order_asset_price(self.asset.registerPrice)
                orderMsg.set_tickerId(self.asset.id)
                orderMsg.set_score(80)
                orderMsg.set_strategyName(self.asset.sellStrategyName)
                price = floor(self.asset.minAllowedPrice * (100 + TP)/100/10) * 10
                orderMsg.set_order_price(price)
                orderMsg.set_minimum_allowed_price(self.asset.minAllowedPrice)
                orderMsg.set_order_time(datetime.now())
                orderMsg.policy = dailyTakeProfitSellPolicy()
                
                result.detail = orderMsg
                print('Buy Policy ===> Setting TP')
                return result
            else:
                result.policyDecision = policyResult.DoNothing
                return result

    def has_cancel_time_passed(self, asset):
        now = datetime.now()
        timeDif: timedelta = now - asset.registerTime
        if timeDif.seconds > registerCancelTimeSpan * 60:
            return True
        return False


class sellPolicy(policy):
    def __init__(self) -> None:
        super(sellPolicy, self).__init__()

    def sell_signal_issued(self, order: Order):
        raise NotImplementedError('sell_signal_issued has not been implemented!')
    

class dailyTakeProfitSellPolicy(sellPolicy):
    def __init__(self) -> None:
        self.isSellSignalIssued = False
        self.isTpRevised = False
        self.registerTime = datetime.now()
        super(dailyTakeProfitSellPolicy, self).__init__()

    def get_action_command(self):
        result = policyGetActionResult()
        if self.isSellSignalIssued:
            result.policyDecision = policyResult.IterateToFirstSupply
            return result
        else:
            if not self.isTpRevised:
                Dt: timedelta = datetime.now() - self.registerTime
                if Dt.seconds > 10 * 60:
                    result.policyDecision = policyResult.EditPrice
                    result.detail = floor(self.asset.minAllowedPrice * (100 + 8) /100/10) * 10
                    self.isTpRevised = True
                    print(f'Sell Policy ====> Editing TP to 8 percent.')
                    return result
                
            result.policyDecision = policyResult.DoNothing
            return result


    def sell_signal_issued(self, order: Order):
        self.isSellSignalIssued = True