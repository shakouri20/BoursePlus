from Domain.Models.Setting import settingModel
from Domain.Enums.Settings.RunType import runType

class operationSettings():
    def __init__(self, settingObject: settingModel) -> None:
        self.operation = settingObject.operation

    def get_runType_setting(self)-> runType:
        '''Returns the run type of program as a runType enum.'''
        _runType = self.operation.runType
        for type in runType:
            if type.value == _runType:
                return type
        raise Exception('Provided runType in settings is not valid!')