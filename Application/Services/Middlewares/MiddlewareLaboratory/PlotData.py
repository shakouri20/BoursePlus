# from Application.Services.Middlewares.MiddlewareLaboratory.MiddlewareTest import plotData
from Infrastructure.Repository.TickerRepository import ticker_repo
from Old.DateConverter import jalali_to_gregorian
from Old.SqlServerDataBaseLib import *
import os
import matplotlib.pyplot as plt
from math import log10
from datetime import datetime, timedelta


def plot_daily(tickerId, time, **kargs):
    tr = ticker_repo()
    ID = tickerId

    Name = tr.read_by_ID(ID)['FarsiTicker']


    rowNum = len(kargs.keys())
    colNum = 1

    fig, ax = plt.subplots(rowNum-1, colNum, sharex=True, figsize=(20,20), num= Name) # (width, height) in inchese)

    counter = 0
    for item in kargs:
        if counter != rowNum-1:
            ax[counter].set_ylabel(item)
            if item == 'Price':
                ax[counter].plot(time.data, kargs[item].data)#, color='green')
            else:
                ax[counter].bar(time.data, kargs[item].data)#, color='green')
            if kargs[item].constLine is not None:
                ax[counter].axhline(y= kargs[item].constLine, color='r')
            if kargs[item].min is not None:
                mini = kargs[item].min
                maxi = kargs[item].max
                ax[counter].set_ylim(mini, maxi)
            counter += 1


    fig.tight_layout()
    mng = plt.get_current_fig_manager()
    mng.window.state('zoomed')

    xline = [[0 for i in range(colNum)] for j in range(rowNum-1)]
    for i in range(rowNum-1):
        for j in range(colNum):
            yMin, yMax = ax[i].get_ylim()
            xline[i], = ax[i].plot([min(time.data), min(time.data)],[yMin,yMax])

    def on_click(event):
        # get the x and y pixel coords
        if event.inaxes:
            for i in range(rowNum-1):
                for j in range(colNum):
                    xline[i].set_xdata(event.xdata)
            fig.canvas.draw()
            fig.canvas.flush_events()

    fig.canvas.mpl_connect('button_press_event', on_click)

    plt.show()

