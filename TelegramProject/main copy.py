
import time, datetime, threading, os, sys
from cmath import log10, nan
from math import ceil, isnan
from turtle import pen
from Application.Services.ReadData.ReadOnline.MarketWatchDataGenerator import marketWatchDataGenerator
from Application.Services.ReadData.ReadOnline.MarketWatchDataHandler import marketWatchDataHandler
from Application.Services.ReadData.ReadOnline.OnlineDataHandler import historyData, onlineDataHandler, presentData
from Application.Services.WriteData.GetOnlineDataService import get_last_clientType_Data, get_marketWatch_data_tse_method
from Application.Utility.DateConverter import gregorian_to_jalali
from Application.Utility.Indicators.IndicatorService import calculateIchimoko
from Domain.Enums.MarketGroups import marketGroupType
from Domain.Enums.QueryOutPutType import queryOutPutType
from TelegramProject.DataClasses import *
from TelegramProject.TelegramBot import *
from Infrastructure.Repository.OfflineDataRepository import offlineData_repo
from Infrastructure.Repository.TickerRepository import ticker_repo

tempID = 41796741644273824

def print_error(string= ''):
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    print(string, ' ', fname, ' ',  exc_tb.tb_lineno, ' ', exc_type, ' ', exc_obj)

def get_time():
    jalaliDays = {0: 'دوشنبه',
        1: 'سه شنبه',
        2: 'چهارشنبه',
        3: 'پنجشنبه',
        4: 'جمعه',
        5: 'شنبه',
        6: 'یکشنبه'}
    now = datetime.datetime.now()
    return '📅 ' + jalaliDays[now.weekday()] + ' ' + gregorian_to_jalali(now.strftime("%Y-%m-%d"), splitter= '/') + ' 🕘 ' + now.strftime("%H:%M:%S")

class filterPlus:

    def __init__(self) -> None:

        self.firstTime = 1

        self.startTime = 31500 # 31500(08:50)
        self.endTime = 45000 # 45000(12:30)

        self.lock = threading.Lock()

        self.tickersInfo = ticker_repo().read_list_of_tickers(marketTypes= [1, 2, 3, 4, 5, 6, 7, 12], outPutType= queryOutPutType.DictDict)|\
                            ticker_repo().read_list_of_tickers(tickerTypes= [3], outPutType= queryOutPutType.DictDict)
        self.IDs = list(self.tickersInfo.keys())
        self.IDs = [tempID]
        
        self.initialize_today_objects()

        self.run()
        self.update_history_10s()
        self.update_history_1m()

        # market Handler
        # self.marketWatchGen = marketWatchDataGenerator()
        # self.marketGroups = [marketGroupType.TotalMarket.value]
        # self.marketWatchHand = marketWatchDataHandler(self.marketGroups, None) 

    def run(self):

        try:
            now = datetime.datetime.now()
            now = now.hour*3600 + now.minute*60 + now.second

            if self.startTime < now < self.endTime or self.dataReceivedValidation == 0:

                try:

                    if now - self.dataInitTime > 120:
                        output = get_marketWatch_data_tse_method(init= 1)
                        self.dataInitTime = now
                    else:
                        output = get_marketWatch_data_tse_method(heven= self.heven, refid= self.refid)
                    mwData = output['Data']
                    self.heven = output['Heven']
                    self.refid = output['Refid']
                    ctData = get_last_clientType_Data()
                    self.dataHandler.update_data(mwData, ctData)
                    self.dataReceivedValidation = 1
                    
                except:
                    print_error('Error in data part')
                    self.dataReceivedValidation = 0

                timer = threading.Timer(1, self.run)
                timer.start()
            
            else:
                timer = threading.Timer(30, self.run)
                timer.start()

            if self.dataReceivedValidation:
                try:
                    print('FiltersRun', threading.active_count())
                    self.run_filters()
                except:
                    print_error('Error in run_filters')
        except:
            timer = threading.Timer(1, self.run)
            timer.start()

    def run_filters(self):

        with self.lock:
            self.positiveRange.run_filter()
            self.heavyTrades.run_filter()

    def update_history_10s(self):

        while True:
            try:
                now = datetime.datetime.now()
                now = now.hour*3600 + now.minute*60 + now.second

                if self.startTime < now < self.endTime:

                    with self.lock:

                        timer = threading.Timer(10, self.update_history_10s)
                        timer.start()

                        if self.dataReceivedValidation:
                            self.dataHandler.update_history('10s')
                            print('len 10s', len(self.dataHandler.history['10s'][self.IDs[0]].LastPrice))
                        else:
                            timer.cancel()
                            timer = threading.Timer(3, self.update_history_10s)
                            timer.start()
                else:
                    print('10s Out of time range')
                    timer = threading.Timer(30, self.update_history_10s)
                    timer.start()
                return

            except:
                print_error('Error in 10s')
                timer = threading.Timer(5, self.update_history_10s)
                timer.start()

    def update_history_1m(self):

        while True:
            try:
                now = datetime.datetime.now()
                now = now.hour*3600 + now.minute*60 + now.second

                if self.startTime < now < self.endTime:

                    with self.lock:
                        
                        timer = threading.Timer(60, self.update_history_1m)
                        timer.start()

                        if self.dataReceivedValidation:
                            self.dataHandler.update_history('1m')
                            print('len 1m', len(self.dataHandler.history['1m'][self.IDs[0]].LastPrice),)
                        else:
                            timer.cancel()
                            timer = threading.Timer(3, self.update_history_1m)
                            timer.start()
                else:
                    print('1m Out of time range')
                    timer = threading.Timer(30, self.update_history_1m)
                    timer.start()
                return
            except:
                print_error('Error in 1m')
                timer = threading.Timer(5, self.update_history_1m)
                timer.start()

    def initialize_today_objects(self):

        now = datetime.datetime.now()
        now = now.hour*3600 + now.minute*60 + now.second

        if self.firstTime or 28800 < now < 29400: # 28800 (08:00) 29400 (08:10) 

            self.firstTime = 0

            self.dataInitTime = 0
            self.heven = 0
            self.refid = 0
            self.dataReceivedValidation = 1
            self.allSignals: list[signal] = []

            self.dataHandler = onlineDataHandler(self.IDs, {'10s': {'cacheSize': 60}, '1m': {'cacheSize': None}})

            self.positiveRange: positiveRange = positiveRange(self)
            self.heavyTrades: heavyTrades = heavyTrades(self)

            timer = threading.Timer(900, self.initialize_today_objects) # 15 min
            timer.start()

            print('Today Objects initialized.')

        else:

            timer = threading.Timer(60, self.initialize_today_objects) # 1 min
            timer.start()

    def publish_market_data(self):
        pass

