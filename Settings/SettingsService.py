from Settings.RealTimeSettings import realTimeSettings
from Settings.AccountSettings import accountSettings
from Domain.Models.Setting import settingModel
from Settings.OperationSettings import operationSettings
from Settings.TradeSettings import tradeSettings
from Settings.BackTestSettings import backTestSettings




settingObject: settingModel = settingModel.from_json()

operation = operationSettings(settingObject)
trade     = tradeSettings(settingObject)
backTest  = backTestSettings(settingObject)
realTime = realTimeSettings(settingObject)
account   = accountSettings(settingObject)

