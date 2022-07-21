from math import log10
from Application.Services.ReadData.ReadOnline.MarketWatchDataGenerator import marketWatchDataGenerator
from Application.Services.ReadData.ReadOnline.MarketWatchDataHandler import marketWatchDataHandler
from Application.Utility.DateConverter import jalali_to_gregorian
from Application.Utility.Indicators.IndicatorService import calculateSma
from Domain.ImportEnums import *
from Infrastructure.Repository.OnlineDataRepository import onlineData_repo
import matplotlib.pyplot as plt
import datetime

date = '1400-06-14'
decNum = 5
period = 15
maLength = int(100/decNum*15/period)
length = int(30/decNum*15/period)

groups = [marketGroupType.TotalMarket.value] #, marketGroupType.Khodroei, marketGroupType.Daroei

distinctTimes = onlineData_repo().read_distinct_times_of_day(jalali_to_gregorian(date))
marketWatchGen = marketWatchDataGenerator()
marketWatchHand = marketWatchDataHandler(groups, None)
risingMode = False
db = onlineData_repo()
t1 = datetime.datetime.now()    

for thisTime in distinctTimes[12::decNum]:

    print('', thisTime, end= '\r')

    data = db.read_onlineData_by_every_time(thisTime)

    marketWatchData = marketWatchGen.get_marketWatchInfo(data)

    marketWatchHand.update(marketWatchData)

t2 = datetime.datetime.now()    
print('\n', t2-t1)

