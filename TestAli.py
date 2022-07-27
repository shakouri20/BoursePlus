
from cmath import nan
import datetime
import threading
import time
from matplotlib import pyplot as plt
import numpy as np
from Application.Services.WriteData.GetOnlineDataService import get_last_clientType_Data, get_marketWatch_data_tse_method
from Application.Utility.AdvancedPlot import advancedPlot
from Infrastructure.Repository.OfflineDataRepository import offlineData_repo
from TelegramProject.TelegramBot import *
import timeit, os, sys
from TelegramProject.main import print_error

import matplotlib
matplotlib.rc('xtick', labelsize=5) 
matplotlib.rc('ytick', labelsize=5) 

# # output = get_marketWatch_data_tse_method(init= 1)
# # output = get_marketWatch_data_tse_method(heven= 100000, refid= 10434169200)
# # output = get_marketWatch_data_tse_method(heven= output['Heven'], refid= output['Refid'])
# buy = [0.0, 0.2, 0.2, 0.2, 0.5, 0.5, 0.5, 0.7, 0.9, 3.2, 4.3, 4.3, 4.6, 5.3, 6.3, 6.5, 6.9, 8.3, 9.8, 11.3, 15.3, 15.8, 16.2, 16.2, 16.2, 16.5, 17.2, 17.4, 18.5, 18.6, 18.7, 18.9, 18.9, 19.5, 19.4, 21.4, 21.7, 22.0, 23.0, 25.6, 26.5, 26.7, 26.7, 27.9, 28.9, 29.1, 29.8, 30.7, 30.8, 32.7, 33.0, 33.3, 34.6, 34.6, 35.1, 35.6, 36.0, 36.0, 36.0, 37.0, 37.0, 37.0, 37.4, 37.7, 37.9, 37.9, 37.9, 38.9, 39.3, 40.0, 40.3, 40.7, 40.8, 41.1, 41.6, 41.8, 42.2, 42.3, 43.4, 43.5, 43.7, 43.7, 44.2, 44.4, 44.3, 44.9, 44.9, 45.1, 45.2, 45.5, 45.5, 45.8, 46.1, 46.1, 46.5, 46.6, 46.7, 46.9, 47.2, 47.6, 47.5, 49.0, 49.2, 49.3, 49.4, 49.4, 50.0, 50.0, 50.1, 50.5, 50.7, 50.7, 50.7, 50.9, 51.2, 51.2, 51.7, 52.3, 52.3, 52.5, 52.5, 52.5, 52.5, 52.7, 52.7, 52.7, 53.3, 53.4, 53.9, 54.2, 54.3, 54.7, 55.2, 56.0, 56.4, 56.6, 56.8, 57.1, 57.6, 57.6, 58.0, 58.3, 59.2, 60.1, 60.0, 60.1, 60.1, 61.4, 61.5, 61.5, 61.8, 62.3, 62.3, 62.8, 63.3, 63.3, 64.1, 64.6, 64.6, 65.0, 65.1, 65.1, 65.2, 65.5, 65.5, 66.0, 67.8, 68.4, 69.0, 69.0, 69.5, 69.6, 71.1, 71.1, 71.7, 72.8, 72.8, 72.8, 72.8, 73.6, 73.6, 73.8, 73.8, 74.2, 76.9, 82.5, 87.0, 88.6, 91.2, 91.9, 98.0, 104.6]
# sell = [0.0, 0.8, 1.6, 4.4, 6.5, 7.0, 9.9, 13.5, 16.0, 17.0, 19.6, 21.8, 24.1, 25.4, 28.0, 33.9, 37.6, 39.8, 47.8, 52.9, 59.8, 60.9, 66.3, 69.7, 70.3, 72.4, 75.0, 77.1, 77.7, 78.9, 81.6, 82.3, 83.3, 83.5, 88.1, 91.8, 93.2, 94.7, 98.9, 109.5, 112.3, 115.1, 115.4, 120.4, 124.2, 124.9, 127.7, 128.6, 132.0, 134.9, 135.3, 136.5, 139.1, 139.5, 141.0, 141.6, 142.0, 142.3, 142.8, 144.0, 145.2, 145.5, 146.2, 147.6, 148.2, 149.0, 150.6, 153.9, 155.7, 156.7, 157.5, 158.3, 159.3, 161.1, 161.5, 163.8, 164.8, 165.8, 166.3, 168.9, 169.5, 170.0, 171.2, 172.0, 172.5, 174.0, 174.5, 175.5, 175.6, 175.8, 175.8, 176.7, 177.5, 178.9, 180.2, 180.8, 183.9, 184.4, 185.4, 188.2, 189.4, 190.1, 191.5, 192.5, 193.2, 194.2, 196.1, 198.4, 198.5, 200.3, 200.3, 202.3, 202.6, 203.4, 203.9, 203.9, 205.5, 220.9, 221.8, 222.4, 223.9, 224.7, 225.6, 226.3, 227.4, 228.2, 228.8, 229.5, 230.1, 230.6, 234.5, 235.2, 235.2, 241.0, 242.6, 243.3, 245.0, 245.5, 245.6, 246.1, 246.3, 247.1, 247.7, 249.4, 249.7, 249.7, 250.0, 253.9, 255.4, 255.3, 256.6, 257.5, 259.2, 261.2, 263.3, 265.4, 266.1, 266.8, 267.4, 268.0, 270.4, 270.4, 271.5, 272.1, 273.9, 273.9, 274.1, 276.5, 277.4, 277.4, 277.7, 280.4, 281.8, 281.8, 281.9, 284.4, 284.4, 285.4, 286.6, 287.9, 288.6, 290.8, 291.5, 294.2, 295.5, 302.9, 308.4, 309.9, 315.9, 320.0, 329.1, 337.6]
# dif = [buy[i]-sell[i] for i in range(len(buy))]
# # plt.plot(buy)
# # plt.plot(sell)
# fig, ax = plt.subplots(2, 2)#, figsize=(15,15)
# ax[0][0].plot(buy)
# ax[0][1].plot(sell)
# ax[1][0].plot(dif)
# for i in range(2):
#     for j in range(2):
#         ax[i][j].grid(linestyle = '--', linewidth = 0.5)
#         ax[i][j].spines['bottom'].set_color('white')
#         ax[i][j].spines['top'].set_color('white') 
#         ax[i][j].spines['right'].set_color('white')
#         ax[i][j].spines['left'].set_color('white')

