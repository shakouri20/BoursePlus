
import json
from Domain.Enums.QueryOutPutType import queryOutPutType
from Infrastructure.Repository.TickerRepository import ticker_repo

ticker_repo().write_rahavard_entity_ID()

tickersData = ticker_repo().read_list_of_tickers(tickerTypes= [1, 3], outPutType= queryOutPutType.DictDict)
IDs = list(tickersData.keys())[:]

finalData = {}
for ID in IDs:
    if tickersData[ID]['RahavardEntityID'] != None:
        finalData[tickersData[ID]['FarsiTicker']] = tickersData[ID]['RahavardEntityID']


with open(r"E:\Skill\JavaScript\EasyTrader Extension\RahavardEntityID.json", "w") as outfile:
        json.dump(finalData, outfile)