class filterParent:

    def __init__(self, main) -> None:
        self.main: filterPlus = main
        self.filterName = self.__class__.__name__
        self.signals: list[signal] = []
        self.tickersData = {ID: {'Signals': [], 'IsInFilter': False} for ID in self.main.IDs}

    def create_general_telegram_message(self, ID):

        tickerPastData: pastData = self.main.dataHandler.pastData[ID]
        tickerPresentData: presentData = self.main.dataHandler.presentData[ID]

        lastPricePrc = round((tickerPresentData.LastPrice-tickerPresentData.YesterdayPrice)/tickerPresentData.YesterdayPrice*100, 2)
        todayPricePrc = round((tickerPresentData.TodayPrice-tickerPresentData.YesterdayPrice)/tickerPresentData.YesterdayPrice*100, 2)

        if lastPricePrc >= 0:
            lastPricePrcStr = ' (' + str(lastPricePrc) + '+ \U0001f7e2)'
        else:
            lastPricePrcStr = ' (' + str(-lastPricePrc) + '- 🔴)'

        if todayPricePrc >= 0:
            todayPricePrcStr = ' (' + str(todayPricePrc) + '+ \U0001f7e2)'
        else:
            todayPricePrcStr = ' (' + str(-todayPricePrc) + '- 🔴)'

        if lastPricePrc-todayPricePrc >= 0:
            lastPriceDifStr = str(round(lastPricePrc-todayPricePrc, 2)) + '+ '
        else:
            lastPriceDifStr = str(round(todayPricePrc-lastPricePrc, 2)) + '- '

        queueStatus = ''
        if tickerPresentData.LastPrice == tickerPresentData.MaxAllowedPrice:
            if tickerPresentData.DemandPrice1 == tickerPresentData.MaxAllowedPrice:
                mVol = tickerPastData.MonthlyValue
                if mVol == 0:
                    buyQueueFactor = 0
                else:
                    buyQueueFactor = int(tickerPresentData.LastPrice * tickerPresentData.DemandVolume1 / mVol*100)

                if buyQueueFactor < 30:
                    buyQueueQ = 'سبک '
                else:
                    buyQueueQ = 'سنگین '
                queueBuyPercapita = int(tickerPresentData.LastPrice * tickerPresentData.DemandVolume1 / tickerPresentData.DemandNumber1 / 10**7)
                if queueBuyPercapita > 40:
                    queueBuyPercapitaStr =  str(queueBuyPercapita) + ' \U0001f7e2'
                else:
                    queueBuyPercapitaStr =  str(queueBuyPercapita) 


                queueStatus = 'صف خرید ' + buyQueueQ + '\U0001f7e2\n' +\
                            'ارزش صف:  ' + str(buyQueueFactor) + ' درصد میانگین ماه' + '\n' +\
                            'سرانه صف:  ' + queueBuyPercapitaStr + '\n\n'
            else:
                queueStatus = ' در حال صف خرید شدن \U0001f7e2\n\n'
            
        if tickerPresentData.LastPrice == tickerPresentData.MinAllowedPrice:
            if tickerPresentData.SupplyPrice1 == tickerPresentData.MinAllowedPrice:
                mVol = tickerPastData.MonthlyValue
                if mVol == 0:
                    sellQueueFactor = 0
                else:
                    sellQueueFactor = int(tickerPresentData.LastPrice * tickerPresentData.SupplyVolume1 / mVol*100)
                if sellQueueFactor < 30:
                    sellQueueQ = 'سبک '
                else:
                    sellQueueQ = 'سنگین '
                queueSellPercapita = int(tickerPresentData.LastPrice * tickerPresentData.SupplyVolume1 / tickerPresentData.SupplyNumber1 / 10**7)
                if queueSellPercapita > 40:
                    queueSellPercapitaStr = str(queueSellPercapita) + ' 🔴' 
                else:
                    queueSellPercapitaStr = str(queueSellPercapita)


                queueStatus = 'صف فروش ' + sellQueueQ + '🔴\n' +\
                    'ارزش صف:  ' + str(sellQueueFactor) + ' درصد میانگین ماه' + '\n' +\
                    'سرانه صف:  ' + queueSellPercapitaStr + '\n\n'
            
            else:
                queueStatus = ' در حال صف فروش شدن 🔴\n\n'
        

        value = round(tickerPresentData.TodayPrice*tickerPresentData.Volume/10**10, 2)
        weekValue = int(tickerPresentData.TodayPrice*tickerPresentData.Volume/tickerPastData.WeeklyValue*100)
        monthValue = int(tickerPresentData.TodayPrice*tickerPresentData.Volume/tickerPastData.MonthlyValue*100)

        bp = ceil(tickerPresentData.RealBuyVolume/tickerPresentData.RealBuyNumber*tickerPresentData.LastPrice/10**7 if tickerPresentData.RealBuyNumber != 0 else 0)
        sp = ceil(tickerPresentData.RealSellVolume/tickerPresentData.RealSellNumber*tickerPresentData.LastPrice/10**7 if tickerPresentData.RealSellNumber != 0 else 0)
        realMoney = round((tickerPresentData.RealBuyVolume-tickerPresentData.RealSellVolume)*tickerPresentData.LastPrice/10**10, 2)
        if bp != 0 and sp != 0 and bp != sp:
            realPower = bp/sp
            if realPower > 1:
                realPowerStr = str(round(realPower, 1)) + '+ \U0001f7e2'
            else:
                realPowerStr = str(round(1/realPower, 1)) + '- 🔴'
        
        else:
            realPowerStr = '1'

        if realMoney >= 0:
            realMoneyStr = str(realMoney) + '+ \U0001f7e2'
        else:
            realMoneyStr = str(-realMoney) + '- 🔴'

        if bp > 40:
            bpStr = str(bp) + ' \U0001f7e2 ( ' + str(round(bp/tickerPastData.buyPercapitaAvg, 1)) + ' برابر میانگین )'
        else:
            bpStr = str(bp) + '  ( ' + str(round(bp/tickerPastData.buyPercapitaAvg, 1)) + ' برابر میانگین )'

        if sp > 40:
            spStr = str(sp) + '  🔴 ( ' + str(round(sp/tickerPastData.sellPercapitaAvg, 1)) + ' برابر میانگین )'
        else:
            spStr = str(sp) + '  ( ' + str(round(sp/tickerPastData.sellPercapitaAvg, 1)) + ' برابر میانگین )'

        dayMaxPriceDif = round((tickerPresentData.MaxPrice-tickerPresentData.LastPrice)/tickerPresentData.LastPrice*100, 1)
        pastMaxPriceDif = round((max(tickerPastData.maxPrice8, tickerPresentData.MaxPrice)-tickerPresentData.LastPrice)/tickerPresentData.LastPrice*100, 1)
        pastMinPriceDif = round((tickerPresentData.LastPrice-min(tickerPastData.minPrice8, tickerPresentData.MinPrice))/min(tickerPastData.minPrice8, tickerPresentData.MinPrice)*100, 1)

        tenkansen = (max(tickerPastData.maxPrice8, tickerPresentData.MaxPrice) + min(tickerPastData.minPrice8, tickerPresentData.MinPrice))/2
        kijunsen = (max(tickerPastData.maxPrice25, tickerPresentData.MaxPrice) + min(tickerPastData.minPrice25, tickerPresentData.MinPrice))/2
        tenkansenDif = round((tickerPresentData.LastPrice-tenkansen)/tenkansen*100, 1)
        kijunsenDif = round((tickerPresentData.LastPrice-kijunsen)/kijunsen*100, 1)
        spanAshiftedDif = round((tickerPresentData.LastPrice-tickerPastData.SpanAshifted)/tickerPastData.SpanAshifted*100, 1)
        spanBshiftedDif = round((tickerPresentData.LastPrice-tickerPastData.SpanBshifted)/tickerPastData.SpanBshifted*100, 1)
        tenkansenLongDif = round((tickerPresentData.LastPrice-tickerPastData.TenkansenLong)/tickerPastData.TenkansenLong*100, 1)
        kijunsenLongDif = round((tickerPresentData.LastPrice-tickerPastData.KijunsenLong)/tickerPastData.KijunsenLong*100, 1)
        
        tenkansenReactionStr = ' ➖ عبور یا پولبک' if tickerPresentData.LastPrice > tenkansen and min(tickerPresentData.MinPrice, tickerPastData.yesterdayMinPrice) <= tenkansen  else ''
        kijunsenReactionStr = ' ➖ عبور یا پولبک' if tickerPresentData.LastPrice > kijunsen and min(tickerPresentData.MinPrice, tickerPastData.yesterdayMinPrice) <= kijunsen  else ''
        spanAshiftedReactionStr = ' ➖ عبور یا پولبک' if tickerPresentData.LastPrice > tickerPastData.SpanAshifted and min(tickerPresentData.MinPrice, tickerPastData.yesterdayMinPrice) <= tickerPastData.SpanAshifted  else ''
        spanBshiftedReactionStr = ' ➖ عبور یا پولبک' if tickerPresentData.LastPrice > tickerPastData.SpanBshifted and min(tickerPresentData.MinPrice, tickerPastData.yesterdayMinPrice) <= tickerPastData.SpanBshifted  else ''
        tenkansenLongReactionStr = ' ➖ عبور یا پولبک' if tickerPresentData.LastPrice > tickerPastData.TenkansenLong and min(tickerPresentData.MinPrice, tickerPastData.yesterdayMinPrice) <= tickerPastData.TenkansenLong  else ''
        kijunsenLongReactionStr = ' ➖ عبور یا پولبک' if tickerPresentData.LastPrice > tickerPastData.KijunsenLong and min(tickerPresentData.MinPrice, tickerPastData.yesterdayMinPrice) <= tickerPastData.KijunsenLong  else ''

        if tenkansenDif >= 0:
            tenkansenDifStr = str(tenkansenDif) + '+ \U0001f7e2'
        else:
            tenkansenDifStr = str(-tenkansenDif) + '- 🔴'
        if isnan(tenkansenDif): tenkansenDifStr = '-'

        if kijunsenDif >= 0:
            kijunsenDifStr = str(kijunsenDif) + '+ \U0001f7e2'
        else:
            kijunsenDifStr = str(-kijunsenDif) + '- 🔴'
        if isnan(kijunsenDif): kijunsenDifStr = '-'

        if spanAshiftedDif >= 0:
            spanAshiftedDifStr = str(spanAshiftedDif) + '+ \U0001f7e2'
        else:
            spanAshiftedDifStr = str(-spanAshiftedDif) + '- 🔴'
        if isnan(spanAshiftedDif): spanAshiftedDifStr = '-'

        if spanBshiftedDif >= 0:
            spanBshiftedDifStr = str(spanBshiftedDif) + '+ \U0001f7e2'
        else:
            spanBshiftedDifStr = str(-spanBshiftedDif) + '- 🔴'
        if isnan(spanBshiftedDif): spanBshiftedDifStr = '-'

        if tenkansenLongDif >= 0:
            tenkansenLongDifStr = str(tenkansenLongDif) + '+ \U0001f7e2'
        else:
            tenkansenLongDifStr = str(-tenkansenLongDif) + '- 🔴'
        if isnan(tenkansenLongDif): tenkansenLongDifStr = '-'

        if kijunsenLongDif >= 0:
            kijunsenLongDifStr = str(kijunsenLongDif) + '+ \U0001f7e2'
        else:
            kijunsenLongDifStr = str(-kijunsenLongDif) + '- 🔴'
        if isnan(kijunsenLongDif): kijunsenLongDifStr = '-'

        heavyDealsPrc = int((self.tickersData[ID]['BuyVolume']-self.tickersData[ID]['SellVolume'])/(tickerPresentData.RealBuyVolume+tickerPresentData.CorporateBuyVolume)*100)
        heavyDealsValue = int((self.tickersData[ID]['BuyVolume']-self.tickersData[ID]['SellVolume'])*tickerPresentData.LastPrice/10**7)
        
        if heavyDealsPrc > 0:
            heavyDealsPrcStr = str(heavyDealsPrc) + '+ درصد ➖ ' +  str(heavyDealsValue) + ' م \U0001f7e2'
        elif heavyDealsPrc < 0:
            heavyDealsPrcStr = str(-heavyDealsPrc) + '- درصد ➖ ' + str(heavyDealsValue) + ' م 🔴'
        else:
            heavyDealsPrcStr = str(heavyDealsPrc) + ' درصد'
        

        msg = '📈 #' + self.main.tickersInfo[ID]['FarsiTicker'] + '  -  ' + self.main.tickersInfo[ID]['FarsiName'] +'\n\n' +\
            'آخرین قیمت:  ' + str(tickerPresentData.LastPrice) + ' ' + lastPricePrcStr + '\n'+\
            'قیمت پایانی:  ' + str(tickerPresentData.TodayPrice) + ' ' + todayPricePrcStr + '\n' +\
            'اختلاف:  ' + lastPriceDifStr + '\n\n' +\
            'فاصله از سقف روز:  ' + str(dayMaxPriceDif) + '\n' +\
            'فاصله از سقف دو هفته:  ' + str(pastMaxPriceDif) + '\n' +\
            'فاصله از کف دو هفته:  ' + str(pastMinPriceDif) + '\n\n' +\
            queueStatus +\
            'ارزش معاملات:  ' + str(value) + '\n' + \
            str(weekValue) + ' درصد میانگین هفته' + '\n' +\
            str(monthValue) + ' درصد میانگین ماه' + '\n\n' +\
            'قدرت خریدار:  ' + realPowerStr + '\n' +\
            'سرانه خریدار:  ' + bpStr + '\n' +\
            'سرانه فروشنده:  ' + spStr + '\n' + \
            'پول حقیقی:  ' + realMoneyStr + '\n' +\
            'مجموع خریدهای درشت\U0001f7e2  ' +\
            str(self.main.heavyTrades.tickersData[ID]['BuyNumber']) + ' بار  ➖ ' + \
            str(int(self.main.heavyTrades.tickersData[ID]['BuyVolume']/tickerPresentData.RealBuyVolume*100)) + ' درصد' + '\n' +\
            'مجموع فروش های درشت🔴  ' +\
            str(self.main.heavyTrades.tickersData[ID]['SellNumber']) + ' بار  ➖ ' + \
            str(int(self.main.heavyTrades.tickersData[ID]['SellVolume']/tickerPresentData.RealSellVolume*100)) + ' درصد' + '\n' +\
            'برآیند معاملات بزرگ:  ' + heavyDealsPrcStr + '\n\n'+\
            'ایچیموکو:\n' +\
            'تنکانسن:  ' + tenkansenDifStr + tenkansenReactionStr + '\n' +\
            'کیجنسن:  ' + kijunsenDifStr + kijunsenReactionStr + '\n' +\
            'اسپن۱:  ' + spanAshiftedDifStr + spanAshiftedReactionStr + '\n' +\
            'اسپن۲:  ' + spanBshiftedDifStr + spanBshiftedReactionStr + '\n' +\
            'کومو بلند۱:  ' + tenkansenLongDifStr + tenkansenLongReactionStr + '\n' +\
            'کومو بلند۲:  ' + kijunsenLongDifStr + kijunsenLongReactionStr + '\n\n'
            
        return msg

    def signal_in_telegram(self, telegramMessage, telegramID, ID, replyMessageID= None):

        if replyMessageID == None:
            tickerSignals: list[signal] = self.tickersData[ID]['Signals']
            if len(tickerSignals) == 0:
                replyMessageID = None
            else:
                replyMessageID = tickerSignals[-1].messageID
        elif replyMessageID == False:
            replyMessageID = None

        messageID = send_message(telegramID, telegramMessage, replyMessageID)
        
        return messageID

    def store_signal_info(self, ID, signalSpec, messageID):

            thisSignal = signal()
            now = datetime.datetime.now()
            now = now.hour*3600 + now.minute*60 + now.second
            thisSignal.time = now
            thisSignal.ID = ID
            thisSignal.filterName = self.filterName
            thisSignal.signalSpec = signalSpec
            thisSignal.messageID = messageID
            self.main.allSignals.append(thisSignal)
            self.signals.append(thisSignal)
            self.tickersData[ID]['Signals'].append(thisSignal)

    def run_filter():
        raise Exception('Not Implemented.')

