from matplotlib import pyplot as plt
import pandas as pd
from Application.Services.ReadData.ReadOffline.RatioService import tickerCompare
from Application.Utility.DateConverter import *
from Infrastructure.Repository.TickerRepository import ticker_repo
import mplfinance as mpf


fromDate = '1400-01-01'
toDate = '1402-01-01'

ticker = 'خگستر'

tickersData = tickerCompare(ticker_repo().read_by_name(ticker)['ID'], 67130298613737946, fromDate, toDate)

lines = {}
trend = 'up'

for i in range(len(tickersData.datesG)):

    if len(lines) == 0:
        if tickersData.ratio[i] > tickersData.ratioMa1[i]:
            lines[tickersData.datesG[i]] = 'green'
            trend = 'up'
        if tickersData.ratio[i] < tickersData.ratioMa1[i]:
            lines[tickersData.datesG[i]] = 'red'
            trend = 'down'

    if tickersData.ratio[i] > tickersData.ratioMa1[i] and trend == 'down':
        lines[tickersData.datesG[i]] = 'green'
        trend = 'up'

    if tickersData.ratio[i] < tickersData.ratioMa1[i] and trend == 'up':
        lines[tickersData.datesG[i]] = 'red'
        trend = 'down'

prices = {'Date': tickersData.datesG, 'High': tickersData.tickerHighPrice1, 'Low': tickersData.tickerLowPrice1, 'Open': tickersData.tickerOpenPrice1, 'Close': tickersData.tickerClosePrice1}
dataPd = pd.DataFrame(prices) 
dataPd.index = pd.DatetimeIndex(dataPd['Date'])
        
custom_rc = {'font.size': 8, 'figure.titlesize': 'x-large', 'figure.titleweight': 'normal'}
s =mpf.make_mpf_style(base_mpf_style='charles', rc=custom_rc) #
    
fig, axlist = mpf.plot(dataPd, axisoff = True, type='candle', tight_layout= True, returnfig=True, style=s, 
    vlines= dict(vlines=list(lines.keys()), colors= [lines[day] for day in lines], linewidths= [0.4 for i in range(len(lines))])) # , mav= (30)

plt.show()
x = 1