from Domain.Models.Setting import settingModel
from Domain.Enums.Settings.RunType import runType

class realTimeSettings():
    def __init__(self, settingObject: settingModel) -> None:
        self.realTime = settingObject.realTime

    def get_monitor_portfo_interval(self):
        return self.realTime.monitorPortfoInterval

    def get_agah_api_default_timeOut(self):
        return self.realTime.AgahApiDefaultTimeOut

    def get_monitor_chrome_period(self):
        return self.realTime.monitorChromePeriod

    def get_register_cancel_timeSpan(self):
        return self.realTime.registerCancelTimeSpan

    def get_portfo_update_timespan(self):
        return self.realTime.portfoUpdateTimeSpan
    
    def get_realTime_initial_balance(self):
        return self.realTime.initialBalance