class ichimokoFilter(filterParent):

    def __init__(self, main) -> None:
        super().__init__(main)

    def run(self):

        now = datetime.datetime.now()
        now = now.hour*3600 + now.minute*60 + now.second
        
        for ID in self.main.dataHandler.presentData:

            if ID in self.main.dataHandler.pastData:

                tickerPastData: pastData = self.main.dataHandler.pastData[ID]
                tickerPresentData: presentData = self.main.dataHandler.presentData[ID]
                tickerSignals: list[signal] = self.tickersData[ID]['Signals']

                tenkansen = (max(tickerPastData.maxPrice8, tickerPresentData.MaxPrice) + min(tickerPastData.minPrice8, tickerPresentData.MinPrice))/2
                kijunsen = (max(tickerPastData.maxPrice25, tickerPresentData.MaxPrice) + min(tickerPastData.minPrice25, tickerPresentData.MinPrice))/2

                tenkansenReaction = True if tickerPresentData.LastPrice > tenkansen and min(tickerPresentData.MinPrice, tickerPastData.yesterdayMinPrice) <= tenkansen  else False
                kijunsenReaction = True if tickerPresentData.LastPrice > kijunsen and min(tickerPresentData.MinPrice, tickerPastData.yesterdayMinPrice) <= kijunsen  else False
                spanAshiftedReaction = True if tickerPresentData.LastPrice > tickerPastData.SpanAshifted and min(tickerPresentData.MinPrice, tickerPastData.yesterdayMinPrice) <= tickerPastData.SpanAshifted  else False
                spanBshiftedReaction = True if tickerPresentData.LastPrice > tickerPastData.SpanBshifted and min(tickerPresentData.MinPrice, tickerPastData.yesterdayMinPrice) <= tickerPastData.SpanBshifted  else False
                # tenkansenLongReaction = True if tickerPresentData.LastPrice > tickerPastData.TenkansenLong and min(tickerPresentData.MinPrice, tickerPastData.yesterdayMinPrice) <= tickerPastData.TenkansenLong  else False
                # kijunsenLongReaction = True if tickerPresentData.LastPrice > tickerPastData.KijunsenLong and min(tickerPresentData.MinPrice, tickerPastData.yesterdayMinPrice) <= tickerPastData.KijunsenLong  else False

                if tenkansenReaction and kijunsenReaction and spanBshiftedReaction:
                    if self.tickersData[ID]['IsInFilter'] == False or now-tickerSignals[-1].time > 60:

                        messageID = self.signal_in_telegram(self.create_general_telegram_message()+get_time(), myTelegramAcountChatID, ID)
                        if messageID:
                            self.store_signal_info(ID, None, messageID)
                        
                            print(ID)
                            x = 1

                x = 1

