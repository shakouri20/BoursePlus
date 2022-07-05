from Application.Utility.Indicators.IndicatorService import calculateSma
from Infrastructure.Repository.OfflineDataRepository import offlineData_repo


class staticLevels_service():

    @classmethod
    def get_static_levels(cls, IDList: list, dayNumberBack: int = 300, smaWindow: int = 10, space1: int = 10, space2: int = 4, prc: int = 11) -> dict:
        """returns Resistance and Supports Levels dict that its keys is IDs and values is levels list ordered ascending"""

        if space1 < space2:
            raise Exception("check space1 >= space2")

        ID_dict = offlineData_repo().read_last_N_offlineData('HighPrice', 'LowPrice','TodayPrice', Num= dayNumberBack, IDList= IDList)

        levelsDict = {}

        # start process
        for ID in ID_dict:

            smaPrice = calculateSma(ID_dict[ID]['TodayPrice'], smaWindow, True)

            if len(smaPrice) >= smaWindow and smaPrice[smaWindow] > smaPrice[smaWindow-1]: 
                rising = True
            else:
                rising = False

            levels = []

            for i in range(len(ID_dict[ID]['TodayPrice'])):

                if i > smaWindow:
                    if smaPrice[i] > smaPrice[i-1] and rising == False:
                        rising = True
                        sup = min(ID_dict[ID]['LowPrice'][i-smaWindow:i])
                        levels.append(sup)

                    elif smaPrice[i] < smaPrice[i-1] and rising == True:
                        rising = False
                        res = max(ID_dict[ID]['HighPrice'][i-smaWindow:i])
                        levels.append(res)
                
                if i >= space1 and i < len(ID_dict[ID]['TodayPrice'])-space1:
                    
                    if cls._is_support(ID_dict[ID], i, space1, space2, prc):
                        sup = ID_dict[ID]['LowPrice'][i]
                        levels.append(sup)

                    if cls._is_resistance(ID_dict[ID], i, space1, space2, -prc):
                        res = ID_dict[ID]['HighPrice'][i]
                        levels.append(res)

            levels.sort()

            finalLevels = []

            if len(levels) > 0:

                finalLevels = [[levels[0]]]

                for i in range(1,len(levels)):
                    for j in range(len(finalLevels)):
                        if levels[i] < sum(finalLevels[j])/len(finalLevels[j])*1.05:
                            finalLevels[j].append(levels[i])
                            break
                    else:
                        finalLevels.append([levels[i]])
                    
                for i in range(len(finalLevels)):
                    finalLevels[i] = int(sum(finalLevels[i])/len(finalLevels[i]))
                
                levelsDict[ID] = finalLevels
        
        return levelsDict

    @staticmethod
    def _is_support(data, i, space1, space2, prc):

        rightNum = 0
        leftNum = 0
        rightHighPrice = 0
        leftHighPrice = 0

        for j in range(1, space1+1):
            if data['LowPrice'][i] <= data['LowPrice'][i-j]:
                leftNum += 1
                leftHighPrice = max(data['HighPrice'][i-j], leftHighPrice)
            else:
                break

        for j in range(1, space1+1):
            if data['LowPrice'][i] <= data['LowPrice'][i+j]:
                rightNum += 1
                rightHighPrice = max(data['HighPrice'][i+j], rightHighPrice)
            else:
                break

        leftPrc = (leftHighPrice-data['LowPrice'][i])/data['LowPrice'][i]*100
        rightPrc = (rightHighPrice-data['LowPrice'][i])/data['LowPrice'][i]*100

        if leftPrc >= prc and rightPrc >= prc and max(rightNum, leftNum) >= space1 and min(rightNum, leftNum) >= space2:
            return True
        else:
            return False

    @staticmethod
    def _is_resistance(data, i, space1, space2, prc):

        rightNum = 0
        leftNum = 0
        rightLowPrice = 10000000
        leftLowPrice = 10000000

        for j in range(1, space1+1):
            if data['HighPrice'][i] >= data['HighPrice'][i-j]:
                leftNum += 1
                leftLowPrice = min(data['LowPrice'][i-j], leftLowPrice)
            else:
                break

        for j in range(1, space1+1):
            if data['HighPrice'][i] >= data['HighPrice'][i+j]:
                rightNum += 1
                rightLowPrice = min(data['LowPrice'][i+j], rightLowPrice)
            else:
                break

        leftPrc = (leftLowPrice-data['HighPrice'][i])/data['HighPrice'][i]*100
        rightPrc = (rightLowPrice-data['HighPrice'][i])/data['HighPrice'][i]*100

        if leftPrc <= prc and rightPrc <= prc and max(rightNum, leftNum) >= space1 and min(rightNum, leftNum) >= space2:
            return True
        else:
            return False
