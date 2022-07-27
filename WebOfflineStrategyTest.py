from Application.Services.OfflineLab.OfflineLab import offlineLab
from Infrastructure.Repository.TickerRepository import ticker_repo
from Application.Services.OfflineLab.M_BuyMiddlewares import *
from Application.Services.OfflineLab.M_SellMiddlewares import *
from Application.Services.OfflineLab.D_BuyMiddlewares import *
from Application.Services.OfflineLab.D_SellMiddlewares import *

name = 'خفنر'
fromDate = '1400-10-01'
toDate= '1401-12-30'

IDs = [ticker_repo().read_by_name(name)['ID']]
# IDs = ticker_repo().read_list_of_tickers(tickerTypes= [1], marketTypes=[1, 2, 3, 4 , 5, 6])['ID'][::6]
lab = offlineLab(IDs)

lab.read_data(fromDate= fromDate, toDate= toDate, timeFrame= '1D', pastDataNumber= 30,
                    getPriceRange= False, getOrdersBoard= False, getTickersGroupData= False)
# lab.print_ichimoko_data()
lab.plot_offline_data()

buyMiddlewares = []
sellMiddlewares = []

buyMiddlewares.append((m_buyMiddlewares.positiveRange2(IDs), 1))   
# buyMiddlewares.append((m_buyMiddlewares.realPowerCheck(IDs), 1))   
# buyMiddlewares.append((m_buyMiddlewares.tenkansenCross2(IDs), 1))   
# sellMiddlewares.append((m_sellMiddlewares.tenkansenCross2(IDs), 1))   
sellMiddlewares.append((m_sellMiddlewares.takeProfit(IDs, 2), 1))
sellMiddlewares.append((m_sellMiddlewares.stopLoss(IDs, 8, 0, 3, sellByClosePrice= True), 1))
# sellMiddlewares.append((m_sellMiddlewares.trailingStopLoss(IDs, 5), 1))
# sellMiddlewares.append((m_sellMiddlewares.realPowerCheck(IDs), 1))
# lab.strategy_backTest(buyMiddlewares, sellMiddlewares, 80, 80, 5)


# lab.plot_chart(decNum= 1, plotvlines= False)