from math import log10, nan
import datetime
import pandas as pd
from Application.Services.ReadData.ReadOffline.RatioService import tickerCompare
from Application.Utility.DateConverter import *
from Application.Utility.AdvancedPlot import advancedPlot
import mplfinance as mpf
from Application.Utility.Indicators.IndicatorService import calculateIchimoko, calculateSma
from Domain.Enums.TableType import tableType
from Infrastructure.DbContext.DbSession import database_session
from Infrastructure.Repository.OfflineDataRepository import offlineData_repo
from Infrastructure.Repository.TickerRepository import ticker_repo

fromDate = '1400-09-01'
toDate = '1402-01-01'

ticker1 = 67130298613737946
ticker2 = 32097828799138957
ticker2 = 'شاخص کل (هم وزن)6'

ticker1 = '27-فلزات اساسي6'
ticker1 = '23-فراورده نفتي6'
ticker1 = '34-خودرو6'
ticker1 = '57-بانکها6'
ticker1 = '44-شيميايي6'
ticker1 = '53-سيمان6'
ticker1 = '01-زراعت6'
ticker1 = '42-غذايي بجز قند6'
ticker1 = '60-حمل و نقل6'
ticker1 = '38-قند و شکر6'
ticker1 = '25-لاستيک6'
ticker1 = '70-انبوه سازي6'
ticker1 = '43-مواد دارويي6'
ticker1 = '56-سرمايه گذاريها6'
ticker1 = '40-تامين آب،برق،گ6'
ticker1 = '72-رايانه6'
ticker1 = '49-کاشي و سراميک6'
ticker1 = '67-اداره بازارمال6'

ticker1 = '67-اداره بازارمال6'
ticker2 = 'شاخص کل (هم وزن)6'

tickersData = tickerCompare(ticker1, ticker2, fromDate, toDate)

# plot
ap = advancedPlot(2, 2, ticker2+'    '+ticker1)


custom_rc = {'font.size': 8, 'figure.titlesize': 'x-large', 'figure.titleweight': 'normal'}
s =mpf.make_mpf_style(base_mpf_style='charles', rc=custom_rc) #

prices = {'Date': [datetime.datetime.strptime(time, "%Y-%m-%d") for time in tickersData.datesG], 'High': tickersData.tickerHighPrice1, 'Low': tickersData.tickerLowPrice1, 'Open': tickersData.tickerOpenPrice1, 'Close': tickersData.tickerClosePrice1}
dataPd = pd.DataFrame(prices)
dataPd.index = pd.DatetimeIndex(dataPd['Date'])
mpf.plot(dataPd, ax= ap.ax[0][0], axisoff = True, type= 'candle', tight_layout= True, returnfig= False, style=s, ylabel= ticker1[::-1] if type(ticker1) == str else '')
ap.ax[0][0].yaxis.tick_left()
# ap.ax[0][0].yaxis.set_label_position("left")
ap.ax[0][0].set_yscale('log')
ap.ax[0][0].tick_params(labelleft= False)


prices = {'Date': [datetime.datetime.strptime(time, "%Y-%m-%d") for time in tickersData.datesG], 'High': tickersData.tickerHighPrice2, 'Low': tickersData.tickerLowPrice2, 'Open': tickersData.tickerOpenPrice2, 'Close': tickersData.tickerClosePrice2}
dataPd = pd.DataFrame(prices)
dataPd.index = pd.DatetimeIndex(dataPd['Date'])
mpf.plot(dataPd, ax= ap.ax[0][1], axisoff = True, type= 'candle', tight_layout= True, returnfig= False, style=s, ylabel= ticker2[::-1] if type(ticker2) == str else '')
ap.ax[0][1].yaxis.tick_left()
# ap.ax[0][1].yaxis.set_label_position("left")
ap.ax[0][1].set_yscale('log')
ap.ax[0][1].tick_params(labelleft= False)


ap.ax[1][0].plot(tickersData.datesJ, tickersData.ratio, color= 'blue')
ap.ax[1][0].plot(tickersData.datesJ, tickersData.ratioMa1, color= 'red', linewidth= 0.7)
ap.ax[1][0].plot(tickersData.datesJ, tickersData.ratioMa2, color= 'green', linewidth= 0.7)
ap.ax[1][0].set_ylabel('Ratio')
ap.ax[1][0].tick_params(labelleft= False)

ap.ax[1][1].plot(tickersData.datesJ, tickersData.ratioRsi, color= 'blue')
ap.ax[1][1].plot(tickersData.datesJ, [30 for _ in range(len(tickersData.datesJ))], color='black', linewidth= 0.6)
ap.ax[1][1].plot(tickersData.datesJ, [50 for _ in range(len(tickersData.datesJ))], color='brown', linewidth= 1.5)
ap.ax[1][1].plot(tickersData.datesJ, [70 for _ in range(len(tickersData.datesJ))], color='black', linewidth= 0.6)
# clrs = ['red' if (x < 50) else 'green' for x in tickersData.ratioMacd]
# ap.ax[1][1].bar(tickersData.datesJ, tickersData.ratioMacd, color= clrs)
ap.ax[1][1].plot(tickersData.datesJ, tickersData.ratioMacd, color= 'green')
ap.ax[1][1].plot(tickersData.datesJ, tickersData.ratioMacdMa, color= 'c')
ap.ax[1][1].set_ylabel('Indicator')
ap.ax[1][1].tick_params(labelleft= False)

ap.run()