#     # for tick in ax[i][j].xaxis.get_major_ticks():
#     #     tick.label.set_fontsize(8) 
#     #     tick.label.set_rotation('vertical')
#     # for tick in ax[i][j].yaxis.get_major_ticks():
#     #     tick.label.set_fontsize(8) 

# fig.savefig('testtt.png', dpi= 200)

# send_photo(myTelegramAcountChatID, 'testtt.png', '''📈 #کل_بازار

# شاخص:  <b>3.9- </b>🔴
# ترند:  <b>صعودی🟢</b>
# درصد صف خرید:  <b>1.3</b>
# درصد صف فروش:  <b>39.6</b>
# قدرت خریدار کل:  <b>1.61- </b>🔴
# قدرت خریدار کل لحظه ای:  <b>1.47- </b>🔴
# قدرت خریدار هم وزن:  <b>1.72- </b>🔴
# قدرت خریدار هم وزن لحظه ای:  <b>1.75- </b>🔴
# پول حقیقی:  <b>522.8- </b>🔴
# خرید درشت:  <b>104.6</b>
# فروش درشت:  <b>337.6</b>
# برآیند معاملات بزرگ:  <b>233.0- </b>🔴<b> ( 8.9- درصد 🔴 )</b>''')



# global create_general_telegram_message
# def create_general_telegram_message(self, groupName):

#     industryData: tickersGroup = self.manager.groups[groupName]
#     # create image
#     fig, ax = plt.subplots(2, 2)
#     labelSize = 6
#     period = 60
#     barWidth = 0.00001 * period
#     ax[0][0].plot(industryData.Time, industryData.LastPricePrcAverage, label= 'Present Index')
#     ax[0][0].plot(industryData.Time, industryData.TodayPricePrcAverage, label= 'Total Index')
#     ax[0][0].legend(prop={'size': labelSize})