class heavyTrades(filterParent):

    def __init__(self, main) -> None:
        super().__init__(main)
        for ID in self.tickersData:
            self.tickersData[ID]['BuyNumber'] = 0
            self.tickersData[ID]['SellNumber'] = 0
            self.tickersData[ID]['BuyVolume'] = 0
            self.tickersData[ID]['SellVolume'] = 0

    def run_filter(self):

        now = datetime.datetime.now()
        now = now.hour*3600 + now.minute*60 + now.second

        if self.main.startTime < now < self.main.endTime:

            for ID in self.main.dataHandler.presentData:

                tickerPresentData: presentData = self.main.dataHandler.presentData[ID]

                if tickerPresentData.Volume != None: #ID == 7745894403636165 and 

                    try:

                        if 'ctData' not in self.tickersData[ID]:
                            self.tickersData[ID]['ctData'] = ctItems()

                        tickerCtHistory: ctItems = self.tickersData[ID]['ctData']
                        tickerPasData: pastData = self.main.dataHandler.pastData[ID]

                        if tickerCtHistory.RealBuyVolume < tickerPresentData.RealBuyVolume or tickerCtHistory.RealSellVolume < tickerPresentData.RealSellVolume or\
                            tickerCtHistory.CorporateBuyVolume < tickerPresentData.CorporateBuyVolume or tickerCtHistory.CorporateSellVolume < tickerPresentData.CorporateSellVolume or 1:

                            RealBuyVolumeDif = tickerPresentData.RealBuyVolume-tickerCtHistory.RealBuyVolume
                            RealBuyNumberDif = max(tickerPresentData.RealBuyNumber-tickerCtHistory.RealBuyNumber, 1)
                            RealSellVolumeDif = tickerPresentData.RealSellVolume-tickerCtHistory.RealSellVolume
                            RealSellNumberDif = max(tickerPresentData.RealSellNumber-tickerCtHistory.RealSellNumber, 1)

                            RealBuyPercapita = int(RealBuyVolumeDif/RealBuyNumberDif*tickerPresentData.LastPrice/10**7) #if RealBuyNumberDif != 0 else nan
                            RealSellPercapita = int(RealSellVolumeDif/RealSellNumberDif*tickerPresentData.LastPrice/10**7) #if RealSellNumberDif != 0 else nan
                            
                            CorporateBuyVolumeDif = tickerPresentData.CorporateBuyVolume-tickerCtHistory.CorporateBuyVolume
                            # CorporateBuyNumberDif = tickerPresentData.CorporateBuyNumber-tickerCtHistory.CorporateBuyNumber
                            CorporateSellVolumeDif = tickerPresentData.CorporateSellVolume-tickerCtHistory.CorporateSellVolume
                            # CorporateSellNumberDif = tickerPresentData.CorporateSellNumber-tickerCtHistory.CorporateSellNumber

                            ctValueLimit = max(min(tickerPasData.WeeklyValue*0.03, 500*10**7), 100*10**7)
                            percapitaLimit = max(min(5*tickerPasData.buyPercapitaAvg, 60), 40)

                            if RealBuyVolumeDif*tickerPresentData.TodayPrice >= ctValueLimit and RealBuyPercapita >= percapitaLimit or\
                                RealSellVolumeDif*tickerPresentData.TodayPrice >= ctValueLimit and RealSellPercapita >= percapitaLimit:

                                lastPricePrc = round((tickerPresentData.LastPrice-tickerPresentData.YesterdayPrice)/tickerPresentData.YesterdayPrice*100, 2)
                                if lastPricePrc >= 0:
                                    lastPricePrcStr = ' (' + str(lastPricePrc) + '+ \U0001f7e2)'
                                else:
                                    lastPricePrcStr = ' (' + str(-lastPricePrc) + '- 🔴)'

                                msg = '📈 #' + self.main.tickersInfo[ID]['FarsiTicker'] + ' - ' + lastPricePrcStr +'\n\n'

                                if RealBuyVolumeDif*tickerPresentData.TodayPrice >= ctValueLimit and RealBuyPercapita >= percapitaLimit:
                                    self.tickersData[ID]['BuyNumber'] += 1
                                    self.tickersData[ID]['BuyVolume'] += RealBuyVolumeDif
                                    msg += 'خرید درشت حقیقی \U0001f7e2 ' + str(RealBuyNumberDif) + ' کد ➖ ' +  str(RealBuyPercapita) + ' م ➖ ' + str(int(RealBuyVolumeDif*tickerPresentData.LastPrice/10**7)) + ' م' + '\n'

                                if RealSellVolumeDif*tickerPresentData.TodayPrice >= ctValueLimit and RealSellPercapita >= percapitaLimit:
                                    self.tickersData[ID]['SellNumber'] += 1
                                    self.tickersData[ID]['SellVolume'] += RealSellVolumeDif
                                    msg += 'فروش درشت حقیقی 🔴 ' + str(RealSellNumberDif) + ' کد ➖ ' +  str(RealSellPercapita) + ' م ➖ ' + str(int(RealSellVolumeDif*tickerPresentData.LastPrice/10**7)) + ' م' + '\n'

                                if CorporateSellVolumeDif != 0 and 0.8 < RealBuyVolumeDif/CorporateSellVolumeDif < 1.2:
                                    msg += '\n احتمال کد به کد حقوقی به حقیقی!\U0001f7e2\n'
                                if CorporateBuyVolumeDif != 0 and 0.8 < RealSellVolumeDif/CorporateBuyVolumeDif < 1.2:
                                    msg += '\n احتمال کد به کد حقیقی به حقوقی!🔴\n'

                                heavyDealsPrc = int((self.tickersData[ID]['BuyVolume']-self.tickersData[ID]['SellVolume'])/(tickerPresentData.RealBuyVolume+tickerPresentData.CorporateBuyVolume)*100)
                                heavyDealsValue = int((self.tickersData[ID]['BuyVolume']-self.tickersData[ID]['SellVolume'])*tickerPresentData.LastPrice/10**7)
                                
                                if heavyDealsPrc > 0:
                                    heavyDealsPrcStr = str(heavyDealsPrc) + '+ درصد ➖ ' +  str(heavyDealsValue) + ' م \U0001f7e2'
                                elif heavyDealsPrc < 0:
                                    heavyDealsPrcStr = str(-heavyDealsPrc) + '- درصد ➖ ' + str(heavyDealsValue) + ' م 🔴'
                                else:
                                    heavyDealsPrcStr = str(heavyDealsPrc) + ' درصد'
                                msg += '\nمجموع خریدهای درشت \U0001f7e2  ' +\
                                    str(self.tickersData[ID]['BuyNumber']) + ' بار  ➖ ' + \
                                    str(int(self.tickersData[ID]['BuyVolume']/tickerPresentData.RealBuyVolume*100)) + ' درصد' + '\n' +\
                                    'مجموع فروش های درشت 🔴  ' +\
                                    str(self.tickersData[ID]['SellNumber']) + ' بار  ➖ ' + \
                                    str(int(self.tickersData[ID]['SellVolume']/tickerPresentData.RealSellVolume*100)) + ' درصد' + '\n\n' +\
                                    'برآیند معاملات بزرگ:  ' + heavyDealsPrcStr + '\n\n'
                                
                                tickerPositiveRangeSignals: list[signal] = self.main.positiveRange.tickersData[ID]['Signals']

                                if len(tickerPositiveRangeSignals) != 0 and tickerPresentData.Time-tickerPositiveRangeSignals[-1].time < 1800:
                                    self.signal_in_telegram(msg+get_time(), positiveRangeChatID, ID, tickerPositiveRangeSignals[-1].messageID)

                                messageID = self.signal_in_telegram(msg+get_time(), doroshtBinChatID, ID)
                                if messageID:
                                    self.store_signal_info(ID, None, messageID)
                            
                                print('heavy deal: ', ID)

                    except:
                        print_error('HeavyTrade inside: ' + str(ID))

                    try:
                        tickerCtHistory.RealBuyVolume = tickerPresentData.RealBuyVolume if tickerPresentData.RealBuyVolume > tickerCtHistory.RealBuyVolume or isnan(tickerCtHistory.RealBuyVolume) else tickerCtHistory.RealBuyVolume
                        tickerCtHistory.RealBuyNumber = tickerPresentData.RealBuyNumber if tickerPresentData.RealBuyNumber > tickerCtHistory.RealBuyNumber or isnan(tickerCtHistory.RealBuyNumber) else tickerCtHistory.RealBuyNumber
                        tickerCtHistory.RealSellVolume = tickerPresentData.RealSellVolume if tickerPresentData.RealSellVolume > tickerCtHistory.RealSellVolume or isnan(tickerCtHistory.RealSellVolume) else tickerCtHistory.RealSellVolume
                        tickerCtHistory.RealSellNumber = tickerPresentData.RealSellNumber if tickerPresentData.RealSellNumber > tickerCtHistory.RealSellNumber or isnan(tickerCtHistory.RealSellNumber) else tickerCtHistory.RealSellNumber
                        tickerCtHistory.CorporateBuyVolume = tickerPresentData.CorporateBuyVolume if tickerPresentData.CorporateBuyVolume > tickerCtHistory.CorporateBuyVolume or isnan(tickerCtHistory.CorporateBuyVolume) else tickerCtHistory.CorporateBuyVolume
                        tickerCtHistory.CorporateBuyNumber = tickerPresentData.CorporateBuyNumber if tickerPresentData.CorporateBuyNumber > tickerCtHistory.CorporateBuyNumber or isnan(tickerCtHistory.CorporateBuyNumber) else tickerCtHistory.CorporateBuyNumber
                        tickerCtHistory.CorporateSellVolume = tickerPresentData.CorporateSellVolume if tickerPresentData.CorporateSellVolume > tickerCtHistory.CorporateSellVolume or isnan(tickerCtHistory.CorporateSellVolume) else tickerCtHistory.CorporateSellVolume
                        tickerCtHistory.CorporateSellNumber = tickerPresentData.CorporateSellNumber if tickerPresentData.CorporateSellNumber > tickerCtHistory.CorporateSellNumber or isnan(tickerCtHistory.CorporateSellNumber) else tickerCtHistory.CorporateSellNumber
                    except:
                        print_error('HeavyTrade update:' + str(ID))

