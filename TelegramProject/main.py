
import datetime, threading, os, sys
from math import ceil, isnan, log10, nan
from Application.Services.WriteData.GetOnlineDataService import get_last_clientType_Data, get_marketWatch_data_tse_method
from Application.Utility.DateConverter import gregorian_to_jalali
from Domain.Enums.QueryOutPutType import queryOutPutType
from TelegramProject.DataClasses import *
from TelegramProject.DataHandler import dataHandler, historyData, presentData
from TelegramProject.TelegramBot import *
from Infrastructure.Repository.TickerRepository import ticker_repo
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import  matplotlib

matplotlib.rc('xtick', labelsize=6) 
matplotlib.rc('ytick', labelsize=6)

tempID = 41796741644273824

def print_error(string= ''):
    exc_type, exc_obj, exc_tb = sys.exc_info()
    while True:
        if exc_tb.tb_next == None:
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            break
        else:
           exc_tb = exc_tb.tb_next 
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

        self.startTime = 32400 # 32400(09:00)
        self.endTime = 45000 # 45000(12:30)

        self.telegramLastUpdateID = 0

        self.lock = threading.Lock()

        self.tickersInfo = ticker_repo().read_list_of_tickers(marketTypes= [1, 2, 3, 4, 5, 6, 7, 12], outPutType= queryOutPutType.DictDict)|\
                            ticker_repo().read_list_of_tickers(tickerTypes= [3], outPutType= queryOutPutType.DictDict)
        self.IDs = list(self.tickersInfo.keys())[:]
        # self.IDs = [tempID]
        
        self.initialize_today_objects()

        self.run()
        self.update_history_10s()
        self.update_history_1m()
        self.run_market_filters()
        self.telegram_assistant()

    def run(self):

        try:
            nowObj = datetime.datetime.now()
            now = nowObj.hour*3600 + nowObj.minute*60 + nowObj.second

            if self.startTime-10*60 < now < self.endTime and nowObj.weekday() not in [3, 4] or self.dataReceivedValidation == 0 or self.dataInitTime == 0:

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
                    with self.lock:
                        self.dataHandler.update_data(mwData, ctData)
                    self.dataReceivedValidation = 1
                    
                except:
                    print_error('Error in data part')
                    self.dataReceivedValidation = 0
            
            if self.dataReceivedValidation:

                try:
                    print('FiltersRun', threading.active_count())
                    self.run_filters()
                except:
                    print_error('Error in run_filters')

            if self.startTime-10*60 < now < self.endTime and nowObj.weekday() not in [3, 4]:
                timer = threading.Timer(1, self.run)
            else:
                timer = threading.Timer(30, self.run)
            timer.start()

        except:
            print_error('Error in run_filters')
            timer = threading.Timer(1, self.run)
            timer.start()

    def run_filters(self):

        with self.lock:
            self.positiveRange.run_filter()
            self.heavyTrades.run_filter()

    def update_history_10s(self):

        try:
            nowObj = datetime.datetime.now()
            now = nowObj.hour*3600 + nowObj.minute*60 + nowObj.second
            if self.startTime-10*60 < now < self.endTime and nowObj.weekday() not in [3, 4]:
                if self.dataReceivedValidation:
                    with self.lock:
                        self.dataHandler.update_history('10s')
                    timer = threading.Timer(10, self.update_history_10s)
                    timer.start()
                else:
                    timer = threading.Timer(3, self.update_history_10s)
                    timer.start()
            else:
                timer = threading.Timer(30, self.update_history_10s)
                timer.start()
        except:
            print_error('Error in 10s')
            timer = threading.Timer(3, self.update_history_10s)
            timer.start()

    def update_history_1m(self):

        try:
            nowObj = datetime.datetime.now()
            now = nowObj.hour*3600 + nowObj.minute*60 + nowObj.second
            if self.startTime-10*60 < now < self.endTime and nowObj.weekday() not in [3, 4]:
                if self.dataReceivedValidation:
                    with self.lock:
                        self.dataHandler.update_history('1m')
                    timer = threading.Timer(60, self.update_history_1m)
                    timer.start()
                else:
                    timer = threading.Timer(3, self.update_history_1m)
                    timer.start()
            else:
                timer = threading.Timer(30, self.update_history_1m)
                timer.start()
        except:
            print_error('Error in 1m')
            timer = threading.Timer(3, self.update_history_1m)
            timer.start()

    def run_market_filters(self):

        try:
            nowObj = datetime.datetime.now()
            now = nowObj.hour*3600 + nowObj.minute*60 + nowObj.second
            if self.startTime < now < self.endTime+2*60 and nowObj.weekday() not in [3, 4]:
                if self.dataReceivedValidation:
                    with self.lock:
                        self.marketManager.run_filters()
                    timer = threading.Timer(60, self.run_market_filters)
                    timer.start()
                else:
                    timer = threading.Timer(3, self.run_market_filters)
                    timer.start()
            else:
                timer = threading.Timer(30, self.run_market_filters)
                timer.start()
        except:
            print_error('Error in marketwatch')
            timer = threading.Timer(3, self.run_market_filters)
            timer.start()

    def initialize_today_objects(self):

        try:

            nowObj = datetime.datetime.now()
            now = nowObj.hour*3600 + nowObj.minute*60 + nowObj.second

            if self.firstTime or 28800 < now < 29400 and nowObj.weekday() not in [3, 4]: # 28800 (08:00) 29400 (08:10) 

                with self.lock:

                    self.firstTime = 0
                    self.dataInitTime = 0
                    self.heven = 0
                    self.refid = 0
                    self.dataReceivedValidation = 1
                    self.allSignals: list[signal] = []

                    self.dataHandler = dataHandler(self.IDs, {'10s': {'cacheSize': 60}, '1m': {'cacheSize': None}})

                    self.positiveRange: positiveRange = positiveRange(self)
                    self.heavyTrades: heavyTrades = heavyTrades(self)
                    self.marketManager: marketManager = marketManager(self)

                    timer = threading.Timer(900, self.initialize_today_objects) # 15 min
                    timer.start()

                    print('Today Objects initialized.')

            else:
                timer = threading.Timer(60, self.initialize_today_objects)
                timer.start()

        except:
            print_error('Error in initialize_today_objects:')
            timer = threading.Timer(60, self.initialize_today_objects)
            timer.start()

    def telegram_assistant(self):

        try:

            data = get_updates(self.telegramLastUpdateID)['result']

            for i in range(len(data)):
                item = data[i]
                if item['update_id'] > self.telegramLastUpdateID and 'message' in item:
                    if item['message']['chat']['id'] in [int(myTelegramAcountChatID), int(filterPlusGroupChatID)] and int(datetime.datetime.now().timestamp())-item['message']['date'] < 10:
                        try:
                            for ID in self.tickersInfo:
                                if self.tickersInfo[ID]['FarsiTicker'] == item['message']['text']:
                                    with self.lock:
                                        message = self.positiveRange.create_general_telegram_message(ID) + get_time()
                                    send_message(str(item['message']['chat']['id']), message, False)
                                    break
                            else:
                                if item['message']['chat']['id'] == int(myTelegramAcountChatID):
                                    try:
                                        try:
                                            self.testVar = signal()
                                            send_message(myTelegramAcountChatID, str(eval(str(item['message']['text']))), False)
                                        except:
                                            exec(str(item['message']['text']))
                                    except:
                                        print_error('Error in TA get data:')

                        except:
                            print_error('Error in telegram_assistant:')
                            pass
                    self.telegramLastUpdateID = item['update_id']

            timer = threading.Timer(2, self.telegram_assistant)
            timer.start()

        except:
            print_error('Error in telegram_assistant data:')
            timer = threading.Timer(2, self.telegram_assistant)
            timer.start()

