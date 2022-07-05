import matplotlib.pyplot as plt
import pandas as pd
import matplotlib.dates as mpl_dates
from Infrastructure.Repository.DataBaseRepository import database_repo
from mplfinance.original_flavor import candlestick_ohlc
import mplfinance as mpf
import winsound
import numpy as np
import datetime


def isSupportSpace(df, i, space):
    for j in range(1, space):
        if not(df['Low'][i] <= df['Low'][i-j] and df['Low'][i] <= df['Low'][i+j]):
            return False
    return True

def isResistanceSpace(df, i, space):
    for j in range(1, space):
        if not(df['High'][i] >= df['High'][i-j] and df['High'][i] >= df['High'][i+j]):
            return False
    return True

def isSupporSide(df, i, space1, space2):

    right = 0
    left = 0

    for j in range(1, space1+1):
        if df['Low'][i] <= df['Low'][i-j]:
            left += 1
        else:
            break

    for j in range(1, space1+1):
        if df['Low'][i] <= df['Low'][i+j]:
            right += 1
        else:
            break

    if max(right, left) >= space1 and min(right, left) >= space2:
        return True
    else:
        return False

def isResistanceSide(df, i, space1, space2):

    right = 0
    left = 0

    for j in range(1, space1+1):
        if df['High'][i] >= df['High'][i-j]:
            left += 1
        else:
            break

    for j in range(1, space1+1):
        if df['High'][i] >= df['High'][i+j]:
            right += 1
        else:
            break

    if max(right, left) >= space1 and min(right, left) >= space2:
        return True
    else:
        return False

def strDate_to_lineDates(strDate: str, price: int):

    thisDate = datetime.datetime.strptime(strDate, "%Y-%m-%d")
    delta = datetime. timedelta(days=6)
    thisDateNeg = (thisDate - delta).strftime("%Y-%m-%d")
    thisDatePos = (thisDate + delta).strftime("%Y-%m-%d")
    return [(thisDateNeg, price), (thisDatePos, price)]

def isFarFromLevel(l):
  return np.sum([abs(l-x) < s  for x in levels]) == 0
  
db = database_repo()
db.connect()

# read
data = db.read_offline_by_farsiTicker_and_date('Date', 'HighPrice', 'LowPrice', 'OpenPrice', 'ClosePrice', 'Volume',\
farsiTicker= 'فارس', fromDate= '1399-03-01')

# data to pd
prices = {'Date': data['Date'], 'High': data['HighPrice'], 'Low': data['LowPrice'], 'Open': data['OpenPrice'], 'Close': data['ClosePrice'], 'Volume': data['Volume']}
dataPd = pd.DataFrame(prices) 
dataPd.index = pd.DatetimeIndex(dataPd['Date'])

s =  np.mean(dataPd['High'] - dataPd['Low'])

levels = []
lines = []
space1 = 21
space2 = 4

for i in range(space1, dataPd.shape[0]-space1):
    if isSupporSide(dataPd, i, space1, space2):
        l = dataPd['Low'][i]
        # if isFarFromLevel(l):
        levels.append(int(l))
        lines.append(strDate_to_lineDates(dataPd['Date'][i],int(l)))

    elif isResistanceSide(dataPd, i, space1, space2):
        l = dataPd['High'][i]

        # if isFarFromLevel(l):
        levels.append(int(l))
        lines.append(strDate_to_lineDates(dataPd['Date'][i], int(l)))

# plot
fig, axlist = mpf.plot(dataPd, type='candle', style='charles', volume=True, tight_layout= True, alines=lines)
ax = axlist[0]
ax.set_yscale('log')
#  hlines=dict(hlines=levels), , alines=two_points,
winsound.Beep(500, 200)
