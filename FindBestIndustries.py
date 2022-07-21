from Application.Services.ReadData.ReadOffline.RatioService import tickerCompare
from Application.Utility.DateConverter import *
from Domain.Enums.QueryOutPutType import queryOutPutType
from Infrastructure.Repository.TickerRepository import ticker_repo

fromDate = '1401-02-01'
toDate = '1402-01-01'

industries = ticker_repo().read_list_of_tickers(tickerTypes=[2], industryTypes= list(range(100)), outPutType= queryOutPutType.DictDict)

trendIndustries = {}
for industryID in industries:
    print(industries[industryID]['FarsiTicker'][::-1])
    tickersData = tickerCompare(industryID, 67130298613737946, fromDate, toDate)
    if tickersData.ratio[-1] > tickersData.ratioMa1[-1] and tickersData.ratioMacd[-1] > 50:
        trendIndustries[industries[industryID]['FarsiTicker']] = []
        
        industryTickers = ticker_repo().read_list_of_tickers(tickerTypes=[1], industryTypes= [industries[industryID]['IndustryTypeID']], outPutType= queryOutPutType.DictDict)

        for tickerID in industryTickers:
            try:
                tickersData = tickerCompare(tickerID, industryID, fromDate, toDate)
                if tickersData.ratio[-2] < tickersData.ratioMa1[-2] and tickersData.ratio[-1] > tickersData.ratioMa1[-1] and tickersData.ratioMacd[-1] > 50:
                    trendIndustries[industries[industryID]['FarsiTicker']].append(industryTickers[tickerID]['FarsiTicker'])
                    x = 1 
            except:
                pass


x = 1