from Domain.Models.Setting import settingModel
from Domain.Enums.Settings.RunType import runType

class backTestSettings():
    def __init__(self, settingObject: settingModel) -> None:
        self.backTest = settingObject.backTest

    def get_initial_balance(self):
        return self.backTest.initialBalance