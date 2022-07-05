from Infrastructure.Repository.OfflineDataRepository import offlineData_repo
from Application.Utility.Indicators.IndicatorService import calculateMacd, calculateRsi

class indicator_services():

    @staticmethod
    def get_RSIs(IDList: list, num: int = 2, length: int = 14):
        """returns RSI dict that its keys is IDs and values is a list of last (num) RSIs.\nif (num)=1 value type is int"""
    
        ID_dict = offlineData_repo().read_last_N_offlineData('ClosePrice', Num= 150, IDList= IDList)

        RsiDict = {}

        # start process
        for ID in ID_dict:
            # macd calculation
            if len(ID_dict[ID]['ClosePrice']) >= length: 
                rsiData = calculateRsi(ID_dict[ID]['ClosePrice'], length)
                rsiData = rsiData[-num:]

                # removes nan from list
                RsiDict[ID] = [x for x in rsiData if str(x) != 'nan']

        return RsiDict   

    @staticmethod
    def get_MACDs(IDList: list, num: int = 2, slowLength: int = 26, fastLength: int = 12, signalSmoothing: int = 9) -> dict:
        """returns MACD dict that its keys is IDs and values is a list of last (num) MACD diff signals.\n if (num)=1 value type is int"""
        
        # requred number for pruduce atleast one output
        requiredNum = max(fastLength, slowLength) + signalSmoothing - 2

        ID_dict = offlineData_repo().read_last_N_offlineData('ClosePrice', Num= requiredNum + 100, IDList= IDList)

        MacdDict = {}

        # start process
        for ID in ID_dict:
            # macd calculation
            if len(ID_dict[ID]['ClosePrice']) >= requiredNum: 
                macdData = calculateMacd(ID_dict[ID]['ClosePrice'], slowLength, fastLength, signalSmoothing)
                macdData = macdData[-num:]

                # removes nan from list
                MacdDict[ID] = [x for x in macdData if str(x) != 'nan']

        return MacdDict     