#     ax[0][1].plot(industryData.Time, industryData.PositiveTickersPrc, label= 'Positive', color= 'blue')
#     ax[0][1].plot(industryData.Time, industryData.BuyQueueTickersPrc, label= 'Buy Queue', color= 'green')
#     ax[0][1].plot(industryData.Time, industryData.SellQueueTickersPrc, label= 'Sell Queue', color= 'red')
#     ax[0][1].legend(prop={'size': labelSize})

#     heavyDealsValue = [industryData.HeavyBuysValue[i]-industryData.HeavySellsValue[i] for i in range(len(industryData.Time))]
#     clrs = ['red' if (x < 0) else 'green' for x in heavyDealsValue]
#     ax[1][0].bar(industryData.Time, heavyDealsValue, label= 'Smart Money', width= barWidth, color= clrs) # 
#     ax[1][0].plot(industryData.Time, [0 for _ in range(len(industryData.Time))], color= 'blue')
#     ax[1][0].plot(industryData.Time, industryData.RealMoneyEntryValue, color= 'blue', label= 'Real Money')
#     ax[1][0].legend(prop={'size': labelSize})

#     realPowerDif = [log10(item) for item in industryData.RealPowerHamvaznDif]
#     clrs = ['red' if (x < 0) else 'green' for x in realPowerDif]
#     ax[1][1].bar(industryData.Time, realPowerDif, label= 'Real Power', width= barWidth, color= clrs) # 
#     ax[1][1].plot(industryData.Time, [log10(2) for _ in range(len(industryData.Time))], color= 'blue')
#     ax[1][1].plot(industryData.Time, [0 for _ in range(len(industryData.Time))], color= 'blue')
#     ax[1][1].plot(industryData.Time, [-log10(2) for _ in range(len(industryData.Time))], color= 'blue')
#     ax[1][1].legend(prop={'size': labelSize})

#     today = datetime.datetime.now().date()
#     startLim = datetime.datetime(today.year, today.month, today.day, 9, 0)
#     stopLim = datetime.datetime(today.year, today.month, today.day, 12, 30)
#     for i in range(2):
#         for j in range(2):
#             ax[i][j].grid(linestyle = '--', linewidth = 0.5)
#             ax[i][j].spines['bottom'].set_color('white')
#             ax[i][j].spines['top'].set_color('white') 
#             ax[i][j].spines['right'].set_color('white')
#             ax[i][j].spines['left'].set_color('white')
#             myFmt = mdates.DateFormatter("%H-%M")
#             ax[i][j].xaxis.set_major_formatter(myFmt)
#             ax[i][j].set_xlim([startLim, stopLim])
#     fig.savefig('market.png', dpi= 350)
#     plt.close()

a = '''def create_general_telegram_message(self, groupName):

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
    ax[0][0].legend(prop={'size': labelSize})

    ax[0][1].plot(industryData.Time, industryData.PositiveTickersPrc, label= 'Positive', color= 'blue')
    ax[0][1].plot(industryData.Time, industryData.BuyQueueTickersPrc, label= 'Buy Queue', color= 'green')
    ax[0][1].plot(industryData.Time, industryData.SellQueueTickersPrc, label= 'Sell Queue', color= 'red')
    ax[0][1].legend(prop={'size': labelSize})

    heavyDealsValue = [industryData.HeavyBuysValue[i]-industryData.HeavySellsValue[i] for i in range(len(industryData.Time))]
    clrs = ['red' if (x < 0) else 'green' for x in heavyDealsValue]
    ax[1][0].bar(industryData.Time, heavyDealsValue, color= clrs, label= 'Smart Money', width= barWidth)
    # ax[1][0].plot(industryData.Time, [0 for _ in range(len(industryData.Time))], color= 'blue')
    ax[1][0].plot(industryData.Time, industryData.RealMoneyEntryValue, color= 'blue', label= 'Real Money')
    ax[1][0].legend(prop={'size': labelSize})

    realPowerDif = [log10(item) for item in industryData.RealPowerHamvaznDif]
    clrs = ['red' if (x < 0) else 'green' for x in realPowerDif]
    ax[1][1].bar(industryData.Time, realPowerDif, color= clrs, label= 'Real Power', width= barWidth)
    ax[1][1].plot(industryData.Time, [log10(1.5) for _ in range(len(industryData.Time))], color= 'blue')
    # ax[1][1].plot(industryData.Time, [0 for _ in range(len(industryData.Time))], color= 'blue')
    ax[1][1].plot(industryData.Time, [-log10(1.5) for _ in range(len(industryData.Time))], color= 'blue')
    ax[1][1].legend(prop={'size': labelSize})

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
            myFmt = mdates.DateFormatter("%H-%M")
            ax[i][j].xaxis.set_major_formatter(myFmt)
            ax[i][j].set_xlim([startLim, stopLim])
    fig.savefig('market.png', dpi= 350)
    plt.close()

    return msg'''