class filterParent:

    def __init__(self, main) -> None:
        self.main: filterPlus = main
        self.filterName = self.__class__.__name__
        self.signals: list[signal] = []
        self.tickersData = {ID: {'Signals': [], 'IsInFilter': False} for ID in self.main.IDs}
        self.reportTime = 0

    def create_general_telegram_message(self, ID):

        tickerPastData: pastData = self.main.dataHandler.pastData[ID]
        tickerPresentData: presentData = self.main.dataHandler.presentData[ID]

        lastPricePrc = round((tickerPresentData.LastPrice-tickerPresentData.YesterdayPrice)/tickerPresentData.YesterdayPrice*100, 2)
        todayPricePrc = round((tickerPresentData.TodayPrice-tickerPresentData.YesterdayPrice)/tickerPresentData.YesterdayPrice*100, 2)

        if lastPricePrc >= 0:
            lastPricePrcStr = '(' + str(lastPricePrc) + '+\U0001f7e2)'
        else:
            lastPricePrcStr = '(' + str(-lastPricePrc) + '-🔴)'

        if todayPricePrc >= 0:
            todayPricePrcStr = '(' + str(todayPricePrc) + '+\U0001f7e2)'
        else:
            todayPricePrcStr = '(' + str(-todayPricePrc) + '-🔴)'

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
                    buyQueueQ = 'سبک'
                else:
                    buyQueueQ = 'سنگین'
                queueBuyPercapita = int(tickerPresentData.LastPrice * tickerPresentData.DemandVolume1 / tickerPresentData.DemandNumber1 / 10**7)
                if queueBuyPercapita > 40:
                    queueBuyPercapitaStr =  str(queueBuyPercapita) + ' \U0001f7e2'
                else:
                    queueBuyPercapitaStr =  str(queueBuyPercapita) 


                queueStatus = 'صف خرید ' + buyQueueQ + '\U0001f7e2' + '  <b>ا</b>  ' + str(buyQueueFactor) + '% ماه  <b>ا</b>  ' + queueBuyPercapitaStr + '\n\n'

            else:
                queueStatus = 'در حال صف خرید شدن\U0001f7e2\n\n'
            
        if tickerPresentData.LastPrice == tickerPresentData.MinAllowedPrice:
            if tickerPresentData.SupplyPrice1 == tickerPresentData.MinAllowedPrice:
                mVol = tickerPastData.MonthlyValue
                if mVol == 0:
                    sellQueueFactor = 0
                else:
                    sellQueueFactor = int(tickerPresentData.LastPrice * tickerPresentData.SupplyVolume1 / mVol*100)
                if sellQueueFactor < 30:
                    sellQueueQ = 'سبک'
                else:
                    sellQueueQ = 'سنگین'
                queueSellPercapita = int(tickerPresentData.LastPrice * tickerPresentData.SupplyVolume1 / tickerPresentData.SupplyNumber1 / 10**7)
                if queueSellPercapita > 40:
                    queueSellPercapitaStr = str(queueSellPercapita) + ' 🔴' 
                else:
                    queueSellPercapitaStr = str(queueSellPercapita)

                queueStatus = 'صف فروش ' + sellQueueQ + '🔴  <b>ا</b>  ' + str(sellQueueFactor) + '% ماه  <b>ا</b>  ' + queueSellPercapitaStr + '\n\n'

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
                realPowerStr = str(round(realPower, 1)) + '+\U0001f7e2'
            else:
                realPowerStr = str(round(1/realPower, 1)) + '-🔴'
        
        else:
            realPowerStr = '1.0'

        if realMoney >= 0:
            realMoneyStr = '(' + str(realMoney) + '+\U0001f7e2)'
        else:
            realMoneyStr = '(' + str(-realMoney) + '-🔴)'

        if bp > 40:
            bpStr = str(bp) + '\U0001f7e2(' + str(round(bp/tickerPastData.buyPercapitaAvg, 1)) + ' برابر)'
        else:
            bpStr = str(bp) + ' (' + str(round(bp/tickerPastData.buyPercapitaAvg, 1)) + ' برابر)'

        if sp > 40:
            spStr = str(sp) + '🔴(' + str(round(sp/tickerPastData.sellPercapitaAvg, 1)) + ' برابر)'
        else:
            spStr = str(sp) + ' (' + str(round(sp/tickerPastData.sellPercapitaAvg, 1)) + ' برابر)'

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
        
        tenkansenReactionStr = '⬆️' if tickerPresentData.LastPrice > tenkansen and min(tickerPresentData.MinPrice, tickerPastData.yesterdayMinPrice) <= tenkansen  else ''
        kijunsenReactionStr = '⬆️' if tickerPresentData.LastPrice > kijunsen and min(tickerPresentData.MinPrice, tickerPastData.yesterdayMinPrice) <= kijunsen  else ''
        spanAshiftedReactionStr = '⬆️' if tickerPresentData.LastPrice > tickerPastData.SpanAshifted and min(tickerPresentData.MinPrice, tickerPastData.yesterdayMinPrice) <= tickerPastData.SpanAshifted  else ''
        spanBshiftedReactionStr = '⬆️' if tickerPresentData.LastPrice > tickerPastData.SpanBshifted and min(tickerPresentData.MinPrice, tickerPastData.yesterdayMinPrice) <= tickerPastData.SpanBshifted  else ''
        tenkansenLongReactionStr = '⬆️' if tickerPresentData.LastPrice > tickerPastData.TenkansenLong and min(tickerPresentData.MinPrice, tickerPastData.yesterdayMinPrice) <= tickerPastData.TenkansenLong  else ''
        kijunsenLongReactionStr = '⬆️' if tickerPresentData.LastPrice > tickerPastData.KijunsenLong and min(tickerPresentData.MinPrice, tickerPastData.yesterdayMinPrice) <= tickerPastData.KijunsenLong  else ''

        if tenkansenDif >= 0:
            tenkansenDifStr = str(tenkansenDif) + '+\U0001f7e2'
        else:
            tenkansenDifStr = str(-tenkansenDif) + '-🔴'
        if isnan(tenkansenDif): tenkansenDifStr = '-'

        if kijunsenDif >= 0:
            kijunsenDifStr = str(kijunsenDif) + '+\U0001f7e2'
        else:
            kijunsenDifStr = str(-kijunsenDif) + '-🔴'
        if isnan(kijunsenDif): kijunsenDifStr = '-'

        if spanAshiftedDif >= 0:
            spanAshiftedDifStr = str(spanAshiftedDif) + '+\U0001f7e2'
        else:
            spanAshiftedDifStr = str(-spanAshiftedDif) + '-🔴'
        if isnan(spanAshiftedDif): spanAshiftedDifStr = '-'

        if spanBshiftedDif >= 0:
            spanBshiftedDifStr = str(spanBshiftedDif) + '+\U0001f7e2'
        else:
            spanBshiftedDifStr = str(-spanBshiftedDif) + '-🔴'
        if isnan(spanBshiftedDif): spanBshiftedDifStr = '-'

        if tenkansenLongDif >= 0:
            tenkansenLongDifStr = str(tenkansenLongDif) + '+\U0001f7e2'
        else:
            tenkansenLongDifStr = str(-tenkansenLongDif) + '-🔴'
        if isnan(tenkansenLongDif): tenkansenLongDifStr = '-'

        if kijunsenLongDif >= 0:
            kijunsenLongDifStr = str(kijunsenLongDif) + '+\U0001f7e2'
        else:
            kijunsenLongDifStr = str(-kijunsenLongDif) + '-🔴'
        if isnan(kijunsenLongDif): kijunsenLongDifStr = '-'

        heavyDealsPrc = max(min(int((self.main.heavyTrades.tickersData[ID]['BuyVolume']-self.main.heavyTrades.tickersData[ID]['SellVolume'])/(tickerPresentData.RealBuyVolume+tickerPresentData.CorporateBuyVolume)*100), 100), -100)
        heavyDealsValue = int((self.main.heavyTrades.tickersData[ID]['BuyVolume']-self.main.heavyTrades.tickersData[ID]['SellVolume'])*tickerPresentData.LastPrice/10**7)
        
        if heavyDealsPrc > 0:
            heavyDealsPrcStr = str(heavyDealsPrc) + '+ درصد ➖ ' +  str(heavyDealsValue) + '+ م \U0001f7e2'
        elif heavyDealsPrc < 0:
            heavyDealsPrcStr = str(-heavyDealsPrc) + '- درصد ➖ ' + str(-heavyDealsValue) + '- م 🔴'
        else:
            heavyDealsPrcStr = str(heavyDealsPrc) + ' درصد'
        

        msg = '📈 #' + self.main.tickersInfo[ID]['FarsiTicker'] + '  -  ' + self.main.tickersInfo[ID]['FarsiName'] +'\n\n' +\
            'آخرین قیمت / قیمت پایانی / اختلاف:\n' +\
            str(tickerPresentData.LastPrice) + ' ' + lastPricePrcStr + '  <b>ا</b>  ' + str(tickerPresentData.TodayPrice) + ' ' + todayPricePrcStr + '  <b>ا</b>  ' + lastPriceDifStr + '\n\n'+\
            'فاصله از سقف روز / سقف 8 روز / کف 8 روز:\n' +\
            str(dayMaxPriceDif) + '  <b>ا</b>  ' + str(pastMaxPriceDif) + '  <b>ا</b>  ' + str(pastMinPriceDif) + '\n\n' +\
            queueStatus +\
            'ارزش معاملات (پول حقیقی):\n' +\
            str(value) + ' ' + realMoneyStr + '  <b>ا</b>  ' + str(weekValue) + '% هفته  <b>ا</b>  ' + str(monthValue) + '% ماه\n\n' +\
            'قدرت خریدار / سرانه خریدار / سرانه فروشنده:\n' +\
            realPowerStr + '  <b>ا</b>  ' + bpStr + '  <b>ا</b>  ' + spStr + '\n\n' + \
            'خرید درشت / فروش درشت:\n' +\
            '\U0001f7e2 ' + str(self.main.heavyTrades.tickersData[ID]['BuyNumber']) + ' بار  <b>ا</b>  ' + \
            str(int(self.main.heavyTrades.tickersData[ID]['BuyVolume']/tickerPresentData.RealBuyVolume*100)) + ' درصد' + '  ➖  ' +\
            '🔴 ' + str(self.main.heavyTrades.tickersData[ID]['SellNumber']) + ' بار  <b>ا</b>  ' + \
            str(int(self.main.heavyTrades.tickersData[ID]['SellVolume']/tickerPresentData.RealSellVolume*100)) + ' درصد\n' +\
            'برآیند معاملات بزرگ:  ' + heavyDealsPrcStr + '\n\n'+\
            'ایچیموکو:\n' +\
            'تنکانسن / کیجنسن:  ' + tenkansenDifStr + tenkansenReactionStr + '  <b>ا</b>  ' + kijunsenDifStr + kijunsenReactionStr + '\n' +\
            'اسپن۱ / اسپن۲:  ' + spanAshiftedDifStr + spanAshiftedReactionStr + '  <b>ا</b>  ' + spanBshiftedDifStr + spanBshiftedReactionStr + '\n' +\
            'کومو بلند۱ / ۲:  ' + tenkansenLongDifStr + tenkansenLongReactionStr + '  <b>ا</b>  ' + kijunsenLongDifStr + kijunsenLongReactionStr + '\n\n'
            
        return msg

    def create_image(self, ID):
        pass

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

    def run_filter(self):
        raise Exception('Not Implemented.')

    def create_report(self):
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
        self.reportTime = [0, 0, 0, 0]

    def run_filter(self):

        nowObj = datetime.datetime.now()
        now = nowObj.hour*3600 + nowObj.minute*60 + nowObj.second

        if self.main.startTime < now < self.main.endTime and nowObj.weekday() not in [3, 4]:

            for ID in self.main.dataHandler.presentData:

                tickerPresentData: presentData = self.main.dataHandler.presentData[ID]

                if tickerPresentData.Volume != None:

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

                                heavyDealsPrc = max(min(int((self.tickersData[ID]['BuyVolume']-self.tickersData[ID]['SellVolume'])/(tickerPresentData.RealBuyVolume+tickerPresentData.CorporateBuyVolume)*100), 100), -100)
                                heavyDealsValue = int((self.tickersData[ID]['BuyVolume']-self.tickersData[ID]['SellVolume'])*tickerPresentData.LastPrice/10**7)
                                
                                if heavyDealsPrc > 0:
                                    heavyDealsPrcStr = str(heavyDealsPrc) + '+ درصد ➖ ' +  str(heavyDealsValue) + '+ م \U0001f7e2'
                                elif heavyDealsPrc < 0:
                                    heavyDealsPrcStr = str(-heavyDealsPrc) + '- درصد ➖ ' + str(-heavyDealsValue) + '- م 🔴'
                                else:
                                    heavyDealsPrcStr = str(heavyDealsPrc)
                                msg += '\nمجموع خریدهای درشت \U0001f7e2  ' +\
                                    str(self.tickersData[ID]['BuyNumber']) + ' بار  ➖ ' + \
                                    str(int(self.tickersData[ID]['BuyVolume']/tickerPresentData.RealBuyVolume*100)) + ' درصد' + '\n' +\
                                    'مجموع فروش های درشت 🔴  ' +\
                                    str(self.tickersData[ID]['SellNumber']) + ' بار  ➖ ' + \
                                    str(int(self.tickersData[ID]['SellVolume']/tickerPresentData.RealSellVolume*100)) + ' درصد' + '\n\n' +\
                                    'برآیند معاملات بزرگ:  ' + heavyDealsPrcStr + '\n\n'
                                
                                tickerPositiveRangeSignals: list[signal] = self.main.positiveRange.tickersData[ID]['Signals']

                                if len(tickerPositiveRangeSignals) != 0 and tickerPresentData.Time-tickerPositiveRangeSignals[-1].time < 30*60:
                                    self.signal_in_telegram(msg+get_time(), positiveRangeChatID, ID, tickerPositiveRangeSignals[-1].messageID)

                                if RealBuyVolumeDif*tickerPresentData.TodayPrice > 500*10**7 or RealSellVolumeDif*tickerPresentData.TodayPrice > 500*10**7:
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
        
        if  self.main.startTime+5*60 < now < self.main.endTime+5*60 and nowObj.weekday() not in [3, 4] and int(now/100)*100 % 900 == 0:
            for i in range(4):
                if now - self.reportTime[i] > 600:
                    break
            else:
                return
            msgs = self.create_report()
            for i in range(4):
                if now - self.reportTime[i] > 600 and send_message(doroshtBinChatID, msgs[i]):
                    self.reportTime[i] = now

    def create_report(self):
        signaledTickers = []
        for ID in self.tickersData:
            try:
                if self.tickersData[ID]['BuyNumber'] or self.tickersData[ID]['SellNumber']:
                    tickerPresentData: presentData = self.main.dataHandler.presentData[ID]
                    lastPricePrc = round((tickerPresentData.LastPrice-tickerPresentData.YesterdayPrice)/tickerPresentData.YesterdayPrice*100, 2)
                    if lastPricePrc >= 0:
                        lastPricePrcStr = '<b>' +str(lastPricePrc) + '+ \U0001f7e2</b>'
                    else:
                        lastPricePrcStr = '<b>' +str(-lastPricePrc) + '- 🔴</b>'
                    heavyDealsPrc = int((self.tickersData[ID]['BuyVolume']-self.tickersData[ID]['SellVolume'])/(tickerPresentData.RealBuyVolume+tickerPresentData.CorporateBuyVolume)*100)
                    heavyDealsValue = int((self.tickersData[ID]['BuyVolume']-self.tickersData[ID]['SellVolume'])*tickerPresentData.LastPrice/10**7)      
                    signaledTickers.append([self.main.tickersInfo[ID]['FarsiTicker'],
                                            heavyDealsPrc,
                                            heavyDealsValue,
                                            lastPricePrcStr
                                            ])
            except:
                print_error('HeavyTrade report ' + str(ID))
        # top high prc
        signaledTickers.sort(key=lambda x: x[1], reverse=True)
        msg1 = '#گزارش معاملات بزرگ:\n\n 30 شرکت با بیشترین برآیند معاملات بزرگ به درصد\n\n'
        for i in range(min(30, len(signaledTickers))):
            heavyDealsPrc = signaledTickers[i][1]
            heavyDealsValue = signaledTickers[i][2]
            if heavyDealsPrc > 0:
                heavyDealsPrcStr = '<b>' +str(heavyDealsPrc) + '+ درصد</b>'
                heavyDealsValueStr = '<b>' +str(heavyDealsValue) + '+ م</b>'
                msg1 += '\U0001f7e2  #' + signaledTickers[i][0] + '➖' + signaledTickers[i][3] + '➖' + heavyDealsPrcStr + '➖' + heavyDealsValueStr + '\n'
        msg1 += '\n' + get_time()
        # top low prc
        signaledTickers.sort(key=lambda x: x[1])
        msg2 = '#گزارش معاملات بزرگ:\n\n 30 شرکت با کمترین برآیند معاملات بزرگ به درصد\n\n'
        for i in range(min(30, len(signaledTickers))):
            heavyDealsPrc = signaledTickers[i][1]
            heavyDealsValue = signaledTickers[i][2]
            if heavyDealsPrc < 0:
                heavyDealsPrcStr = '<b>' +str(-heavyDealsPrc) + '- درصد</b>'
                heavyDealsValueStr = '<b>' +str(-heavyDealsValue) + '- م</b>'
                msg2 += ' 🔴 #' + signaledTickers[i][0] + '➖' + signaledTickers[i][3] + '➖' + heavyDealsPrcStr + '➖' + heavyDealsValueStr + '\n'
        msg2 += '\n' + get_time()
        # top high value
        signaledTickers.sort(key=lambda x: x[2], reverse=True)
        msg3 = '#گزارش معاملات بزرگ:\n\n 30 شرکت با بیشترین برآیند معاملات بزرگ به ارزش\n\n'
        for i in range(min(30, len(signaledTickers))):
            heavyDealsPrc = signaledTickers[i][1]
            heavyDealsValue = signaledTickers[i][2]
            if heavyDealsPrc > 0:
                heavyDealsPrcStr = '<b>' +str(heavyDealsPrc) + '+ درصد</b>'
                heavyDealsValueStr = '<b>' +str(heavyDealsValue) + '+ م</b>'
                msg3 += '\U0001f7e2  #' + signaledTickers[i][0] + '➖' + signaledTickers[i][3] + '➖' + heavyDealsPrcStr + '➖' + heavyDealsValueStr + '\n'
        msg3 += '\n' + get_time()
        # top low value
        signaledTickers.sort(key=lambda x: x[2])
        msg4 = '#گزارش معاملات بزرگ:\n\n 30 شرکت با کمترین برآیند معاملات بزرگ به ارزش\n\n'
        for i in range(min(30, len(signaledTickers))):
            heavyDealsPrc = signaledTickers[i][1]
            heavyDealsValue = signaledTickers[i][2]
            if heavyDealsPrc < 0:
                heavyDealsPrcStr = '<b>' +str(-heavyDealsPrc) + '- درصد</b>'
                heavyDealsValueStr = '<b>' +str(-heavyDealsValue) + '- م</b>'
                msg4 += ' 🔴 #' + signaledTickers[i][0] + '➖' + signaledTickers[i][3] + '➖' + heavyDealsPrcStr + '➖' + heavyDealsValueStr + '\n'
        msg4 += '\n' + get_time()
        return [msg1, msg2, msg3, msg4]
        
