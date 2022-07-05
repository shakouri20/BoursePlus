import os
from SqlServerDataBaseLib import DatabaseConnection
from request_session import requests_retry_session
import datetime
import time

DB = DatabaseConnection()

DB.connect()
print('started')
while True:
    if datetime.datetime.now() > datetime.datetime(2021, 8, 9, 12, 30, 0):
        break
    if datetime.datetime.now() > datetime.datetime(2021, 8, 7, 9, 0, 0):
        try:
            # Download ClientTypes File
            url = r'http://www.tsetmc.com/tsev2/data/ClientTypeAll.aspx'
            session = requests_retry_session()
            response = session.get(url, timeout=5)
        except:
            continue
        # read ClientTypes file
        ClientTypesData = response.text.split(";")
        ClientTypesData = [row.split(",") for row in ClientTypesData]
        
        try:
            # Download Prices File
            url = r'http://www.tsetmc.com/tsev2/data/MarketWatchInit.aspx?h=0&r=1'
            session = requests_retry_session()
            response = session.get(url, timeout=5)
        except:
            continue
        # read ClientTypes file
        PricesData = response.text.split(";")
        PricesData = [row.split(",") for row in PricesData]

        ID = 0
        RealBuyNumber = 1
        CorporateBuyNumber = 2
        RealBuyVolume = 3
        CorporateBuyVolume = 4
        RealSellNumber = 5
        CorporateSellNumber = 6
        RealSellVolume = 7
        CorporateSellVolume = 8

        TodayPrice = 6
        LastPrice = 7
        Number = 8
        Volume = 9
        MinPrice = 11
        MaxPrice = 12
        YesterdayPrice = 13
        EPS = 14
        BaseVolume = 15
        MaxAllowedPrice = 19
        MinAllowedPrice = 20
        ShareNumber =  21

        Time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        for i in range(len(ClientTypesData)):

            # find the ID from Prices Data and insert into database
            for j in range(1, len(PricesData)):

                if len(PricesData[j]) != len(PricesData[1]):
                    break

                if PricesData[j][ID] == ClientTypesData[i][ID]:
                    #print(PricesData[j][ID])
                    # reform ClientTypes data
                    for k in range(ID, CorporateSellVolume + 1):
                        ClientTypesData[i][k] = int(float(ClientTypesData[i][k].replace(' ', '').replace('\n', '').replace('\t', '')))
            
                    # reform Prices data
                    PricesData[j][TodayPrice] = int(float(PricesData[j][TodayPrice].replace(' ', '').replace('\n', '').replace('\t', '')))
                    PricesData[j][LastPrice] = int(float(PricesData[j][LastPrice].replace(' ', '').replace('\n', '').replace('\t', '')))
                    PricesData[j][Number] = int(float(PricesData[j][Number].replace(' ', '').replace('\n', '').replace('\t', '')))
                    PricesData[j][Volume] = int(float(PricesData[j][Volume].replace(' ', '').replace('\n', '').replace('\t', '')))
                    PricesData[j][MinPrice] = int(float(PricesData[j][MinPrice].replace(' ', '').replace('\n', '').replace('\t', '')))
                    PricesData[j][MaxPrice] = int(float(PricesData[j][MaxPrice].replace(' ', '').replace('\n', '').replace('\t', '')))
                    PricesData[j][YesterdayPrice] = int(float(PricesData[j][YesterdayPrice].replace(' ', '').replace('\n', '').replace('\t', '')))
                    if PricesData[j][EPS].replace(' ', '').replace('\n', '').replace('\t', '').isnumeric():
                        PricesData[j][EPS] = int(float(PricesData[j][EPS].replace(' ', '').replace('\n', '').replace('\t', '')))
                    else:
                        PricesData[j][EPS] = 0
                    PricesData[j][BaseVolume] = int(float(PricesData[j][BaseVolume].replace(' ', '').replace('\n', '').replace('\t', '')))
                    PricesData[j][MaxAllowedPrice] = int(float(PricesData[j][MaxAllowedPrice].replace(' ', '').replace('\n', '').replace('\t', '')))
                    PricesData[j][MinAllowedPrice] = int(float(PricesData[j][MinAllowedPrice].replace(' ', '').replace('\n', '').replace('\t', '')))

                    cmd = '''
                    INSERT INTO OnlineData
                    VALUES ({}, '{}', {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {})
                    '''.format(PricesData[j][ID], Time, PricesData[j][TodayPrice], PricesData[j][LastPrice], PricesData[j][Number],\
                        PricesData[j][Volume], PricesData[j][MinPrice], PricesData[j][MaxPrice], PricesData[j][YesterdayPrice], \
                        PricesData[j][EPS], PricesData[j][BaseVolume], PricesData[j][MaxAllowedPrice], PricesData[j][MinAllowedPrice], \
                        PricesData[j][ShareNumber], ClientTypesData[i][RealBuyNumber], ClientTypesData[i][CorporateBuyNumber], \
                        ClientTypesData[i][RealBuyVolume], ClientTypesData[i][CorporateBuyVolume], ClientTypesData[i][RealSellNumber],\
                        ClientTypesData[i][CorporateSellNumber], ClientTypesData[i][RealSellVolume],\
                        ClientTypesData[i][CorporateSellVolume])

                    DB.execute(cmd)

                    break
        print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        DB.commit()

    time.sleep(15)
DB.close()
# os.system("shutdown /h") #hibernate