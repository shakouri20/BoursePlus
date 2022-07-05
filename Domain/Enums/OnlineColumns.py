import enum

class onlineColumns(enum.Enum):

    # basic columns
    Time = 'Time'
    TodayPrice = 'TodayPrice'
    LastPrice = 'LastPrice'
    Number = 'Number'
    Volume = 'Volume'
    MinPrice = 'MinPrice'
    MaxPrice  = 'MaxPrice'
    YesterdayPrice = 'YesterdayPrice'
    MaxAllowedPrice= 'MaxAllowedPrice'
    MinAllowedPrice = 'MinAllowedPrice'
    RealBuyNumber = 'RealBuyNumber'
    CorporateBuyNumber = 'CorporateBuyNumber'
    RealBuyVolume = 'RealBuyVolume'
    CorporateBuyVolume = 'CorporateBuyVolume'
    RealSellNumber = 'RealSellNumber'
    CorporateSellNumber = 'CorporateSellNumber'
    RealSellVolume = 'RealSellVolume'
    CorporateSellVolume = 'CorporateSellVolume'

    SupplyNumber1 = 'SupplyNumber1'
    SupplyVolume1 = 'SupplyVolume1'
    SupplyPrice1 = 'SupplyPrice1'
    DemandPrice1 = 'DemandPrice1'
    DemandVolume1 = 'DemandVolume1'
    DemandNumber1 = 'DemandNumber1'
    
    SupplyNumber2 = 'SupplyNumber2'
    SupplyVolume2 = 'SupplyVolume2'
    SupplyPrice2 = 'SupplyPrice2'
    DemandPrice2 = 'DemandPrice2'
    DemandVolume2 = 'DemandVolume2'
    DemandNumber2 = 'DemandNumber2'
    
    SupplyNumber3 = 'SupplyNumber3'
    SupplyVolume3 = 'SupplyVolume3'
    SupplyPrice3 = 'SupplyPrice3'
    DemandPrice3 = 'DemandPrice3'
    DemandVolume3 = 'DemandVolume3'
    DemandNumber3 = 'DemandNumber3'
    
    SupplyNumber4 = 'SupplyNumber4'
    SupplyVolume4 = 'SupplyVolume4'
    SupplyPrice4 = 'SupplyPrice4'
    DemandPrice4 = 'DemandPrice4'
    DemandVolume4 = 'DemandVolume4'
    DemandNumber4 = 'DemandNumber4'

    SupplyNumber5 = 'SupplyNumber5'
    SupplyVolume5 = 'SupplyVolume5'
    SupplyPrice5 = 'SupplyPrice5'
    DemandPrice5 = 'DemandPrice5'
    DemandVolume5 = 'DemandVolume5'
    DemandNumber5 = 'DemandNumber5'

    LastTradeTime = 'LastTradeTime'

    # added columns
    TodayPricePRC = 'TodayPricePRC'
    LastPricePRC = 'LastPricePRC'

    PerCapitaBuy = 'PerCapitaBuy'
    PerCapitaSell = 'PerCapitaSell'
    PerCapitaBuyDif = 'PerCapitaBuyDif'
    PerCapitaSellDif = 'PerCapitaSellDif'

    RealPower = 'RealPower'
    RealPowerDif = 'RealPowerDif'

    VolumeDif = 'VolumeDif'

    RPVP = 'RPVP'

    # MarketInfo
    TickersNumber = 'TickersNumber'

    PositiveTickersPRC =  'PositiveTickersPRC'
    SellQueueTickersPRC = 'SellQueueTickersPRC'
    BuyQueueTickersPRC = 'BuyQueueTickersPRC'

    LastPricePRCAverge = 'LastPricePRCAverge'
    TodayPricePRCAverage = 'TodayPricePRCAverage'

    TotalValue = 'TotalValue'
    SellQueuesValue = 'SellQueuesValue'
    BuyQueuesValue = 'BuyQueuesValue'
    RealMoneyEntryValue = 'RealMoneyEntryValue'

    DemandValue = 'DemandValue'
    SupplyValue = 'SupplyValue'

    RealPowerLog = 'RealPowerLog'

    RealBuyValue = 'RealBuyValue'
    RealSellValue = 'RealSellValue'