class positiveRange(filterParent):

    def __init__(self, main) -> None:
        super().__init__(main)

    def run_filter(self):

        nowObj = datetime.datetime.now()
        now = nowObj.hour*3600 + nowObj.minute*60 + nowObj.second

        if self.main.startTime < now < self.main.endTime and nowObj.weekday() not in [3, 4]:

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

                        if self.tickersData[ID]['IsInFilter'] == False and (len(self.tickersData[ID]['Signals']) == 0 or tickerPresentData.Time-self.tickersData[ID]['Signals'][-1].time > 5*60):

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
        
        if self.main.endTime < now < self.main.endTime + 600 and nowObj.weekday() not in [3, 4] and self.reportTime == 0:
            msg = self.create_report()
            if send_message(positiveRangeChatID, msg):
                self.reportTime = now
    
    def create_report(self):
        signaledTickers = []
        for ID in self.tickersData:
            try:
                if len(self.tickersData[ID]['Signals']) != 0:
                    tickerPresentData: presentData = self.main.dataHandler.presentData[ID]
                    tickerSignals: list[signal] = self.tickersData[ID]['Signals']
                    lastPricePrc = round((tickerPresentData.LastPrice-tickerPresentData.YesterdayPrice)/tickerPresentData.YesterdayPrice*100, 2)
                    if lastPricePrc >= 0:
                        lastPricePrcStr = '<b>' +str(lastPricePrc) + '+ \U0001f7e2</b>'
                    else:
                        lastPricePrcStr = '<b>' +str(-lastPricePrc) + '- 🔴</b>'
                    signaledTickers.append([self.main.tickersInfo[ID]['FarsiTicker'],
                                            len(tickerSignals),
                                            tickerSignals[0].time,
                                            tickerPresentData.MaxPrice == tickerPresentData.MaxAllowedPrice,
                                            lastPricePrcStr
                                            ])
            except:
                print_error('PositiveRange report ' + str(ID))
        signaledTickers.sort(key=lambda x: x[2])
        msg = '#گزارش امروز فیلتر رنج مثبت - حجم مشکوک:\n\n'
        for i in range(len(signaledTickers)):
            buyQueueStatus = '✅' if signaledTickers[i][3] else '❌'
            msg += str(i+1) + '- #' + signaledTickers[i][0] + '➖' + signaledTickers[i][4]+ ' ➖ <b>' + str(signaledTickers[i][1]) + '</b> ➖ ' + buyQueueStatus + '\n'
        msg += '\n' + get_time()
        return msg