for group in groups:

    rowNum = 7
    colNum = 2

    time = marketWatchHand.time()[group]
    positiveTickersPRC = marketWatchHand.positiveTickersPRC()[group]
    totalValue = marketWatchHand.totalValue()[group]
    buyQueueTickersPRC = marketWatchHand.buyQueueTickersPRC()[group]
    sellQueueTickersPRC = marketWatchHand.sellQueueTickersPRC()[group]
    lastPricePRCAverge = marketWatchHand.lastPricePRCAverge()[group]
    lastPricePRCAvergeMA = marketWatchHand.lastPricePRCAverge_MA(maLength= maLength)[group]
    todayPricePRCAverage = marketWatchHand.todayPricePRCAverage()[group]
    buyQueuesValue = marketWatchHand.buyQueuesValue()[group]
    sellQueuesValue = marketWatchHand.sellQueuesValue()[group]
    # demandValue = marketWatchHand.demandValue()[group]
    # supplyValue = marketWatchHand.supplyValue()[group]
    realPowerLog = marketWatchHand.realPowerLog()[group]
    tickersNumber = marketWatchHand.tickersNumber()[group]
    realPower = marketWatchHand.realPower()[group]
    totalValueDif = marketWatchHand.totalValueDif(length= length)[group]
    lastPricePRCAverge_MA_dif = marketWatchHand.lastPricePRCAverge_MA_dif(maLength= maLength)[group]
    realPowerDif = marketWatchHand.realPowerDif(length = length)[group]
    rpvp = [log10(realPowerDif[i])*totalValueDif[i] for i in range(len(realPowerDif))]

    # SellQueuPRC ma
    SQPMA = calculateSma(sellQueueTickersPRC, int(60*15/period), True)

    # rising and falling recognition
    #method1
    # xmax = -100
    # xmin = 100
    # mxmax = -100
    # mxmin = 100
    # tradedTimes = []
    # xmin = min(lastPricePRCAverge)
    # for i in range(len(lastPricePRCAverge)):
    #     xmax = max(xmax, lastPricePRCAverge[i])
    #     mxmax = max(lastPricePRCAverge[max(i-int(25/decNum*15/period), 0):i+1])
    #     mxmin = min(lastPricePRCAverge[max(i-int(25/decNum*15/period), 0):i+1])

    #     if lastPricePRCAverge[i] >= mxmin + 1 and lastPricePRCAverge[i] >= mxmax - 1: # and lastPricePRCAverge[i] >= xmax -15
    #         tradedTimes.append(lastPricePRCAverge[i])
    #     else:
    #         tradedTimes.append(xmin-5)

    # indexSlope
    indexSlope = [0 for i in range(len(lastPricePRCAverge))]
    for i in range(1, len(lastPricePRCAverge)):
        indexSlope[i] = lastPricePRCAverge[i] - lastPricePRCAverge[max(i-int(10/decNum*15/period), 0)] # 20
        indexSlope[i] /= ((time[i]-time[max(i-int(10/decNum*15/period), 0)]).total_seconds()/60)

    xmin = min(lastPricePRCAverge)
    tradedTimes = [xmin-2 for i in range(len(lastPricePRCAverge))]
    tradeFlag = False
    for i in range(1, len(lastPricePRCAverge)):
        if indexSlope[i] >= 0.2:
            tradeFlag = True
        if indexSlope[i] < 0:
            tradeFlag = False
        if tradeFlag == True:
            tradedTimes[i] = lastPricePRCAverge[i]
    
    # SQP Slope
    sqpSlope = [0 for i in range(len(sellQueueTickersPRC))]
    for i in range(1, len(sellQueueTickersPRC)):
        sqpSlope[i] = sellQueueTickersPRC[i] - sellQueueTickersPRC[max(i-int(20/decNum*15/period), 0)]
        sqpSlope[i] /= ((time[i]-time[max(i-int(20/decNum*15/period), 0)]).total_seconds()/60)

    xmin = min(sellQueueTickersPRC)
    sqpTradesTimes = [xmin-0.5 for i in range(len(sellQueueTickersPRC))]
    tradeFlag = False
    for i in range(1, len(sellQueueTickersPRC)):
        if sqpSlope[i] <= -0.05:
            tradeFlag = True
        if sqpSlope[i] > 0:
            tradeFlag = False
        if tradeFlag == True:
            sqpTradesTimes[i] = sellQueueTickersPRC[i]

    fig, ax = plt.subplots(nrows=rowNum, ncols=colNum, sharex=True, figsize=(18,18), num= str(group) + date) # (width, height) in inches

    ax[0][0].plot(time, positiveTickersPRC, 'blue', label= 'PositiveTickersPRC')
    ax[0][0].legend()
    ax[0][1].plot(time, totalValue, 'blue', label= 'TotalValue')
    ax[0][1].legend()
    ax[1][0].plot(time, buyQueueTickersPRC, 'blue', label= 'BuyQueueTickersPRC')
    ax[1][0].legend()
    ax[1][1].plot(time, sellQueueTickersPRC, 'blue', label= 'SellQueueTickersPRC')
    ax[1][1].plot(time, sqpTradesTimes, 'red')
    ax[1][1].plot(time, SQPMA, 'black')
    ax[1][1].legend()
    ax[2][0].plot(time, lastPricePRCAverge, 'blue', label= 'LastPricePRCAverge')
    ax[2][0].plot(time, tradedTimes, 'red', label= 'tradedTimes')
    ax[2][0].plot(time, lastPricePRCAvergeMA, 'green', label= 'LastPricePRCAvergeMA')
    # ax[2][0].legend()
    ax[2][1].plot(time, todayPricePRCAverage, 'blue', label= 'TodayPricePRCAverage')
    ax[2][1].legend()
    ax[3][0].plot(time, indexSlope, 'blue', label= 'indexSlope')
    ax[3][0].plot(time, [0 for i in range(len(time))], 'black')
    ax[3][0].legend()
    ax[3][1].plot(time, sellQueuesValue, 'red', label= 'SellQueuesValue')
    ax[3][1].legend()
    ax[4][0].plot(time, realPowerLog, 'blue', label= 'RealPowerLog')
    ax[4][0].plot(time, [1 for i in range(len(time))], 'black')
    ax[4][0].legend()
    ax[4][1].plot(time, buyQueuesValue, 'blue', label= 'BuyQueuesValue')
    ax[4][1].legend()
    ax[5][0].plot(time, realPower, 'blue', label= 'Realpower')
    ax[5][0].plot(time, [1 for i in range(len(time))], 'black')
    ax[5][0].legend()
    ax[5][1].plot(time, totalValueDif, label= 'TotalValueDif')
    ax[5][1].legend()
    ax[6][0].plot(time, lastPricePRCAverge_MA_dif, 'blue', label= 'LastPricePRCAvergeMADif')
    ax[6][0].plot(time, [0 for i in range(len(time))], 'black')
    # ax[6][0].plot(time, [1 for i in range(len(time))], 'green')
    ax[6][0].plot(time, [-1.5 for i in range(len(time))], 'red')
    ax[6][0].legend()
    ax[6][1].plot(time, realPowerDif, label= 'RealpowerDif')
    ax[6][1].plot(time, [1 for i in range(len(time))], 'black')
    ax[6][1].legend()
    # ax[8][0].plot(time, lastPricePRCAverge_MA_dif, label= 'lastPricePRCAverge_MA_dif')
    # ax[8][0].plot(time, [1 for i in range(len(time))], 'black')
    # ax[8][0].legend()
    # ax[8][1].plot(time, realPowerDif1, label= 'RealpowerDif1')
    # ax[8][1].plot(time, [1 for i in range(len(time))], 'black')
    # ax[8][1].legend()


    fig.tight_layout()

    mng = plt.get_current_fig_manager()
    mng.window.state('zoomed')

xline = [[0 for i in range(colNum)] for j in range(rowNum)]

for i in range(rowNum):
    for j in range(colNum):
        yMin, yMax  = ax[i][j].get_ylim()
        xline[i][j], = ax[i][j].plot([min(time), min(time)],[yMin,yMax])

def on_click(event):
    # get the x and y pixel coords
    if event.inaxes:
        for i in range(rowNum):
            for j in range(colNum):
                xline[i][j].set_xdata(event.xdata)
        fig.canvas.draw()
        fig.canvas.flush_events()

fig.canvas.mpl_connect('button_press_event', on_click)

plt.show()

