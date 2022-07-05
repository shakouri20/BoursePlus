from Domain.Enums.OnlineColumns import onlineColumns
from Domain.Enums.QueryOutPutType import queryOutPutType
from Domain.Enums.TableType import tableType
from Infrastructure.Repository.OfflineDataRepository import offlineData_repo
from Infrastructure.Repository.OnlineDataRepository import onlineData_repo
from Application.Services.ReadData.ReadOffline.ReadOfflineServices import read_offline_services
from Application.Services.ReadData.ReadOnline.OnlineDataHandler import onlineDataHandler
from Application.Utility.DateConverter import *
from Infrastructure.Repository.TickerRepository import ticker_repo
from Application.Services.DataProcess import get_data_from_web
from datetime import date, datetime
import winsound
from tkinter import *
from tkinter import ttk

class onlineTradeUI:

    def __init__(self) -> None:
        
        self.period = 10000
        self.tickersData = ticker_repo().read_list_of_tickers(tickerTypes= [1], marketTypes= list(range(1, 9)), outPutType= queryOutPutType.DictDict)
        self.IDs = list(self.tickersData.keys())
        self.cache = onlineDataHandler(self.IDs)
        self.create_offline_data(self.IDs)
        self.create_UI()

    def create_UI(self):
        
        self.root = Tk()

        self.root.geometry("1700x1350")
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("mystyle.Treeview", rowheight=20, highlightthickness=0, bd=0, font=('Calibri', 11,'bold'))
        style.configure("mystyle.Treeview.Heading", font=('Calibri', 10,'bold'))

        self.tree = ttk.Treeview(self.root, column=("c1", "c2", "c3", "c4", "c5", "c6", "c7", "c8", "c9", "c10", "c11"), show='headings', height=20, style="mystyle.Treeview")
        # , "c12", "c13", "c14"
        self.tree.column("#1", anchor=CENTER, width= 50)
        self.tree.column("#2", anchor=CENTER, width= 70)
        self.tree.column("#3", anchor=CENTER, width= 70)
        self.tree.column("#4", anchor=CENTER, width= 80)
        self.tree.column("#5", anchor=CENTER, width= 130)
        self.tree.column("#6", anchor=CENTER, width= 130)
        self.tree.column("#7", anchor=CENTER, width= 130)
        self.tree.column("#8", anchor=CENTER, width= 130)
        self.tree.column("#9", anchor=CENTER, width= 80)
        self.tree.column("#10", anchor=CENTER, width= 80)
        self.tree.column("#11", anchor=CENTER, width= 80)
        # self.tree.column("#12", anchor=CENTER, width= 80)
        # self.tree.column("#13", anchor=CENTER, width= 80)
        # self.tree.column("#14", anchor=CENTER, width= 80)

        self.tree.heading("#1", text="شماره")
        self.tree.heading("#2", text="سهم")
        self.tree.heading("#3", text="قیمت")
        self.tree.heading("#4", text="فاکتور سیگنال")
        self.tree.heading("#5", text="سرانه خرید لحظه ای")
        self.buyPerCapitaDifLimit = 30
        self.tree.heading("#6", text="قدرت خریدار لحظه ای")
        self.realPowerDifLimit = 1.5
        self.tree.heading("#7", text="حجم لحظه ای")
        self.volumeDifLimit = 5
        self.tree.heading("#8", text="تغییر قیمت")
        self.priceChangeLimit = 1
        self.tree.heading("#9", text="سرانه خرید")
        self.buyPerCapitaLimit = 30
        self.tree.heading("#10", text="قدرت خریدار")
        self.realPowerLimit = 1.5
        self.tree.heading("#11", text="حجم هفتگی")
        self.weekVolumeLimit = 1.5

        self.tree.grid(row=0, column=0, sticky='NSEW')

        self.tree.pack()

        self.root.after(self.period, self.action)
        self.root.mainloop()

    def create_offline_data(self, IDs):

        data = offlineData_repo().read_last_N_offlineData('all', Num=30, IDList=IDs, table= tableType.OfflineData.value)
        self.offlineData = {}

        for ID in data:

            self.offlineData[ID] = {}
            
            volumes = [data[ID]['Value'][i]/data[ID]['TodayPrice'][i] for i in range(len(data[ID]['Value']))]
            monthlyVolume = sum(volumes)/len(volumes)
            weeklyVolume = sum(volumes[-7:])/len(volumes[-7:])
            volumes3day = volumes[-3:]
            realPower3day = data[ID]['RealPower'][-3:]
            
            if self.tickersData[ID]['MarketTypeID'] in (1, 2, 3, 4):
                self.offlineData[ID]['MarketType'] = 1
            elif self.tickersData[ID]['MarketTypeID'] in (5, 6, 7):
                self.offlineData[ID]['MarketType'] = 2
            elif self.tickersData[ID]['MarketTypeID'] == 8:
                self.offlineData[ID]['MarketType'] = 3

            self.offlineData[ID]['MonthlyVolume'] = monthlyVolume
            self.offlineData[ID]['WeeklyVolume'] = weeklyVolume
            # self.offlineData[ID]['RecentVolume'] = sum(volumes3day)
            # self.offlineData[ID]['RecentRealPower'] = sum([volumes3day[i]*realPower3day[i] for i in range(len(volumes3day))])/sum(volumes3day)
            
    def action(self):

        # winsound.Beep(500, 200)
        self.tree.delete(*self.tree.get_children())

        while True:
            try:
                cacheDataDict = get_data_from_web()[1]
                break
            except:
                continue

        if cacheDataDict != None:

            self.cache.update(cacheDataDict)

            # print(datetime.now())

            # run strategy
            self.vecLen = 15 #30

            self.lastPrice = self.cache.lastPrice(num= 1)
            self.lastPricePrc = self.cache.lastPricePRC(num= self.vecLen*2)
            self.maxAllowedPrice = self.cache.maxAllowedPrice()
            
            self.volume = self.cache.volume(num=self.vecLen)

            self.buyPerCapita = self.cache.perCapitaBuy(num= 1)
            self.sellPerCapita = self.cache.perCapitaSell(num= 1)
            realValues = self.cache.realValues(num= self.vecLen)
            self.realBuyVolume = realValues[onlineColumns.RealBuyVolume.value]
            self.realBuyNumber = realValues[onlineColumns.RealBuyNumber.value]
            self.realSellVolume = realValues[onlineColumns.RealSellVolume.value]
            self.realSellNumber = realValues[onlineColumns.RealSellNumber.value]

            self.realValues = self.cache.realValues(num= self.vecLen)

            row = self.cache.row1(num= 1)
            self.demandVolume1 = row[onlineColumns.DemandVolume1.value]
            self.supplyVolume1 = row[onlineColumns.SupplyVolume1.value]

            availableIDs = list(self.lastPrice.keys())

            self.signaledData = []
            self.time = datetime.now()
            for ID in availableIDs:
                # try:
                    self.single_ticker_calc(ID)
                # except:
                #     winsound.Beep(500, 2000)
                #     print('Error')

            self.signaledData.sort(key=lambda tup: (tup[2], tup[10] ), reverse=True)

            for i in range(len(self.signaledData)):
                self.tree.insert('', 'end', text="1", values=[i+1] + self.signaledData[i])
            
            self.root.after(self.period, self.action) 

    def single_ticker_calc(self, ID):
        
        if self.supplyVolume1[ID][-1] == 0 and self.demandVolume1[ID][-1] > self.offlineData[ID]['WeeklyVolume'] /3:
            return

        signalFactor = 0
        #################################################
        tickerName = str(ticker_repo().read_by_ID(ID)['FarsiTicker'])+' -'+str(self.offlineData[ID]['MarketType'])
        #################################################
        buyPerCapita = self.buyPerCapita[ID][-1]
        sellPerCapita = self.sellPerCapita[ID][-1]
        realPower = round(buyPerCapita/sellPerCapita, 1) if sellPerCapita != 0 else 1
        
        if buyPerCapita > self.buyPerCapitaLimit:
            buyPerCapita = '( ' + str(buyPerCapita) + ' )'
            signalFactor += 1
        else:
            buyPerCapita = str(buyPerCapita)

        if realPower > self.realPowerLimit:
            realPower = '( ' + str(realPower) + ' )'
            signalFactor += 1
        else:
            realPower = str(realPower)
        #################################################
        weekVolume = round(self.volume[ID][-1]/self.offlineData[ID]['WeeklyVolume'], 1)
        if weekVolume > self.weekVolumeLimit:
            weekVolume = '( ' + str(weekVolume) + ' )'
            signalFactor += 1
        else:
            weekVolume = str(weekVolume)
        #################################################
        buyPerCapitaDif = 0
        if self.realBuyNumber[ID][-1] != self.realBuyNumber[ID][0]:
            buyPerCapitaDif = max(int((self.realBuyVolume[ID][-1]-self.realBuyVolume[ID][0])/(self.realBuyNumber[ID][-1]-self.realBuyNumber[ID][0]) * self.lastPrice[ID][-1] / 10**7), 0)

        sellPerCapitaDif = 0
        if self.realSellNumber[ID][-1] != self.realSellNumber[ID][0]:
            sellPerCapitaDif = max(int((self.realSellVolume[ID][-1]-self.realSellVolume[ID][0])/(self.realSellNumber[ID][-1]-self.realSellNumber[ID][0]) * self.lastPrice[ID][-1] / 10**7), 0)
        
        realPowerDif = round(buyPerCapitaDif/sellPerCapitaDif, 1) if sellPerCapitaDif != 0 else 1

        if realPowerDif < 1: return

        if buyPerCapitaDif > self.buyPerCapitaDifLimit:
            signalFactor += min(3, int(buyPerCapitaDif/self.buyPerCapitaDifLimit))
            buyPerCapitaDif = '( ' + str(buyPerCapitaDif) + ' )'
        else:
            buyPerCapitaDif = str(buyPerCapitaDif)

        if realPowerDif > self.realPowerDifLimit:
            signalFactor += min(3, int(realPowerDif/10+1))
            realPowerDif = '( ' + str(realPowerDif) + ' )'

        else:
            realPowerDif = str(realPowerDif)
        #################################################
        baseVolume = self.offlineData[ID]['MonthlyVolume']/(3.5*12)
        if len(self.volume[ID]) == self.vecLen or self.time.hour == 9 and self.time.minute > 15 or self.time.hour > 9:
            volumeDif = round((self.volume[ID][-1]-self.volume[ID][0])/baseVolume, 1)
        else:
            volumeDif = round(self.volume[ID][-1]/baseVolume, 1)
        if volumeDif > self.volumeDifLimit:
            signalFactor += min(3, int(volumeDif/10+1))
            volumeDif = '( ' + str(volumeDif) + ' )'
        else:
            return
        # volumeDif = str(volumeDif)
        #################################################
        priceChange = round(self.lastPricePrc[ID][-1]-self.lastPricePrc[ID][0], 1)
        if priceChange > self.priceChangeLimit:
            priceChange = '( ' + str(priceChange) + ' )'
            signalFactor += 1
        else:
            priceChange = str(priceChange)
        #################################################
        if self.supplyVolume1[ID][-1] == 0:
            price = str(round(self.lastPricePrc[ID][-1], 1)) + ' -BQ'
        elif self.demandVolume1[ID][-1] == 0:
            price = str(round(self.lastPricePrc[ID][-1], 1)) + ' -SQ'
        else:
            price = str(round(self.lastPricePrc[ID][-1], 1))
        #################################################
        try:
            buyPerCapitaDifNum = int(buyPerCapitaDif)
        except:
            buyPerCapitaDifNum = int(buyPerCapitaDif.split('( ')[1].split(' )')[0])
        #################################################

        if signalFactor >= 4:
            self.signaledData.append([tickerName, price, signalFactor, buyPerCapitaDif, realPowerDif, volumeDif, priceChange, 
                buyPerCapita, realPower, weekVolume, buyPerCapitaDifNum])

a = onlineTradeUI()