class marketManager:

    def __init__(self, main) -> None:

        self.main: filterPlus = main
        self.signals: list[signal] = []
        self.groups = {}

        try: self.groups['کل_بازار'] = tickersGroup(ticker_repo().read_list_of_tickers(tickerTypes = [1], IPO= 0)['ID'])
        except: pass

        try: self.groups['زراعت'] = tickersGroup(ticker_repo().read_list_of_tickers(tickerTypes = [1], industryTypes= [1], IPO= 0)['ID']) 
        except: pass
        try: self.groups['استخراج_کانه_های_فلزی'] = tickersGroup(ticker_repo().read_list_of_tickers(tickerTypes = [1], industryTypes= [4], IPO= 0)['ID']) 
        except: pass
        try: self.groups['فرآورده_های_نفتی'] = tickersGroup(ticker_repo().read_list_of_tickers(tickerTypes = [1], industryTypes= [11], IPO= 0)['ID'])
        except: pass
        try: self.groups['لاستیک_و_پلاستیک'] = tickersGroup(ticker_repo().read_list_of_tickers(tickerTypes = [1], industryTypes= [12], IPO= 0)['ID'])
        except: pass
        try: self.groups['فلزات_اساسی'] = tickersGroup(ticker_repo().read_list_of_tickers(tickerTypes = [1], industryTypes= [14], IPO= 0)['ID']) 
        except: pass
        try: self.groups['ساخت_محصولات_فلزی'] = tickersGroup(ticker_repo().read_list_of_tickers(tickerTypes = [1], industryTypes= [15], IPO= 0)['ID'])   
        except: pass
        try: self.groups['ماشین_آلات_و_تجهیزات'] = tickersGroup(ticker_repo().read_list_of_tickers(tickerTypes = [1], industryTypes= [16], IPO= 0)['ID'])   
        except: pass
        try: self.groups['دستگاه_های_برقی'] = tickersGroup(ticker_repo().read_list_of_tickers(tickerTypes = [1], industryTypes= [17], IPO= 0)['ID']) 
        except: pass
        try: self.groups['فراکاب'] = tickersGroup(ticker_repo().read_list_of_tickers(tickerTypes = [1], industryTypes= [41], IPO= 0)['ID']) 
        except: pass
        try: self.groups['خودرو_و_قطعات'] = tickersGroup(ticker_repo().read_list_of_tickers(tickerTypes = [1], industryTypes= [19], IPO= 0)['ID'])
        except: pass
        try: self.groups['قند_و_شکر'] = tickersGroup(ticker_repo().read_list_of_tickers(tickerTypes = [1], industryTypes= [20], IPO= 0)['ID']) 
        except: pass
        try: self.groups['نیروگاهی'] = tickersGroup(ticker_repo().read_list_of_tickers(tickerTypes = [1], industryTypes= [22], IPO= 0)['ID'])
        except: pass
        try: self.groups['غذایی'] = tickersGroup(ticker_repo().read_list_of_tickers(tickerTypes = [1], industryTypes= [23], IPO= 0)['ID']) 
        except: pass
        try: self.groups['دارویی'] = tickersGroup(ticker_repo().read_list_of_tickers(tickerTypes = [1], industryTypes= [24], IPO= 0)['ID']) 
        except: pass
        try: self.groups['شیمیایی'] = tickersGroup(ticker_repo().read_list_of_tickers(tickerTypes = [1], industryTypes= [25], IPO= 0)['ID']) 
        except: pass
        try: self.groups['کاشی_و_سرامیک'] = tickersGroup(ticker_repo().read_list_of_tickers(tickerTypes = [1], industryTypes= [29], IPO= 0)['ID'])
        except: pass
        try: self.groups['سیمانی'] = tickersGroup(ticker_repo().read_list_of_tickers(tickerTypes = [1], industryTypes= [30], IPO= 0)['ID']) 
        except: pass
        try: self.groups['کانی_غیر_فلزی'] = tickersGroup(ticker_repo().read_list_of_tickers(tickerTypes = [1], industryTypes= [31], IPO= 0)['ID']) 
        except: pass
        try: self.groups['سرمایه_گذاری'] = tickersGroup(ticker_repo().read_list_of_tickers(tickerTypes = [1], industryTypes= [33], IPO= 0)['ID'])  
        except: pass
        try: self.groups['بانکی'] = tickersGroup(ticker_repo().read_list_of_tickers(tickerTypes = [1], industryTypes= [34], IPO= 0)['ID']) 
        except: pass
        try: self.groups['واسطه_گری_مالی'] = tickersGroup(ticker_repo().read_list_of_tickers(tickerTypes = [1], industryTypes= [35], IPO= 0)['ID']) 
        except: pass
        try: self.groups['حمل_و_نقل'] = tickersGroup(ticker_repo().read_list_of_tickers(tickerTypes = [1], industryTypes= [36], IPO= 0)['ID']) 
        except: pass
        try: self.groups['بیمه'] = tickersGroup(ticker_repo().read_list_of_tickers(tickerTypes = [1], industryTypes= [40], IPO= 0)['ID']) 
        except: pass
        try: self.groups['انبوه_سازی'] = tickersGroup(ticker_repo().read_list_of_tickers(tickerTypes = [1], industryTypes= [43], IPO= 0)['ID']) 
        except: pass
        try: self.groups['رایانه'] = tickersGroup(ticker_repo().read_list_of_tickers(tickerTypes = [1], industryTypes= [45], IPO= 0)['ID']) 
        except: pass
        
        self.marketTrend: marketTrend = marketTrend(self)
        self.marketRise: marketRise = marketRise(self)

    def run_filters(self):

        for groupName in self.groups:
            groupData: tickersGroup = self.groups[groupName]
            groupData.update(self.main)

        self.marketTrend.run_filter()
        self.marketRise.run_filter()

