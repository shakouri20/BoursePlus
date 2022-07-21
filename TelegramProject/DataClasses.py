
from cmath import nan


class signal:
    def __init__(self) -> None:
        self.time = None
        self.ID = None
        self.filterName = None
        self.signalSpec = None
        self.messageID = None

class ctItems:
        def __init__(self) -> None:
            self.RealBuyNumber = nan
            self.CorporateBuyNumber = nan
            self.RealBuyVolume = nan
            self.CorporateBuyVolume = nan
            self.RealSellNumber = nan
            self.CorporateSellNumber = nan
            self.RealSellVolume = nan
            self.CorporateSellVolume = nan

class pastData:
    def __init__(self) -> None:
        self.MonthlyValue = None
        self.WeeklyValue = None
        
        self.Tenkansen = None
        self.Kijunsen = None
        self.SpanA = None
        self.SpanB = None
        self.SpanAshifted = None
        self.SpanBshifted = None
        self.TenkansenLong = None
        self.KijunsenLong = None

        self.maxPrice8 = None
        self.minPrice8 = None
        self.maxPrice25 = None
        self.minPrice25 = None
        self.yesterdayMinPrice = None
        
        self.buyPercapitaAvg = None
        self.sellPercapitaAvg = None
