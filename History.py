# RealPower Group
RealPowersIndex = []
numList = [0 for i in range(21)]
RealPowercorrespond = [-3, -2.8, -2.4, -2, -1.8, -1.5, -1.4, -1.25, -1.15, -1.05, 0, 1.05, 1.15, 1.25, 1.4, 1.5, 1.8, 2, 2.4, 2.8, 3]
    
if data[ID]['RealPower'] > 1 and  data[ID]['RealPower'] <= 1.1:
    numList[20] += 1
elif data[ID]['RealPower'] > 1.1 and  data[ID]['RealPower'] <= 1.2:
    numList[19] += 1
elif data[ID]['RealPower'] > 1.2 and  data[ID]['RealPower'] <= 1.3:
    numList[18] += 1
elif data[ID]['RealPower'] > 1.3 and  data[ID]['RealPower'] <= 1.45:
    numList[17] += 1
elif data[ID]['RealPower'] > 1.45 and  data[ID]['RealPower'] <= 1.65:
    numList[16] += 1
elif data[ID]['RealPower'] > 1.65 and  data[ID]['RealPower'] <= 1.9:
    numList[15] += 1
elif data[ID]['RealPower'] > 1.9 and  data[ID]['RealPower'] <= 2.2:
    numList[14] += 1
elif data[ID]['RealPower'] > 2.2 and  data[ID]['RealPower'] <= 2.6:
    numList[13] += 1
elif data[ID]['RealPower'] > 2.6 and  data[ID]['RealPower'] <= 3:
    numList[12] += 1
elif data[ID]['RealPower'] > 3:
    numList[11] += 1

if data[ID]['RealPower'] == 1:
    numList[10] += 1

elif data[ID]['RealPower'] < 1:
    if 1/data[ID]['RealPower'] > 1 and  1/data[ID]['RealPower'] <= 1.1:
        numList[9] += 1
    elif 1/data[ID]['RealPower'] > 1.1 and  1/data[ID]['RealPower'] <= 1.2:
        numList[8] += 1
    elif 1/data[ID]['RealPower'] > 1.2 and  1/data[ID]['RealPower'] <= 1.3:
        numList[7] += 1
    elif 1/data[ID]['RealPower'] > 1.3 and  1/data[ID]['RealPower'] <= 1.45:
        numList[6] += 1
    elif 1/data[ID]['RealPower'] > 1.45 and  1/data[ID]['RealPower'] <= 1.65:
        numList[5] += 1
    elif 1/data[ID]['RealPower'] > 1.65 and  1/data[ID]['RealPower'] <= 1.9:
        numList[4] += 1
    elif 1/data[ID]['RealPower'] > 1.9 and  1/data[ID]['RealPower'] <= 2.2:
        numList[3] += 1
    elif 1/data[ID]['RealPower'] > 2.2 and  1/data[ID]['RealPower'] <= 2.6:
        numList[2] += 1
    elif 1/data[ID]['RealPower'] > 2.6 and  1/data[ID]['RealPower'] <= 3:
        numList[1] += 1
    elif 1/data[ID]['RealPower'] > 3:
        numList[0] += 1

    maxNum = max(numList)
    thisRealPower = RealPowercorrespond[numList.index(maxNum)]
    RealPowersIndex.append(thisRealPower)

    