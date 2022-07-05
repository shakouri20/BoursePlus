from Domain.Models.Setting import settingModel
from Domain.Enums.Settings.RunType import runType

class accountSettings():
    def __init__(self, settingObject: settingModel) -> None:
        self.account = settingObject.account

    def get_agah_customer_id(self):
        id = self.account.agahCustomerId
        if isinstance(id, int):
            return id
        raise Exception('Agah customer id is not valid!')