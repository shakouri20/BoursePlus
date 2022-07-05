from os import stat
from Infrastructure.Repository.OfflineDataRepository import offlineData_repo

class averge_services():


    @staticmethod
    def get_averge_volume(IDList: list, num: int = 30) -> dict:
        """returns averge volume dict that its keys is IDs and values is averge volumes"""
        
        ID_dict = offlineData_repo().read_last_N_offlineData('Value', 'TodayPrice', Num= num, IDList= IDList)
        
        # start process
        volumesDict = {}

        for ID in ID_dict:
            Volumes = [int(ID_dict[ID]['Value'][i]/ID_dict[ID]['TodayPrice'][i]) for i in range(len(ID_dict[ID]['Value']))]
            volumesDict[ID] = int(sum(Volumes)/len(Volumes))
        return volumesDict