class tickersGroup:

    def __init__(self, IDList: list) -> None:

        self.IDList = IDList

        self.Time = []
        self.TickersNumber = []
        self.PositiveTickersPrc = []
        self.BuyQueueTickersPrc = []
        self.SellQueueTickersPrc = []
        self.LastPricePrcAverage = []
        self.TodayPricePrcAverage = []
        self.TotalValue = []
        self.BuyQueuesValue = []
        self.SellQueuesValue = []
        self.RealMoneyEntryValue = []
        self.DemandValue = []
        self.SupplyValue = []
        self.RealPowerHamvazn = []
        self.RealPowerKol = []
        self.RealPowerHamvaznDif = []
        self.RealPowerKolDif = []
        self.HeavyBuysValue = []
        self.HeavySellsValue = []
        self.HeavyBuysNumber = []
        self.HeavySellsNumber = []
        self.HeavyDealsPrc = []
        
    def update(self, main: filterPlus) -> None:

        tickersNumber = 0
        positiveTickersNumber = 0
        buyQueueTickersNumber = 0
        sellQueueTickersNumber = 0
        lastPricePrcSum = 0
        todayPricePrcSum = 0
        totalValue = 0
        buyQueuesValue = 0
        sellQueuesValue = 0
        realMoneyEntryValue = 0
        demandValue = 0
        supplyValue = 0
        realPowerLogSum = 0
        realBuyValue = 0
        realBuyNumber = 0
        realSellValue = 0
        realSellNumber = 0
        realPowerLogDifSum = 0
        realBuyValueDif = 0
        realBuyNumberDif = 0
        realSellValueDif = 0
        realSellNumberDif = 0
        heavyBuysValue = 0
        heavySellsValue = 0
        heavyBuysNumber = 0
        heavySellsNumber = 0
        heavyDealsPrc = 0

        for ID in self.IDList:

            try:
            
                tickerPresentData: presentData = main.dataHandler.presentData[ID]

                lastPricePRC = (tickerPresentData.LastPrice-tickerPresentData.YesterdayPrice)/tickerPresentData.YesterdayPrice * 100
                todayPricePRC = (tickerPresentData.TodayPrice-tickerPresentData.YesterdayPrice)/tickerPresentData.YesterdayPrice * 100

                if lastPricePRC >= 0:
                    positiveTickersNumber += 1

                if tickerPresentData.LastPrice == tickerPresentData.MaxAllowedPrice:
                    buyQueueTickersNumber += 1
                    buyQueuesValue += tickerPresentData.DemandPrice1 * tickerPresentData.DemandVolume1
                
                elif tickerPresentData.LastPrice == tickerPresentData.MinAllowedPrice:
                    sellQueueTickersNumber += 1
                    sellQueuesValue += tickerPresentData.SupplyPrice1 * tickerPresentData.SupplyVolume1

                lastPricePrcSum += lastPricePRC
                todayPricePrcSum += todayPricePRC

                totalValue += tickerPresentData.TodayPrice * tickerPresentData.Volume
                
                realMoneyEntryValue += (tickerPresentData.RealBuyVolume-tickerPresentData.RealSellVolume)*tickerPresentData.TodayPrice

                tickersNumber += 1

            except:
                continue

            for i in range(1, 6):
                try:
                    if getattr(tickerPresentData, f'SupplyPrice{i}') <= tickerPresentData.MaxAllowedPrice and getattr(tickerPresentData, f'SupplyPrice{i}') != tickerPresentData.MinAllowedPrice:
                        supplyValue += getattr(tickerPresentData, f'SupplyPrice{i}') * getattr(tickerPresentData, f'SupplyVolume{i}')
                    if getattr(tickerPresentData, f'DemandPrice{i}') >= tickerPresentData.MinAllowedPrice and getattr(tickerPresentData, f'DemandPrice{i}') != tickerPresentData.MaxAllowedPrice:
                        demandValue += getattr(tickerPresentData, f'DemandPrice{i}') * getattr(tickerPresentData, f'DemandVolume{i}')
                except:
                    pass

            try:
                realPowerLogSum += log10((tickerPresentData.RealBuyVolume/tickerPresentData.RealBuyNumber)/(tickerPresentData.RealSellVolume/tickerPresentData.RealSellNumber))
                realBuyValue += tickerPresentData.RealBuyVolume * tickerPresentData.TodayPrice
                realBuyNumber += tickerPresentData.RealBuyNumber
                realSellValue += tickerPresentData.RealSellVolume * tickerPresentData.TodayPrice
                realSellNumber += tickerPresentData.RealSellNumber
            except:
                pass
                
            try:

                tickerHistory: historyData = main.dataHandler.history['1m'][ID]

                indice = -min(len(tickerHistory.LastPrice), 60)

                realPowerLogDifSum += log10(((tickerPresentData.RealBuyVolume-tickerHistory.RealBuyVolume[indice])/(tickerPresentData.RealBuyNumber-tickerHistory.RealBuyNumber[indice]))/((tickerPresentData.RealSellVolume-tickerHistory.RealSellVolume[indice])/(tickerPresentData.RealSellNumber-tickerHistory.RealSellNumber[indice])))
                
                realBuyValueDif += (tickerPresentData.RealBuyVolume-tickerHistory.RealBuyVolume[indice]) * tickerPresentData.TodayPrice
                realBuyNumberDif += tickerPresentData.RealBuyNumber-tickerHistory.RealBuyNumber[indice]
                realSellValueDif += (tickerPresentData.RealSellVolume-tickerHistory.RealSellVolume[indice]) * tickerPresentData.TodayPrice
                realSellNumberDif += tickerPresentData.RealSellNumber-tickerHistory.RealSellNumber[indice]

            except:
                pass

            try:
                tickerHeavyDealsData = main.heavyTrades.tickersData[ID]

                heavyBuysValue += tickerHeavyDealsData['BuyVolume']*tickerPresentData.LastPrice
                heavySellsValue += tickerHeavyDealsData['SellVolume']*tickerPresentData.LastPrice
                heavyBuysNumber += tickerHeavyDealsData['BuyNumber']
                heavySellsNumber += tickerHeavyDealsData['SellNumber']
                heavyDealsPrc += (tickerHeavyDealsData['BuyVolume']-tickerHeavyDealsData['SellVolume'])/tickerPresentData.Volume*100
            except:
                pass

        if tickersNumber == 0:
            return

        self.Time.append(datetime.datetime.now())
        self.TickersNumber.append(tickersNumber)
        self.PositiveTickersPrc.append(round(positiveTickersNumber / tickersNumber * 100, 1))
        self.BuyQueueTickersPrc.append(round(buyQueueTickersNumber / tickersNumber * 100, 1))
        self.SellQueueTickersPrc.append(round(sellQueueTickersNumber / tickersNumber * 100, 1))
        self.LastPricePrcAverage.append(round(lastPricePrcSum / tickersNumber, 2))
        self.TodayPricePrcAverage.append(round(todayPricePrcSum / tickersNumber, 2))
        self.TotalValue.append(round(totalValue / 10**10, 1))
        self.BuyQueuesValue.append(round(buyQueuesValue / 10**10, 1))
        self.SellQueuesValue.append(round(sellQueuesValue / 10**10, 1))
        self.RealMoneyEntryValue.append(round(realMoneyEntryValue / 10**10, 1))
        self.DemandValue.append(round(demandValue / 10**10, 1))
        self.SupplyValue.append(round(supplyValue / 10**10, 1))

        self.RealPowerHamvazn.append(round(10**(realPowerLogSum / tickersNumber), 2))
        try:
            self.RealPowerKol.append(round((realBuyValue/realBuyNumber)/(realSellValue/realSellNumber), 2))
        except:
            self.RealPowerKol.append(1)

        self.RealPowerHamvaznDif.append(round(10**(realPowerLogDifSum / tickersNumber), 2))
        try:
            self.RealPowerKolDif.append(round((realBuyValueDif/realBuyNumberDif)/(realSellValueDif/realSellNumberDif), 2))
        except:
            self.RealPowerKolDif.append(1)

        self.HeavyBuysValue.append(round(heavyBuysValue / 10**10, 1))
        self.HeavySellsValue.append(round(heavySellsValue / 10**10, 1))
        self.HeavyBuysNumber.append(heavyBuysNumber)
        self.HeavySellsNumber.append(heavySellsNumber)
        self.HeavyDealsPrc.append(round(heavyDealsPrc / tickersNumber, 1))
        
