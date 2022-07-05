from Application.Utility.Indicators.IndicatorService import calculateIchimoko
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
import pyperclip

class onlineTradeUI:

    def __init__(self) -> None:
        
        self.period = 10000
        self.run = True
        self.buyPerCapitaDifLimit = 30
        self.realPowerDifLimit = 1.5
        self.volumeDifLimit = 5
        self.priceChangeLimit = 1
        self.buyPerCapitaLimit = 30
        self.realPowerLimit = 1.5
        self.weekVolumeLimit = 1.5

        self.tickersData = ticker_repo().read_list_of_tickers(tickerTypes= [1], marketTypes= list(range(1, 8)), outPutType= queryOutPutType.DictDict)
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

        self.tree1 = ttk.Treeview(self.root, column=("c1", "c2", "c3", "c4", "c5", "c6", "c7", "c8", "c9", "c10", "c11", "c12", "c13", "c14", "c15", "c16", "c17"),
            show='headings', height=14, style="mystyle.Treeview")
        self.tree1.column("#1", anchor=CENTER, width= 50)
        self.tree1.column("#2", anchor=CENTER, width= 70)
        self.tree1.column("#3", anchor=CENTER, width= 70)
        self.tree1.column("#4", anchor=CENTER, width= 80)
        self.tree1.column("#5", anchor=CENTER, width= 80)
        self.tree1.column("#6", anchor=CENTER, width= 80)
        self.tree1.column("#7", anchor=CENTER, width= 80)
        self.tree1.column("#8", anchor=CENTER, width= 80)
        self.tree1.column("#9", anchor=CENTER, width= 80)
        self.tree1.column("#10", anchor=CENTER, width= 80)
        self.tree1.column("#11", anchor=CENTER, width= 80)
        self.tree1.column("#12", anchor=CENTER, width= 80)
        self.tree1.column("#13", anchor=CENTER, width= 80)
        self.tree1.column("#14", anchor=CENTER, width= 80)
        self.tree1.column("#15", anchor=CENTER, width= 80)
        self.tree1.column("#16", anchor=CENTER, width= 80)
        self.tree1.column("#17", anchor=CENTER, width= 80)

        self.tree1.heading("#1", text="شماره")
        self.tree1.heading("#2", text="سهم")
        self.tree1.heading("#3", text="قیمت")
        self.tree1.heading("#4", text="حجم صف")
        self.tree1.heading("#5", text="فاکتور سیگنال")
        self.tree1.heading("#6", text="س.خ.لحظه ای")
        self.tree1.heading("#7", text="ق.خ.لحظه ای")
        self.tree1.heading("#8", text="ح.لحظه ای")
        self.tree1.heading("#9", text="تغییر قیمت")
        self.tree1.heading("#10", text="سرانه خرید")
        self.tree1.heading("#11", text="قدرت خریدار")
        self.tree1.heading("#12", text="حجم هفتگی")
        self.tree1.heading("#13", text="تنکانسن")
        self.tree1.heading("#14", text="کیجونسن")
        self.tree1.heading("#15", text="اسپن بالا")
        self.tree1.heading("#16", text="اسپن پایین")
        self.tree1.heading("#17", text="چیکواسپن")

        self.tree1.pack()

        self.tree1.bind("<Button-1>", self.onClick1)

        ######################
        self.tree2 = ttk.Treeview(self.root, column=("c1", "c2", "c3", "c4", "c5", "c6", "c7", "c8", "c9", "c10", "c11", "c12", "c13", "c14", "c15", "c16", "c17"),
            show='headings', height=14, style="mystyle.Treeview")
        self.tree2.column("#1", anchor=CENTER, width= 50)
        self.tree2.column("#2", anchor=CENTER, width= 70)
        self.tree2.column("#3", anchor=CENTER, width= 70)
        self.tree2.column("#4", anchor=CENTER, width= 80)
        self.tree2.column("#5", anchor=CENTER, width= 80)
        self.tree2.column("#6", anchor=CENTER, width= 80)
        self.tree2.column("#7", anchor=CENTER, width= 80)
        self.tree2.column("#8", anchor=CENTER, width= 80)
        self.tree2.column("#9", anchor=CENTER, width= 80)
        self.tree2.column("#10", anchor=CENTER, width= 80)
        self.tree2.column("#11", anchor=CENTER, width= 80)
        self.tree2.column("#12", anchor=CENTER, width= 80)
        self.tree2.column("#13", anchor=CENTER, width= 80)
        self.tree2.column("#14", anchor=CENTER, width= 80)
        self.tree2.column("#15", anchor=CENTER, width= 80)
        self.tree2.column("#16", anchor=CENTER, width= 80)
        self.tree2.column("#17", anchor=CENTER, width= 80)

        self.tree2.heading("#1", text="شماره")
        self.tree2.heading("#2", text="سهم")
        self.tree2.heading("#3", text="قیمت")
        self.tree2.heading("#4", text="حجم صف")
        self.tree2.heading("#5", text="فاکتور سیگنال")
        self.tree2.heading("#6", text="س.خ.لحظه ای")
        self.tree2.heading("#7", text="ق.خ.لحظه ای")
        self.tree2.heading("#8", text="ح.لحظه ای")
        self.tree2.heading("#9", text="تغییر قیمت")
        self.tree2.heading("#10", text="سرانه خرید")
        self.tree2.heading("#11", text="قدرت خریدار")
        self.tree2.heading("#12", text="حجم هفتگی")
        self.tree2.heading("#13", text="تنکانسن")
        self.tree2.heading("#14", text="کیجونسن")
        self.tree2.heading("#15", text="اسپن بالا")
        self.tree2.heading("#16", text="اسپن پایین")
        self.tree2.heading("#17", text="چیکواسپن")

        self.tree2.pack()

        self.tree2.bind("<Button-1>", self.onClick2)

        runBtn = Button(self.root, text = 'Run', bd = '5',
                                command = self.runUI)
        runBtn.pack(side = 'top')

        runBtn = Button(self.root, text = 'Pause', bd = '5',
                                command = self.pauseUI)
        runBtn.pack(side = 'top')
        
        self.root.after(self.period, self.action)
        self.root.mainloop()

    def create_offline_data(self, IDs):

        data = offlineData_repo().read_last_N_offlineData('all', Num=100, IDList=IDs, table= tableType.OfflineData.value)
        self.offlineData = {}

        for ID in data:

            
            volumes = [data[ID]['Value'][i]/data[ID]['TodayPrice'][i] for i in range(len(data[ID]['Value']))]
            monthlyVolume = sum(volumes)/len(volumes)
            weeklyVolume = sum(volumes[-7:])/len(volumes[-7:])

            ich = calculateIchimoko(data[ID]['HighPrice'], data[ID]['LowPrice'], 9, 26, 52, True, False)

            tenkansen = ich[0][-1]
            kijunsen = ich[1][-1]
            spanA = ich[2][-1]
            spanB = ich[3][-1]
                
            if len(ich[2]) > 26:
                spanAshifted = ich[2][-26]
                spanBshifted = ich[3][-26]
            else:
                continue
            
            # write 
            self.offlineData[ID] = {}
            if self.tickersData[ID]['MarketTypeID'] in (1, 2, 3, 4):
                self.offlineData[ID]['MarketType'] = 1
            elif self.tickersData[ID]['MarketTypeID'] in (5, 6, 7):
                self.offlineData[ID]['MarketType'] = 2
            elif self.tickersData[ID]['MarketTypeID'] == 8:
                self.offlineData[ID]['MarketType'] = 3

            self.offlineData[ID]['MonthlyVolume'] = monthlyVolume
            self.offlineData[ID]['WeeklyVolume'] = weeklyVolume
            
            self.offlineData[ID]['Tenkansen'] = tenkansen
            self.offlineData[ID]['Kijunsen'] = kijunsen
            self.offlineData[ID]['SpanA'] = spanA
            self.offlineData[ID]['SpanB'] = spanB
            self.offlineData[ID]['SpanAshifted'] = spanAshifted
            self.offlineData[ID]['SpanBshifted'] = spanBshifted

            self.offlineData[ID]['yesterdayMinPrice'] = data[ID]['LowPrice'][-1]
                    
    def action(self):

        while True:
            try:
                cacheDataDict = get_data_from_web()[1]
                break
            except:
                continue

        if cacheDataDict != None:
            self.cache.update(cacheDataDict)

        if self.run:
            self.updateUI()
            
        self.root.after(self.period, self.action) 

    def single_ticker_calc(self, ID):
        
        # if self.supplyVolume1[ID][-1] == 0 and self.demandVolume1[ID][-1] > self.offlineData[ID]['WeeklyVolume'] /3:
        #     return

        # total data
        signalFactor1 = 0

        tickerName = str(ticker_repo().read_by_ID(ID)['FarsiTicker'])+' -'+str(self.offlineData[ID]['MarketType'])

        if self.supplyVolume1[ID][-1] == 0:
            queueRatio = str(round(self.demandVolume1[ID][-1] / self.offlineData[ID]['WeeklyVolume'], 1))
        elif self.demandVolume1[ID][-1] == 0:
            queueRatio = str(round(self.supplyVolume1[ID][-1] / self.offlineData[ID]['WeeklyVolume'], 1))
        else:
            queueRatio = '0'

        buyPerCapita = self.buyPerCapita[ID][-1]
        sellPerCapita = self.sellPerCapita[ID][-1]
        realPower = round(buyPerCapita/sellPerCapita, 1) if sellPerCapita != 0 else 1
        
        if buyPerCapita > self.buyPerCapitaLimit:
            buyPerCapitaStr = '( ' + str(buyPerCapita) + ' )'
            signalFactor1 += 1
        else:
            buyPerCapitaStr = str(buyPerCapita)

        if realPower > self.realPowerLimit:
            realPowerStr = '( ' + str(realPower) + ' )'
            signalFactor1 += 1
        else:
            realPowerStr = str(realPower)

        weekVolume = round(self.volume[ID][-1]/self.offlineData[ID]['WeeklyVolume'], 1)
        if weekVolume > self.weekVolumeLimit:
            weekVolumeStr = '( ' + str(weekVolume) + ' )'
            signalFactor1 += 1
        else:
            weekVolumeStr = str(weekVolume)

        # ichimoko
        lastPrice = self.lastPrice[ID][-1]

        tenkansenDif = round((lastPrice - self.offlineData[ID]['Tenkansen'])/self.offlineData[ID]['Tenkansen']*100, 1)
        if lastPrice > self.offlineData[ID]['Tenkansen'] and self.offlineData[ID]['yesterdayMinPrice'] < self.offlineData[ID]['Tenkansen']:
            tenkansenDifStr = '( ' + str(tenkansenDif) + ' )'
            signalFactor1 += 1
        else:
            tenkansenDifStr = str(tenkansenDif)

        KijunsenDif = round((lastPrice - self.offlineData[ID]['Kijunsen'])/self.offlineData[ID]['Kijunsen']*100, 1)
        if lastPrice > self.offlineData[ID]['Kijunsen'] and self.offlineData[ID]['yesterdayMinPrice'] < self.offlineData[ID]['Kijunsen']:
            KijunsenDifStr = '( ' + str(KijunsenDif) + ' )'
            signalFactor1 += 1
        else:
            KijunsenDifStr = str(KijunsenDif)

        spansMax = max(self.offlineData[ID]['SpanA'], self.offlineData[ID]['SpanB'])
        spansMin = min(self.offlineData[ID]['SpanA'], self.offlineData[ID]['SpanB'])
        upperSpanDif = round((lastPrice - spansMax)/spansMax*100, 1)
        lowerSpanDif = round((lastPrice - spansMin)/spansMin*100, 1)

        if lastPrice > spansMax and self.offlineData[ID]['yesterdayMinPrice'] < spansMax:
            upperSpanDifStr = '( ' + str(upperSpanDif) + ' )'
            signalFactor1 += 1
        else:
            upperSpanDifStr = str(upperSpanDif)

        if lastPrice > spansMin and self.offlineData[ID]['yesterdayMinPrice'] < spansMin:
            lowerSpanDifStr = '( ' + str(lowerSpanDif) + ' )'
            signalFactor1 += 1
        else:
            lowerSpanDifStr = str(lowerSpanDif)

        spansShiftedMax = max(self.offlineData[ID]['SpanAshifted'], self.offlineData[ID]['SpanBshifted'])
        chikoSpanCloudDif = round((lastPrice - spansShiftedMax)/spansShiftedMax*100, 1)

        # momentary data
        signalFactor2 = 0

        buyPerCapitaDif = 0
        if self.realBuyNumber[ID][-1] != self.realBuyNumber[ID][0]:
            buyPerCapitaDif = max(int((self.realBuyVolume[ID][-1]-self.realBuyVolume[ID][0])/(self.realBuyNumber[ID][-1]-self.realBuyNumber[ID][0]) * self.lastPrice[ID][-1] / 10**7), 0)

        sellPerCapitaDif = 0
        if self.realSellNumber[ID][-1] != self.realSellNumber[ID][0]:
            sellPerCapitaDif = max(int((self.realSellVolume[ID][-1]-self.realSellVolume[ID][0])/(self.realSellNumber[ID][-1]-self.realSellNumber[ID][0]) * self.lastPrice[ID][-1] / 10**7), 0)
        
        realPowerDif = round(buyPerCapitaDif/sellPerCapitaDif, 1) if sellPerCapitaDif != 0 else 1

        if buyPerCapitaDif > self.buyPerCapitaDifLimit:
            buyPerCapitaDifStr = '( ' + str(buyPerCapitaDif) + ' )'
            signalFactor2 += min(3, int(buyPerCapitaDif/self.buyPerCapitaDifLimit))
        else:
            buyPerCapitaDifStr = str(buyPerCapitaDif)

        if realPowerDif > self.realPowerDifLimit:
            realPowerDifStr = '( ' + str(realPowerDif) + ' )'
            signalFactor2 += min(3, int(realPowerDif/10+1))

        else:
            realPowerDifStr = str(realPowerDif)

        baseVolume = self.offlineData[ID]['MonthlyVolume']/(3.5*12)
        if len(self.volume[ID]) == self.vecLen or self.time.hour == 9 and self.time.minute > 15 or self.time.hour > 9:
            volumeDif = round((self.volume[ID][-1]-self.volume[ID][0])/baseVolume, 1)
        else:
            volumeDif = round(self.volume[ID][-1]/baseVolume, 1)
        if volumeDif > self.volumeDifLimit:
            volumeDifStr = '( ' + str(volumeDif) + ' )'
            signalFactor2 += min(3, int(volumeDif/10+1))
        else:
            volumeDifStr = str(volumeDif)

        priceChange = round(self.lastPricePrc[ID][-1]-self.lastPricePrc[ID][0], 1)
        if priceChange > self.priceChangeLimit:
            priceChangeStr = '( ' + str(priceChange) + ' )'
            signalFactor2 += 1
        else:
            priceChangeStr = str(priceChange)

        if self.supplyVolume1[ID][-1] == 0:
            price = str(round(self.lastPricePrc[ID][-1], 1)) + ' -BQ'
        elif self.demandVolume1[ID][-1] == 0:
            price = str(round(self.lastPricePrc[ID][-1], 1)) + ' -SQ'
        else:
            price = str(round(self.lastPricePrc[ID][-1], 1))
        
        if signalFactor1 >= 3:
            self.signaledTickers1.append([tickerName, price, queueRatio, signalFactor1, buyPerCapitaDifStr, realPowerDifStr, volumeDifStr, priceChangeStr, 
                buyPerCapitaStr, realPowerStr, weekVolumeStr, tenkansenDifStr, KijunsenDifStr, upperSpanDifStr, lowerSpanDifStr, chikoSpanCloudDif, buyPerCapita])
        
        if signalFactor1 + signalFactor2 >= 5 and realPowerDif > 1 and volumeDif > 2:
                self.signaledTickers2.append([tickerName, price, queueRatio, signalFactor1 + signalFactor2, buyPerCapitaDifStr, realPowerDifStr, volumeDifStr, priceChangeStr, 
                    buyPerCapitaStr, realPowerStr, weekVolumeStr, tenkansenDifStr, KijunsenDifStr, upperSpanDifStr, lowerSpanDifStr, chikoSpanCloudDif, buyPerCapitaDif])

        if volumeDif > 5 and priceChange > 1.5 and self.lastPricePrc[ID][-1] > 3:
            self.signaledTickers2.append([tickerName, price, queueRatio, 100, buyPerCapitaDifStr, realPowerDifStr, volumeDifStr, priceChangeStr, 
                    buyPerCapitaStr, realPowerStr, weekVolumeStr, tenkansenDifStr, KijunsenDifStr, upperSpanDifStr, lowerSpanDifStr, chikoSpanCloudDif, buyPerCapitaDif])
            winsound.Beep(500, 300)

    def updateUI(self):
        
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

        self.signaledTickers1 = []
        self.signaledTickers2 = []
        self.time = datetime.now()
        for ID in availableIDs:
            if ID in self.offlineData:
            # try:
                self.single_ticker_calc(ID)
            # except:
            #     winsound.Beep(500, 2000)
            #     print('Error')

        self.signaledTickers1.sort(key=lambda tup: (tup[3], tup[16] ), reverse=True)
        self.signaledTickers2.sort(key=lambda tup: (tup[3], tup[16] ), reverse=True)

        self.tree1.delete(*self.tree1.get_children())
        self.tree2.delete(*self.tree2.get_children())

        for i in range(len(self.signaledTickers1)):
            self.tree1.insert('', 'end', text="1", values=[i+1] + self.signaledTickers1[i])
        for i in range(len(self.signaledTickers2)):
            self.tree2.insert('', 'end', text="1", values=[i+1] + self.signaledTickers2[i])

    def runUI(self):
        self.run = True
        self.updateUI()
    
    def pauseUI(self):
        self.run = False

    def onClick1(self, event):
        item = self.tree1.identify_row(event.y)
        if item:
            pyperclip.copy(self.tree1.item(item)['values'][1][:-3])
    
    def onClick2(self, event):
        item = self.tree2.identify_row(event.y)
        if item:
            pyperclip.copy(self.tree2.item(item)['values'][1][:-3])

a = onlineTradeUI()
