
from Application.Utility.Indicators.IndicatorService import calculateSma


def calc_resistance_support(highPrices, lowPrices, space1= 10, space2 = 4, prc = 11):

    levels = []

    for i in range(space1, len(lowPrices)-space1):

        if isSupport(highPrices, lowPrices, i, space1, space2, prc):
            levels.append(lowPrices[i])

        if isResistance(highPrices, lowPrices, i, space1, space2, -prc):
            levels.append(highPrices[i])
            
    todayPrices = [(lowPrices[i]+highPrices[i])/2 for i in range(len(lowPrices))]

     #  method sma
    window = 10
    todayMA= calculateSma(todayPrices, window= window,  fillna= True)

    try:
        if todayMA[window] > todayMA[window-1]: 
            Rising = True
        else:
            Rising = False
    except:
        return []

    for i in range(window+1, len(todayMA)):

        if todayMA[i] > todayMA[i-1] and Rising == False:
            Rising = True
            levels.append(min(lowPrices[i-window:i]))

        elif todayMA[i] < todayMA[i-1] and Rising == True:
            Rising = False
            levels.append(max(highPrices[i-window:i]))
    
    if levels == []:
        return []
        
    levels.sort()
    finalLevels = [[levels[0]]]

    for i in range(1,len(levels)):
        for j in range(len(finalLevels)):
            if levels[i] < sum(finalLevels[j])/len(finalLevels[j])*1.05:
                finalLevels[j].append(levels[i])
                break
        else:
            finalLevels.append([levels[i]])

    finalLevelsAvg = []
    for i in range(len(finalLevels)):
        finalLevelsAvg.append(sum(finalLevels[i])/len(finalLevels[i]))
        
    return finalLevelsAvg



def isSupport(highPrices, lowPrices,  i, space1, space2, prc):

    rightNum = 0
    leftNum = 0
    rightHighPrices = 0
    leftHighPrices = 0

    for j in range(1, space1+1):
        if lowPrices[i] <= lowPrices[i-j]:
            leftNum += 1
            leftHighPrices = max(highPrices[i-j], leftHighPrices)
        else:
            break

    for j in range(1, space1+1):
        if lowPrices[i] <= lowPrices[i+j]:
            rightNum += 1
            rightHighPrices = max(highPrices[i+j], rightHighPrices)
        else:
            break

    leftPrc = (leftHighPrices-lowPrices[i])/lowPrices[i]*100
    rightPrc = (rightHighPrices-lowPrices[i])/lowPrices[i]*100

    if leftPrc >= prc and rightPrc >= prc and max(rightNum, leftNum) >= space1 and min(rightNum, leftNum) >= space2: # and 
        return True
    else:
        return False

def isResistance(highPrices, lowPrices, i, space1, space2, prc):

    rightNum = 0
    leftNum = 0
    rightLowPrice = 10000000
    leftLowPrice = 10000000

    for j in range(1, space1+1):
        if highPrices[i] >= highPrices[i-j]:
            leftNum += 1
            leftLowPrice = min(lowPrices[i-j], leftLowPrice)
        else:
            break

    for j in range(1, space1+1):
        if highPrices[i] >= highPrices[i+j]:
            rightNum += 1
            rightLowPrice = min(lowPrices[i+j], rightLowPrice)
        else:
            break

    leftPrc = (leftLowPrice-highPrices[i])/highPrices[i]*100
    rightPrc = (rightLowPrice-highPrices[i])/highPrices[i]*100

    if leftPrc <= prc and rightPrc <= prc and max(rightNum, leftNum) >= space1 and min(rightNum, leftNum) >= space2: #  and
        return True
    else:
        return False
