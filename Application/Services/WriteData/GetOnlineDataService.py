from math import floor
from Application.Utility.Web.WebRequest import getCsvData
import DefaultParams as defParam


def get_last_clientType_Data() -> dict:
    '''returns ClientTypeData as a dict whose keys is ticker Ids'''
    csvData = getCsvData(defParam.clientTypeAllUrl)

    ClientTypeDataDict = {}
    lineLength = 9
    ID = 0
    RealBuyNumber = 1
    CorporateBuyNumber = 2
    RealBuyVolume = 3
    CorporateBuyVolume = 4
    RealSellNumber = 5
    CorporateSellNumber = 6
    RealSellVolume = 7
    CorporateSellVolume = 8

    for thisLine in csvData:
        if len(thisLine) == lineLength:
            isNumericAll = True
            for i in range(lineLength):
                if thisLine[i].isnumeric() == False:
                    isNumericAll = False
                    break
            if isNumericAll == True:
                thisID = int(thisLine[ID])
                ClientTypeDataDict[thisID] = {}
                ClientTypeDataDict[thisID]['RealBuyNumber'] = int(thisLine[RealBuyNumber])
                ClientTypeDataDict[thisID]['CorporateBuyNumber'] = int(thisLine[CorporateBuyNumber])
                ClientTypeDataDict[thisID]['RealBuyVolume'] = int(thisLine[RealBuyVolume])
                ClientTypeDataDict[thisID]['CorporateBuyVolume'] = int(thisLine[CorporateBuyVolume])
                ClientTypeDataDict[thisID]['RealSellNumber'] = int(thisLine[RealSellNumber])
                ClientTypeDataDict[thisID]['CorporateSellNumber'] = int(thisLine[CorporateSellNumber])
                ClientTypeDataDict[thisID]['RealSellVolume'] = int(thisLine[RealSellVolume])
                ClientTypeDataDict[thisID]['CorporateSellVolume'] = int(thisLine[CorporateSellVolume])
    return ClientTypeDataDict

def get_last_marketWatch_data() -> dict:
    '''returns MarketWatchData as a dict whose keys is ticker Ids'''
    # get Data as list of lists
    csvData = getCsvData(defParam.marketWatchUrl, splitters= ['@', ';', ','])

    pricesData = csvData[2]
    ordersBoardData = csvData[3]

    # define dict and defult parameters
    # prices
    marketWatchDict = {}
    # pricesLineLength = 23
    ID = 0
    Name = 2
    heven = 4
    FirstPrice = 5
    TodayPrice = 6
    LastPrice = 7
    Number = 8
    Volume = 9
    MinPrice = 11
    MaxPrice = 12
    YesterdayPrice = 13
    MaxAllowedPrice = 19
    MinAllowedPrice = 20
    ShareNumber = 21
    # orders board
    # OrdersLineLength = 8
    ID = 0
    Row = 1
    SupplyNumber = 2
    DemandNumber = 3
    DemandPrice = 4
    SupplyPrice = 5
    DemandVolume = 6
    SupplyVolume = 7

    for thisLine in pricesData:
        thisID = int(thisLine[ID])
        marketWatchDict[thisID] = {}
        marketWatchDict[thisID]['Name'] = thisLine[Name]
        marketWatchDict[thisID]['heven'] = int(thisLine[heven])
        marketWatchDict[thisID]['FirstPrice'] = int(thisLine[FirstPrice])
        marketWatchDict[thisID]['TodayPrice'] = int(thisLine[TodayPrice])
        marketWatchDict[thisID]['LastPrice'] = int(thisLine[LastPrice])
        marketWatchDict[thisID]['Number'] = int(thisLine[Number])
        marketWatchDict[thisID]['Volume'] = int(thisLine[Volume])
        marketWatchDict[thisID]['MinPrice'] = int(thisLine[MinPrice])
        marketWatchDict[thisID]['MaxPrice'] = int(thisLine[MaxPrice])
        marketWatchDict[thisID]['YesterdayPrice'] = int(thisLine[YesterdayPrice])
        marketWatchDict[thisID]['MaxAllowedPrice'] = int(float(thisLine[MaxAllowedPrice]))
        marketWatchDict[thisID]['MinAllowedPrice'] = int(float(thisLine[MinAllowedPrice]))
        marketWatchDict[thisID]['ShareNumber'] = int(thisLine[ShareNumber])

    for thisLine in ordersBoardData:
        thisID = int(thisLine[ID])
        if thisID in marketWatchDict:
            marketWatchDict[thisID][f'SupplyNumber{int(thisLine[Row])}'] = int(thisLine[SupplyNumber])
            marketWatchDict[thisID][f'DemandNumber{int(thisLine[Row])}'] = int(thisLine[DemandNumber])
            marketWatchDict[thisID][f'DemandPrice{int(thisLine[Row])}'] = int(thisLine[DemandPrice])
            marketWatchDict[thisID][f'SupplyPrice{int(thisLine[Row])}'] = int(thisLine[SupplyPrice])
            marketWatchDict[thisID][f'DemandVolume{int(thisLine[Row])}'] = int(thisLine[DemandVolume])
            marketWatchDict[thisID][f'SupplyVolume{int(thisLine[Row])}'] = int(thisLine[SupplyVolume])

    for ID in tuple(marketWatchDict.keys()):

        if "SupplyNumber5" not in marketWatchDict[ID]:
            del marketWatchDict[ID]
            continue
        if "SupplyNumber4" not in marketWatchDict[ID]:
            del marketWatchDict[ID]
            continue
        if "SupplyNumber3" not in marketWatchDict[ID]:
            del marketWatchDict[ID]
            continue
        if "SupplyNumber2" not in marketWatchDict[ID]:
            del marketWatchDict[ID]
            continue
        if "SupplyNumber1" not in marketWatchDict[ID]:
            del marketWatchDict[ID]
            continue

    return marketWatchDict