a = '''def create_general_telegram_message(self,groupName):
	industryData=self.manager.groups[groupName];index=industryData.LastPricePrcAverage[-1];trend='<b>صعودی🟢</b>'if self.manager.marketTrend.groupsData[groupName]['Trend']else'<b>نزولی🔴</b>';buyQueueTickersPrc=industryData.BuyQueueTickersPrc[-1];sellQueueTickersPrc=industryData.SellQueueTickersPrc[-1];realPowerKol=industryData.RealPowerKol[-1];realPowerKolDif=industryData.RealPowerKolDif[-1];realPowerHamvazn=industryData.RealPowerHamvazn[-1];realPowerHamvaznDif=industryData.RealPowerHamvaznDif[-1];realMoney=industryData.RealMoneyEntryValue[-1];heavyBuysValue=industryData.HeavyBuysValue[-1];heavySellsValue=industryData.HeavySellsValue[-1];heavyDealsValue=round(heavyBuysValue-heavySellsValue,1);heavyDealsPrc=industryData.HeavyDealsPrc[-1]
	if index>=0:indexStr='<b>'+str(index)+'+ </b>🟢'
	else:indexStr='<b>'+str(-index)+'- </b>🔴'
	buyQueueTickersPrcStr='<b>'+str(buyQueueTickersPrc)+'</b>';sellQueueTickersPrcStr='<b>'+str(sellQueueTickersPrc)+'</b>'
	if realPowerKol>=1:realPowerKolStr='<b>'+str(realPowerKol)+'+ </b>🟢'
	else:realPowerKolStr='<b>'+str(round(1/realPowerKol,2))+'- </b>🔴'
	if realPowerKolDif>=1:realPowerKolDifStr='<b>'+str(realPowerKolDif)+'+ </b>🟢'
	else:realPowerKolDifStr='<b>'+str(round(1/realPowerKolDif,2))+'- </b>🔴'
	if realPowerHamvazn>=1:realPowerHamvaznStr='<b>'+str(realPowerHamvazn)+'+ </b>🟢'
	else:realPowerHamvaznStr='<b>'+str(round(1/realPowerHamvazn,2))+'- </b>🔴'
	if realPowerHamvaznDif>=1:realPowerHamvaznDifStr='<b>'+str(realPowerHamvaznDif)+'+ </b>🟢'
	else:realPowerHamvaznDifStr='<b>'+str(round(1/realPowerHamvaznDif,2))+'- </b>🔴'
	if realMoney>=0:realMoneyStr='<b>'+str(realMoney)+'+ </b>🟢'
	else:realMoneyStr='<b>'+str(-realMoney)+'- </b>🔴'
	heavyBuysValueStr='<b>'+str(heavyBuysValue)+'</b>';heavySellsValueStr='<b>'+str(heavySellsValue)+'</b>'
	if heavyDealsValue>0:heavyDealsValueStr='<b>'+str(heavyDealsValue)+'+ </b>🟢'
	elif heavyDealsValue<0:heavyDealsValueStr='<b>'+str(-heavyDealsValue)+'- </b>🔴'
	else:heavyDealsValueStr='<b>0</b>'
	if heavyDealsPrc>0:heavyDealsPrcStr='<b> ( '+str(heavyDealsPrc)+'+ درصد 🟢 )</b>'
	elif heavyDealsPrc<0:heavyDealsPrcStr='<b> ( '+str(-heavyDealsPrc)+'- درصد 🔴 )</b>'
	else:heavyDealsPrcStr='<b> ( 0 درصد )</b>'
	msg='📈 #'+groupName+'\n\n'+'شاخص:  '+indexStr+'\n'+'ترند:  '+trend+'\n'+'درصد صف خرید:  '+buyQueueTickersPrcStr+'\n'+'درصد صف فروش:  '+sellQueueTickersPrcStr+'\n'+'قدرت خریدار کل:  '+realPowerKolStr+'\n'+'قدرت خریدار کل لحظه ای:  '+realPowerKolDifStr+'\n'+'قدرت خریدار هم وزن:  '+realPowerHamvaznStr+'\n'+'قدرت خریدار هم وزن لحظه ای:  '+realPowerHamvaznDifStr+'\n'+'پول حقیقی:  '+realMoneyStr+'\n'+'خرید درشت:  '+heavyBuysValueStr+'\n'+'فروش درشت:  '+heavySellsValueStr+'\n'+'برآیند معاملات بزرگ:  '+heavyDealsValueStr+heavyDealsPrcStr+'\n\n';fig,ax=plt.subplots(2,2);labelSize=6;period=60;barWidth=1e-05*period;ax[0][0].plot(industryData.Time,industryData.LastPricePrcAverage,label='Present Index');ax[0][0].plot(industryData.Time,industryData.TodayPricePrcAverage,label='Total Index');ax[0][0].legend(prop={'size':labelSize});ax[0][1].plot(industryData.Time,industryData.PositiveTickersPrc,label='Positive',color='blue');ax[0][1].plot(industryData.Time,industryData.BuyQueueTickersPrc,label='Buy Queue',color='green');ax[0][1].plot(industryData.Time,industryData.SellQueueTickersPrc,label='Sell Queue',color='red');ax[0][1].legend(prop={'size':labelSize});heavyDealsValue=[industryData.HeavyBuysValue[i]-industryData.HeavySellsValue[i]for i in range(len(industryData.Time))];clrs=['red'if x<0 else'green'for x in heavyDealsValue];ax[1][0].bar(industryData.Time,heavyDealsValue,color=clrs,label='Smart Money',width=barWidth);ax[1][0].plot(industryData.Time,industryData.RealMoneyEntryValue,color='blue',label='Real Money');ax[1][0].legend(prop={'size':labelSize});realPowerDif=[log10(item)for item in industryData.RealPowerHamvaznDif];clrs=['red'if x<0 else'green'for x in realPowerDif];ax[1][1].bar(industryData.Time,realPowerDif,color=clrs,label='Real Power',width=barWidth);ax[1][1].plot(industryData.Time,[log10(1.5)for _ in range(len(industryData.Time))],color='blue');ax[1][1].plot(industryData.Time,[-log10(1.5)for _ in range(len(industryData.Time))],color='blue');ax[1][1].legend(prop={'size':labelSize});today=datetime.datetime.now().date();startLim=datetime.datetime(today.year,today.month,today.day,9,0);stopLim=datetime.datetime(today.year,today.month,today.day,12,30)
	for i in range(2):
		for j in range(2):ax[i][j].grid(linestyle='--',linewidth=0.5);ax[i][j].spines['bottom'].set_color('white');ax[i][j].spines['top'].set_color('white');ax[i][j].spines['right'].set_color('white');ax[i][j].spines['left'].set_color('white');myFmt=mdates.DateFormatter('%H-%M');ax[i][j].xaxis.set_major_formatter(myFmt);ax[i][j].set_xlim([startLim,stopLim])
	fig.savefig('market.png',dpi=350);plt.close();return msg'''
print(len(a))