class positiveRange(filterParent):

    def __init__(self, main) -> None:
        super().__init__(main)

    def run_filter(self):

        now = datetime.datetime.now()
        now = now.hour*3600 + now.minute*60 + now.second

        if self.main.startTime < now < self.main.endTime:

            for ID in self.main.dataHandler.activeIDs:

                verify = False

                try:
                    tickerPresentData: presentData = self.main.dataHandler.presentData[ID]
                    tickerPastData: pastData = self.main.dataHandler.pastData[ID]
                    tickerHistory: historyData = self.main.dataHandler.history['10s'][ID]

                    priceIndice = -min(len(tickerHistory.LastPrice), 60)
                    volumeIndice = -min(len(tickerHistory.LastPrice), 18)

                    if abs(priceIndice) < 6:
                        continue

                    priceDif = round((tickerPresentData.LastPrice-tickerHistory.LastPrice[priceIndice])/tickerPresentData.YesterdayPrice*100, 1)
                    timeDif = tickerPresentData.Time-tickerHistory.Time[volumeIndice]
                    valueDif = (tickerPresentData.Volume-tickerHistory.Volume[volumeIndice])*tickerPresentData.TodayPrice

                    normalValue = round((valueDif*210*60/timeDif) / tickerPastData.MonthlyValue, 1)

                    if priceDif >= 1.5 and normalValue >= 6: # ID == 611986653700161 and 
                        dayMaxPriceDif = (tickerPresentData.MaxPrice-tickerPresentData.LastPrice)/tickerPresentData.LastPrice*100
                        if dayMaxPriceDif < 5 and tickerPresentData.CorporateBuyVolume/(tickerPresentData.CorporateBuyVolume+tickerPresentData.RealBuyVolume) < 0.2:
                            if tickerPastData.WeeklyValue/(tickerPresentData.BaseVolume*tickerPresentData.LastPrice) > 1:
                                verify = True

                    if verify:

                        if self.tickersData[ID]['IsInFilter'] == False and (len(self.tickersData[ID]['Signals']) == 0 or tickerPresentData.Time-self.tickersData[ID]['Signals'][-1].time > 120):

                            if priceDif >= 0:
                                priceDifStr = str(priceDif) + '+'
                            else:
                                priceDifStr = str(-priceDif) + '-'

                            filterMessage = 'تغییر قیمت:  ' + priceDifStr + ' درصد\n' +\
                                'ارزش معاملات:  ' + str(normalValue) + ' برابر حالت عادی\n' +\
                                'تعداد سیگنال:  ' + str(len(self.tickersData[ID]['Signals'])+1) + '\n\n'

                            telegramMessage = self.create_general_telegram_message(ID) + filterMessage + get_time()

                            messageID = self.signal_in_telegram(telegramMessage, positiveRangeChatID, ID)
                            if messageID:
                                self.store_signal_info(ID, {'PriceChange': priceDif, 'NormalValue': normalValue}, messageID)
                                print('PostiveRange Signaled:', ID)
                                self.tickersData[ID]['IsInFilter'] = True
                    else:
                        self.tickersData[ID]['IsInFilter'] = False

                except:
                    print_error('PositiveRange: ' + str(ID) + ' Price: ' + str(tickerPresentData.LastPrice))