class marketFilter:

    def __init__(self, manager: marketManager) -> None:

        self.manager: marketManager = manager
        self.filterName = self.__class__.__name__
        self.isInFilter = False

        self.groupsData = {groupName: {'Signals': [], 'IsInFilter': False} for groupName in self.manager.groups}

    def create_general_telegram_message(self, groupName):

        industryData: tickersGroup = self.manager.groups[groupName]
        index = industryData.LastPricePrcAverage[-1]
        trend = '<b>صعودی\U0001f7e2</b>' if self.manager.marketTrend.groupsData[groupName]['Trend'] else '<b>نزولی🔴</b>'
        buyQueueTickersPrc = industryData.BuyQueueTickersPrc[-1]
        sellQueueTickersPrc = industryData.SellQueueTickersPrc[-1]
        realPowerKol = industryData.RealPowerKol[-1]
        realPowerKolDif = industryData.RealPowerKolDif[-1]
        realPowerHamvazn = industryData.RealPowerHamvazn[-1]
        realPowerHamvaznDif = industryData.RealPowerHamvaznDif[-1]
        realMoney = industryData.RealMoneyEntryValue[-1]
        heavyBuysValue = industryData.HeavyBuysValue[-1]
        heavySellsValue = industryData.HeavySellsValue[-1]
        heavyDealsValue = round(heavyBuysValue-heavySellsValue, 1)
        heavyDealsPrc = industryData.HeavyDealsPrc[-1]

        if index >= 0:
            indexStr = '<b>' +str(index) + '+ </b>\U0001f7e2'
        else:
            indexStr = '<b>' +str(-index) + '- </b>🔴'

        buyQueueTickersPrcStr = '<b>' +str(buyQueueTickersPrc) + '</b>'
        
        sellQueueTickersPrcStr = '<b>' +str(sellQueueTickersPrc) + '</b>'
        
        if realPowerKol >= 1:
            realPowerKolStr = '<b>' +str(realPowerKol) + '+ </b>\U0001f7e2'
        else:
            realPowerKolStr = '<b>' +str(round(1/realPowerKol, 2)) + '- </b>🔴'
        
        if realPowerKolDif >= 1:
            realPowerKolDifStr = '<b>' +str(realPowerKolDif) + '+ </b>\U0001f7e2'
        else:
            realPowerKolDifStr = '<b>' +str(round(1/realPowerKolDif, 2)) + '- </b>🔴'

        if realPowerHamvazn >= 1:
            realPowerHamvaznStr = '<b>' +str(realPowerHamvazn) + '+ </b>\U0001f7e2'
        else:
            realPowerHamvaznStr = '<b>' +str(round(1/realPowerHamvazn, 2)) + '- </b>🔴'
        
        if realPowerHamvaznDif >= 1:
            realPowerHamvaznDifStr = '<b>' +str(realPowerHamvaznDif) + '+ </b>\U0001f7e2'
        else:
            realPowerHamvaznDifStr = '<b>' +str(round(1/realPowerHamvaznDif, 2)) + '- </b>🔴'
        
        if realMoney >= 0:
            realMoneyStr = '<b>' +str(realMoney) + '+ </b>\U0001f7e2'
        else:
            realMoneyStr = '<b>' +str(-realMoney) + '- </b>🔴'
        
        heavyBuysValueStr = '<b>' +str(heavyBuysValue) + '</b>'
        heavySellsValueStr = '<b>' +str(heavySellsValue) + '</b>'

        if heavyDealsValue > 0:
            heavyDealsValueStr = '<b>' +str(heavyDealsValue) + '+ </b>\U0001f7e2'
        elif heavyDealsValue < 0:
            heavyDealsValueStr = '<b>' +str(-heavyDealsValue) + '- </b>🔴'
        else:
            heavyDealsValueStr = '<b>0</b>'
        
        if heavyDealsPrc > 0:
            heavyDealsPrcStr = '<b> ( ' +str(heavyDealsPrc) + '+ درصد \U0001f7e2 )</b>'
        elif heavyDealsPrc < 0:
            heavyDealsPrcStr = '<b> ( ' +str(-heavyDealsPrc) + '- درصد 🔴 )</b>'
        else:
            heavyDealsPrcStr = '<b> ( 0 درصد )</b>'
        
        msg = '📈 #' + groupName +'\n\n' +\
        'شاخص:  ' + indexStr + '\n' +\
        'ترند:  ' + trend + '\n' +\
        'درصد صف خرید:  ' + buyQueueTickersPrcStr + '\n' +\
        'درصد صف فروش:  ' + sellQueueTickersPrcStr + '\n' +\
        'قدرت خریدار کل:  ' + realPowerKolStr + '\n' +\
        'قدرت خریدار کل لحظه ای:  ' + realPowerKolDifStr + '\n' +\
        'قدرت خریدار هم وزن:  ' + realPowerHamvaznStr + '\n' +\
        'قدرت خریدار هم وزن لحظه ای:  ' + realPowerHamvaznDifStr + '\n' +\
        'پول حقیقی:  ' + realMoneyStr + '\n' +\
        'خرید درشت:  ' + heavyBuysValueStr + '\n' +\
        'فروش درشت:  ' + heavySellsValueStr + '\n' +\
        'برآیند معاملات بزرگ:  ' + heavyDealsValueStr + heavyDealsPrcStr + '\n\n'

        # create image
        fig, ax = plt.subplots(2, 2)
        labelSize = 6
        period = 60
        barWidth = 0.00001 * period
        ax[0][0].plot(industryData.Time, industryData.LastPricePrcAverage, label= 'Present Index')
        ax[0][0].plot(industryData.Time, industryData.TodayPricePrcAverage, label= 'Total Index')
        ax[0][0].legend(loc= "upper right", prop={'size': labelSize})

        ax[0][1].plot(industryData.Time, industryData.PositiveTickersPrc, label= 'Positive', color= 'blue')
        ax[0][1].plot(industryData.Time, industryData.BuyQueueTickersPrc, label= 'Buy Queue', color= 'green')
        ax[0][1].plot(industryData.Time, industryData.SellQueueTickersPrc, label= 'Sell Queue', color= 'red')
        ax[0][1].legend(loc= "upper right", prop={'size': labelSize})

        heavyDealsValue = [industryData.HeavyBuysValue[i]-industryData.HeavySellsValue[i] for i in range(len(industryData.Time))]
        clrs = ['red' if (x < 0) else 'green' for x in heavyDealsValue]
        ax[1][0].bar(industryData.Time, heavyDealsValue, color= clrs, label= 'Smart Money', width= barWidth)
        ax[1][0].plot(industryData.Time, industryData.RealMoneyEntryValue, color= 'blue', label= 'Real Money')
        ax[1][0].legend(loc= "upper right", prop={'size': labelSize})

        realPowerDif = [log10(item) for item in industryData.RealPowerHamvaznDif]
        clrs = ['red' if (x < 0) else 'green' for x in realPowerDif]
        ax[1][1].bar(industryData.Time, realPowerDif, color= clrs, label= 'Real Power', width= barWidth)
        ax[1][1].axhline(log10(1.5))
        ax[1][1].axhline(-log10(1.5))  
        ax[1][1].legend(loc= "upper right", prop={'size': labelSize})
        ax2 = ax[1][1].twinx()
        ax2.plot(industryData.Time, industryData.HeavyDealsPrc)
        prcMax = max(industryData.HeavyDealsPrc)
        prcMin = min(industryData.HeavyDealsPrc)
        ax2.set_ylim([-1.2*max(abs(prcMin), abs(prcMax)), 1.2*max(abs(prcMin), abs(prcMax))])
        ax2.legend(loc= "upper left", prop={'size': labelSize})

        today = datetime.datetime.now().date()
        startLim = datetime.datetime(today.year, today.month, today.day, 9, 0)
        stopLim = datetime.datetime(today.year, today.month, today.day, 12, 30)
        for i in range(2):
            for j in range(2):
                ax[i][j].grid(linestyle = '--', linewidth = 0.5)
                ax[i][j].spines['bottom'].set_color('white')
                ax[i][j].spines['top'].set_color('white') 
                ax[i][j].spines['right'].set_color('white')
                ax[i][j].spines['left'].set_color('white')
                myFmt = mdates.DateFormatter("%H:%M")
                ax[i][j].xaxis.set_major_formatter(myFmt)
                ax[i][j].set_xlim([startLim, stopLim])
        ax2.grid(linestyle = '--', linewidth = 0.5)
        ax2.spines['bottom'].set_color('white')
        ax2.spines['top'].set_color('white') 
        ax2.spines['right'].set_color('white')
        ax2.spines['left'].set_color('white')
        fig.savefig('market.png', dpi= 350)
        plt.close()

        return msg

    def signal_in_telegram(self, telegramMessage, telegramID, groupName, replyMessageID= None):

        if replyMessageID == None:
            groupSignals: list[signal] = self.groupsData[groupName]['Signals']
            if len(groupSignals) == 0:
                replyMessageID = None
            else:
                replyMessageID = groupSignals[-1].messageID
        elif replyMessageID == False:
            replyMessageID = None

        messageID = send_message(telegramID, telegramMessage, replyMessageID)
        
        return messageID
    
    def store_signal_info(self, groupName, signalSpec, messageID):

            thisSignal = signal()
            now = datetime.datetime.now()
            now = now.hour*3600 + now.minute*60 + now.second
            thisSignal.time = now
            thisSignal.ID = groupName
            thisSignal.filterName = self.filterName
            thisSignal.signalSpec = signalSpec
            thisSignal.messageID = messageID
            self.groupsData[groupName]['Signals'].append(thisSignal)

    def run_filter(self):
        raise Exception('Not Implemented.')

