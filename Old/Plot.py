from math import log10
from Classes import Ticker, getTickers
from SqlServerDataBaseLib import DatabaseConnection
import matplotlib.pyplot as plt

Name = 'پترول'
FromDate = '1400-01-01'
ToDate = '1400-12-04'

TickerNames = [Name]
Tickers: dict[Ticker] = getTickers(TickerNames, FromDate, ToDate)

# RealPower
RealPower = [10*log10(Tickers[Name].RealPower[i]) for i in range(len(Tickers[Name].RealPower))]
RPVP = [RealPower[i] * Tickers[Name].Volume[i] for i in range(len(RealPower))]
OpenPricePRC = [(Tickers[Name].OpenPrice[i] - Tickers[Name].YesterdayPrice[i])/Tickers[Name].YesterdayPrice[i]*100 for i in range(len(Tickers[Name].OpenPrice))]


# AccumulativePRC
AccumulativePRC = []
status = True

for i in range(len(Tickers[Name].TodayPricePRC)): 
    if i == 0:
        status = Tickers[Name].TodayPricePRC[0] >= 0
        AcPer = 1 + Tickers[Name].TodayPricePRC[0]/100
        AccumulativePRC.append((AcPer - 1)* 100)
    else:
        if status == True and Tickers[Name].TodayPricePRC[i] >= -0.5 or status == False and Tickers[Name].TodayPricePRC[i] <= 0.5:
            AcPer *= (1 + Tickers[Name].TodayPricePRC[i]/100)
            AccumulativePRC.append((AcPer - 1)* 100)
        else:
            status = Tickers[Name].TodayPricePRC[i] >= 0
            AcPer = 1 + Tickers[Name].TodayPricePRC[i]/100
            AccumulativePRC.append((AcPer - 1)* 100)

# Scatter Colors
C = [0 for i in range(len(Tickers[Name].RealPower))]
for i in range(len(Tickers[Name].RealPower)):
    if Tickers[Name].RealPower[i] > 1.2 and Tickers[Name].TodayPricePRC[i] < 0:
        C[i] = 'lime'
    elif Tickers[Name].RealPower[i] > 1.3 and Tickers[Name].TodayPricePRC[i] >= -1:
        C[i] = 'green'
    elif i != 0 and Tickers[Name].RealPower[i]> 1.2 and Tickers[Name].RealPower[i-1] > 0:
        C[i] = 'green'
    elif Tickers[Name].RealPower[i] < 0.85 and Tickers[Name].TodayPricePRC[i] >= -1:
        C[i] = 'red'
    elif Tickers[Name].RealPower[i] < 0.85 and Tickers[Name].TodayPricePRC[i] < 1:
        C[i] = 'firebrick'
    else:
        C[i] = 'orange'


# # Resistance and Support calc
# PriceSMAday = 10
# PriceSMA = []

# for i in range(len(Tickers[Name].TodayPrice)):
#     if i < PriceSMAday-1:
#         PriceSMA.append(sum(Tickers[Name].TodayPrice[:i+1]) / (i+1))
#     else:
#         PriceSMA.append(sum(Tickers[Name].TodayPrice[i-PriceSMAday+1:i+1]) / PriceSMAday)

# Support = []
# Resistance = []

# if PriceSMA[PriceSMAday] > PriceSMA[PriceSMAday-1]: 
#     Rising = True
# else:
#     Rising = False


# for i in range(PriceSMAday+1, len(PriceSMA)):
#     if PriceSMA[i] > PriceSMA[i-1] and Rising == False:
#         Rising = True
#         sup = min(Tickers[Name].LowPrice[i-PriceSMAday:i])
#         Support.append(sup)
#         # indexes = [index for index, item in enumerate(Tickers[Name].LowPrice[i-PriceSMAday:i]) if item == sup]
#         print("Support")
#         print(Tickers[Name].Date[i-PriceSMAday+max(indexes)])
#     elif PriceSMA[i] < PriceSMA[i-1] and Rising == True:
#         Rising = False
#         res = max(Tickers[Name].HighPrice[i-PriceSMAday:i])
#         Resistance.append(res)
#         indexes = [index for index, item in enumerate(Tickers[Name].HighPrice[i-PriceSMAday:i]) if item == res]
#         print("Resistance")
#         print(Tickers[Name].Date[i-PriceSMAday+max(indexes)])

# print('Support:', Support)
# print('Resistance:', Resistance)

rowNum = 4
colNum = 1

fig, ax = plt.subplots(nrows=rowNum, ncols=colNum, sharex=True, figsize=(20,20), num= Name) # (width, height) in inches

ax[0].plot(Tickers[Name].Date, Tickers[Name].TodayPricePRC, color= 'blue')
ax[0].scatter(Tickers[Name].Date, RealPower, c= C, linewidths=0, s= 20)
ax[0].plot([0 for i in range(len(Tickers[Name].Date))], color= 'black')

ax[1].semilogy(Tickers[Name].Date, Tickers[Name].ClosePrice, color='black')

ax[2].plot([0 for i in range(len(AccumulativePRC))], color= 'green')
ax[2].bar(Tickers[Name].Date, Tickers[Name].Volume, color='black')
ax[2].bar(Tickers[Name].Date, [Tickers[Name].CorporateSellVolume[i] - Tickers[Name].CorporateBuyVolume[i] for i in range(len(Tickers[Name].Date))], color= 'red')


ax[3].plot([0 for i in range(len(RPVP))], color= 'black')
ax[3].bar(Tickers[Name].Date, RPVP, color='blue')

fig.tight_layout()
mng = plt.get_current_fig_manager()
mng.window.state('zoomed')

xline = [0 for i in range(rowNum)]
for i in range(rowNum):
    yMin, yMax = ax[i].get_ylim()
    xline[i], = ax[i].plot([min(Tickers[Name].Date), min(Tickers[Name].Date)],[yMin,yMax])

def on_click(event):
    # get the x and y pixel coords
    if event.inaxes:
        for i in range(rowNum):
            for j in range(colNum):
                xline[i].set_xdata(event.xdata)
        fig.canvas.draw()
        fig.canvas.flush_events()

fig.canvas.mpl_connect('button_press_event', on_click)

plt.show()



