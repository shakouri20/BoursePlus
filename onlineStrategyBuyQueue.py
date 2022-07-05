from Domain.Enums.OnlineColumns import onlineColumns
from Domain.Enums.TableType import tableType
from Infrastructure.Repository.OfflineDataRepository import offlineData_repo
from Infrastructure.Repository.OnlineDataRepository import onlineData_repo
from Application.Services.ReadData.ReadOffline.ReadOfflineServices import read_offline_services
from Application.Services.ReadData.ReadOnline.OnlineDataHandler import onlineDataHandler
from Application.Utility.DateConverter import *
from Infrastructure.Repository.TickerRepository import ticker_repo
from Application.Services.DataProcess import get_data_from_web
from datetime import datetime
import winsound
from tkinter import *
from tkinter import ttk

# Create an instance of tkinter frame
win = Tk()

# Set the size of the tkinter window
win.geometry("1700x1350")
s = ttk.Style()
s.theme_use('clam')
s.configure("Treeview",
	background="#D3D3D3",
	foreground="black",
	rowheight=25,
	fieldbackground="#D3D3D3")

# Add a Treeview widget
tree = ttk.Treeview(win, column=("c1", "c2", "c3", "c4", "c5", "c6", "c7"), show='headings', height=100)
tree.column("# 1", anchor=CENTER)
tree.column("# 2", anchor=CENTER)
tree.column("# 3", anchor=CENTER)
tree.column("# 4", anchor=CENTER)
tree.column("# 5", anchor=CENTER)
tree.column("# 6", anchor=CENTER)
tree.column("# 7", anchor=CENTER)
tree.heading("# 1", text="Signal Type")
tree.heading("# 2", text="Ticker")
tree.heading("# 3", text="Buy Percapita")
tree.heading("# 4", text="Sell Percapita")
tree.heading("# 5", text="Real Power")
tree.heading("# 6", text="Price Change")
tree.heading("# 7", text="Volume Ratio")

IDs = ticker_repo().read_list_of_tickers(tickerTypes= [1])["ID"]

cache = onlineDataHandler(IDs)

def action():

    winsound.Beep(500, 200)
    tree.delete(*tree.get_children())

    while True:
        try:
            (onlineDataList, cacheDataDict) = get_data_from_web()
            break
        except:
            continue

    if cacheDataDict == None:
        print('None')

    else:

        cache.update(cacheDataDict)

        print(datetime.now())

        # run strategy
        lastPrice = cache.lastPrice(num= 10)
        maxAllowedPrice = cache.maxAllowedPrice()
        lastPricePrc5 = cache.lastPricePRC(decNum= 20, num= 2)
        volumeDif = cache.volumeDif(num=1, decNum= 5)
        volume = cache.volume(num=1)
        buyPerCapita = cache.perCapitaBuy(num= 1)
        sellPerCapita = cache.perCapitaSell(num= 1)
        realPower = cache.realPower(num= 1)

        availableIDs = list(lastPrice.keys())

        signaledData = []

        def single_ticker_calc(ID):

            priceDif5 = round(lastPricePrc5[ID][-1]-lastPricePrc5[ID][0], 1)
            volumeRatio = round(volumeDif[ID][-1]/volume[ID][-1], 2)

            if lastPrice[ID][0] == maxAllowedPrice[ID]:

                numberOfBuyQueueTimes = 0
                for price in lastPrice[ID]:
                    if price == maxAllowedPrice[ID]:
                        numberOfBuyQueueTimes += 1

                if numberOfBuyQueueTimes < 5:

                    signaledData.append(('BQ...', str(ticker_repo().read_by_ID(ID)['FarsiTicker']),
                        buyPerCapita[ID][0], sellPerCapita[ID][0], round(realPower[ID][0], 2), priceDif5, volumeRatio))

        
            if buyPerCapita[ID][0] > 30 and lastPrice[ID][0] != maxAllowedPrice[ID]:
                signaledData.append(('Good Condition but not BQ', str(ticker_repo().read_by_ID(ID)['FarsiTicker']),
                    buyPerCapita[ID][0], sellPerCapita[ID][0], round(realPower[ID][0], 2), priceDif5, volumeRatio))


        for ID in availableIDs:
            try:
                single_ticker_calc(ID)
            except:
                print('Error')

    signaledData.sort(key=lambda tup: tup[2], reverse=True)

    for tickerData in signaledData:
        tree.insert('', 'end', text="1", values=tickerData)
    
    win.after(15000, action) 

tree.pack()

win.after(15000, action)

win.mainloop()