class marketTrend(marketFilter):
    
    def __init__(self, manager: marketManager) -> None:
        super().__init__(manager)

        for groupName in self.groupsData:
            self.groupsData[groupName]['Trend'] = None
            self.groupsData[groupName]['LastTime'] = 0

    def run_filter(self):

        now = datetime.datetime.now()
        now = now.hour*3600 + now.minute*60 + now.second

        for groupName in self.manager.groups:

            industryData: tickersGroup = self.manager.groups[groupName]

            trendChange = False

            if len(industryData.Time) == 5:
                indexMa = sum(industryData.LastPricePrcAverage)/5
                trendChange = True
                if industryData.LastPricePrcAverage[-1] >= indexMa:
                    self.groupsData[groupName]['Trend'] = True
                else:
                    self.groupsData[groupName]['Trend'] = False

            if len(industryData.Time) >= 10:
                
                indexAvg = sum(industryData.LastPricePrcAverage[-15:])/len(industryData.LastPricePrcAverage[-15:])
                changeLimit = min(self.manager.groups['کل_بازار'].TickersNumber[-1] / industryData.TickersNumber[-1] * 0.1, 0.5)

                if self.groupsData[groupName]['Trend'] == False:
                    minIndex = min(industryData.LastPricePrcAverage[-15:])
                    if industryData.LastPricePrcAverage[-1] > minIndex + changeLimit and industryData.LastPricePrcAverage[-1] > indexAvg:
                        self.groupsData[groupName]['Trend'] = True
                        trendChange = True
                        print('up')

                else:
                    maxIndex = max(industryData.LastPricePrcAverage[-15:])
                    if industryData.LastPricePrcAverage[-1] < maxIndex - changeLimit and industryData.LastPricePrcAverage[-1] < indexAvg:
                        self.groupsData[groupName]['Trend'] = False
                        trendChange = True
                        print('down')

            if groupName == 'کل_بازار':

                if trendChange or now-self.groupsData[groupName]['LastTime'] > 3*60 and int(now/100)*100 % 900 == 0 and now > 9*3600+4*60:
            
                    telegramMessage = self.create_general_telegram_message(groupName)

                    if trendChange and self.groupsData[groupName]['LastTime'] != 0:
                        telegramMessage += '<b>هشدار تغییر روند</b>\n\n'

                    if send_photo(marketTrendChatID, 'market.png', telegramMessage + get_time()):
                        self.groupsData[groupName]['LastTime'] = now
                        print('Market trend signaled.')
                    else:
                        print('Error sending market image')
            