def get_marketWatch_data_tse_method(init= 0, heven= 0, refid= 0) -> dict:
    '''returns MarketWatchData as a dict whose keys is ticker Ids'''
    
    if init == 1:
        url = defParam.marketWatchInitUrl
    else:   
        url = defParam.MarketWatchPlusUrl.format(5*floor(heven/5), 25*floor(refid/25))

    # print(url)
    csvData = getCsvData(url, splitters= ['@', ';', ','])
    
    pricesData = csvData[2]
    ordersBoardData = csvData[3]
    refid = int(csvData[4][0][0]) if csvData[4][0][0] != '0' and int(csvData[4][0][0]) > refid else refid 
    heven = 0

    marketWatchDict = {}

    firstTimeLength = 23
    ID = 0
    heven1 = 4
    FirstPrice1 = 5
    TodayPrice1 = 6
    LastPrice1 = 7
    Volume1 = 9
    MinPrice1 = 11
    MaxPrice1 = 12
    YesterdayPrice1 = 13
    BaseVolume = 15
    MaxAllowedPrice1 = 19
    MinAllowedPrice1 = 20
    ShareNumber1 = 21

    nextTimesLength = 10
    heven2 = 1
    FirstPrice2 = 2
    TodayPrice2 = 3
    LastPrice2 = 4
    Volume2 = 6
    MinPrice2 = 8
    MaxPrice2 = 9

    OrdersLineLength = 8
    Row = 1
    SupplyNumber = 2
    DemandNumber = 3
    DemandPrice = 4
    SupplyPrice = 5
    DemandVolume = 6
    SupplyVolume = 7

    for thisLine in pricesData:

        if (len(thisLine) == firstTimeLength):
            thisID = int(thisLine[ID])
            marketWatchDict[thisID] = {'Constant': {}, 'Variable': {}, 'OrdersBoard': {}}
            marketWatchDict[thisID]['Variable']['FirstPrice'] = int(thisLine[FirstPrice1])
            marketWatchDict[thisID]['Variable']['TodayPrice'] = int(thisLine[TodayPrice1])
            marketWatchDict[thisID]['Variable']['LastPrice'] = int(thisLine[LastPrice1])
            marketWatchDict[thisID]['Variable']['Volume'] = int(thisLine[Volume1])
            marketWatchDict[thisID]['Variable']['MinPrice'] = int(thisLine[MinPrice1])
            marketWatchDict[thisID]['Variable']['MaxPrice'] = int(thisLine[MaxPrice1])
            marketWatchDict[thisID]['Constant']['YesterdayPrice'] = int(thisLine[YesterdayPrice1])
            marketWatchDict[thisID]['Constant']['BaseVolume'] = int(thisLine[BaseVolume])
            marketWatchDict[thisID]['Constant']['MaxAllowedPrice'] = int(float(thisLine[MaxAllowedPrice1]))
            marketWatchDict[thisID]['Constant']['MinAllowedPrice'] = int(float(thisLine[MinAllowedPrice1]))
            marketWatchDict[thisID]['Constant']['ShareNumber'] = int(thisLine[ShareNumber1])

            heven = max(heven, int(thisLine[heven1]))

        if (len(thisLine) == nextTimesLength):
            thisID = int(thisLine[ID])
            if thisID not in marketWatchDict:
                marketWatchDict[thisID] = {'Constant': {}, 'Variable': {}, 'OrdersBoard': {}}
            marketWatchDict[thisID]['Variable']['FirstPrice'] = int(thisLine[FirstPrice2])
            marketWatchDict[thisID]['Variable']['TodayPrice'] = int(thisLine[TodayPrice2])
            marketWatchDict[thisID]['Variable']['LastPrice'] = int(thisLine[LastPrice2])
            marketWatchDict[thisID]['Variable']['Volume'] = int(thisLine[Volume2])
            marketWatchDict[thisID]['Variable']['MinPrice'] = int(thisLine[MinPrice2])
            marketWatchDict[thisID]['Variable']['MaxPrice'] = int(thisLine[MaxPrice2])

            heven = max(heven, int(thisLine[heven2]))

    for thisLine in ordersBoardData:
        if (len(thisLine) == OrdersLineLength):
            thisID = int(thisLine[ID])
            if thisID not in marketWatchDict:
                marketWatchDict[thisID] = {'Constant': {}, 'Variable': {}, 'OrdersBoard': {}}
            marketWatchDict[thisID]['OrdersBoard'][f'SupplyNumber{int(thisLine[Row])}'] = int(thisLine[SupplyNumber])
            marketWatchDict[thisID]['OrdersBoard'][f'DemandNumber{int(thisLine[Row])}'] = int(thisLine[DemandNumber])
            marketWatchDict[thisID]['OrdersBoard'][f'DemandPrice{int(thisLine[Row])}'] = int(thisLine[DemandPrice])
            marketWatchDict[thisID]['OrdersBoard'][f'SupplyPrice{int(thisLine[Row])}'] = int(thisLine[SupplyPrice])
            marketWatchDict[thisID]['OrdersBoard'][f'DemandVolume{int(thisLine[Row])}'] = int(thisLine[DemandVolume])
            marketWatchDict[thisID]['OrdersBoard'][f'SupplyVolume{int(thisLine[Row])}'] = int(thisLine[SupplyVolume])

    return {'Data': marketWatchDict, 'Heven': heven, 'Refid': refid}

def get_intra_day_price(ID):

    url = f"http://www.tsetmc.com/tsev2/chart/data/IntraDayPrice.aspx?i={ID}"

    data = getCsvData(url)

    times = []
    openPrices = []
    closePrices = []
    highPrices = []
    lowPrices = []

    for item in data:
        times.append(item[0])
        highPrices.append(int(item[1]))
        lowPrices.append(int(item[2]))
        openPrices.append(int(item[3]))
        closePrices.append(int(item[4]))

    intra_day_price = {'Time': times, 'OpenPrice': openPrices, 'ClosePrice': closePrices, 'HighPrice': highPrices, 'LowPrice': lowPrices}

    return intra_day_price