class marketRise(marketFilter):
    
    def __init__(self, manager: marketManager) -> None:
        super().__init__(manager)

        for groupName in self.groupsData:
            self.groupsData[groupName]['LastTime'] = None

    def run_filter(self):

        now = datetime.datetime.now()
        now = now.hour*3600 + now.minute*60 + now.second

        for groupName in self.manager.groups:

            industryData: tickersGroup = self.manager.groups[groupName]

            if len(industryData.LastPricePrcAverage) >= 6 and industryData.TickersNumber[-1] > 10:

                changeLimit = min(self.manager.groups['کل_بازار'].TickersNumber[-1] / industryData.TickersNumber[-1] * 0.4, 1)
                priceDif = industryData.LastPricePrcAverage[-1] - industryData.LastPricePrcAverage[-6]
                    
                if priceDif > changeLimit:
                    
                    if now-self.groupsData[groupName]['LastTime'] > 280:
                        
                        self.groupsData[groupName]['LastTime'] = now

                        filterMessage = '<b>رنج مثبت ' + str(round(priceDif, 1)) + ' درصدی</b>\n\n'
                        telegramMessage = self.create_general_telegram_message(groupName) + filterMessage + get_time()
                        if send_photo(marketTrendChatID, 'market.png', telegramMessage):
                            self.groupsData[groupName]['LastTime'] = now
                            print('Market trend signaled.')
                        else:
                            print('Error sending market image')
