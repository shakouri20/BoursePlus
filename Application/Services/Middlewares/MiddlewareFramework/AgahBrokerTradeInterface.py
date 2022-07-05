from datetime import datetime
from Infrastructure.Repository.TickerRepository import ticker_repo
from Domain.ImportEnums import *
from Settings import SettingsService
import threading
import requests
import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains

workFlag = threading.Lock()
defaultTimeOut = SettingsService.realTime.get_agah_api_default_timeOut() # for Api requests
monitorPeriod = SettingsService.realTime.get_monitor_chrome_period()

class onlineBroker():
    def __init__(self) -> None:
        pass

    def get_account_balance(self)-> int:
        raise NotImplementedError()

    def get_customer_instrument_count(self, Isin)->int:
        raise NotImplementedError()

    def get_portfolio(self):
        raise NotImplementedError()

    def execute_order(self, _orderType:orderType, tickerId, price, quantity):
        raise NotImplementedError()

class agahUrls():
    pingUrl = r'https://push12.agah.ir/asa/ping'
    getQuickBalanceDataUrl = r'https://online.agah.com/BankAccount/GetQuickBankAccountData'
    getInstrumentInfoUrl = r'https://online.agah.com/Watch/GetInstrumentInfo?isin={}'
    getCustomerInstrumentAssetUrl = r'https://online.agah.com/Account/GetCustomerInstrumentAsset?customerId={}&instrumentId={}'
    getPortfolioUrl = r'https://online.agah.com/Portfolio/GetMyPortfolios?CalculateByTotalNumberOfShare=true&HideZeroAsset=true&IsLastPrice=true&filter={}&limit=25&page=1&sort={"CalculatedTodayCost":"desc"}'
    getTodayErrorOrdersUrl = r'https://online.agah.com/Order/GetTodayErrorOrders?filter=%7B%7D&limit=25&page=1&sort=%7B%7D'
    getTodayOrdersListUrl = r'https://online.agah.com/Order/GetOrderList?decisionReportMode=2&filter={}&limit=100&page=1&sort={"ResponseTime":"desc"}'
    getWeekOrdersListUrl = r'https://online.agah.com/Order/GetOrderList?decisionReportMode=3&filter={}&limit=100&page=1&sort={"ResponseTime":"desc"}'

class agahOrderDetail():
    def __init__(self) -> None:
        self.name = None
        self.state = None
        self.status = None
        self.responseTime = None
        self. orderSide = None
        self.tradedQuantity = None
        self.price = None

    def __str__(self) -> str:
        text = self.name[::-1] + '\n'
        text += str(self.tradedQuantity) + '\n'
        text += str(self.orderSide) + '\n'
        text += str(self.status) + '\n'
        text += str(self.state) + '\n'
        text += str(self.responseTime)
        return text

class agahOrders():
    def __init__(self) -> None:
        self.activeBuyOrders:list[agahOrderDetail] = [] # Active buy order -> order sent but not traded
        self.activeSellOrders:list[agahOrderDetail]  = [] # Active sell order -> order sent but not traded
        self.partialSuccessBuyOrders:list[agahOrderDetail]  = [] # Active buy with partial success
        self.partialSuccessSellOrders:list[agahOrderDetail]  = [] # Active sell with partial sucsess
        self.openOrders:list[agahOrderDetail]  = [] # These Tickers have been bought success or partial and deactivated but not sold completely yet
        self.closedOrders:list[agahOrderDetail]  = [] # These tickers have been bought and sold => Finished

class agahBrokerTradeInterface(onlineBroker):
    '''This class provides an interface to work with Agah broker trading system named "AsaOnline".\n
         It also provides sending buy and sell functions and receiving portfoilo information from
         online platform. It uses selenium and requests at its core.'''

    def __init__(self) -> None:
        self.tickers = ticker_repo().read_list_of_tickers(IPO= 2, outPutType= queryOutPutType.DictDict)

        self.wait = None
        self.cookies = None
        self.driver = None
        self.start_chrome_browser()
        try:
            self.close_frames()
            self.switch_to_watchlist('MyWatch')
        except:
            print('Warning!! Exception at close_frames & switch_to_watchlist.')
        # self.wait = WebDriverWait(self.driver, 2)

        self.cookies = self.get_cookies()
        self.hadError = False
        threading.Thread(target=self.monitor_chrome).start()
        
        super(agahBrokerTradeInterface, self).__init__()

    def get_ticker(self, id)-> dict:
        '''Returns the Isin and Farsi name for provided ticker id. Returns None of not available in database.'''

        ticker = self.tickers[id]
        if ticker is None:
            return None
        return {
            'isin' : ticker['IR1'],
            'name' : ticker['FarsiTicker']
        }

    # =============================<< Browser-Based Operations >>============================= #
    def start_chrome_browser(self):
        # with workFlag:
        myOptions = webdriver.ChromeOptions()
        myOptions.add_argument('log-level=3')
        myOptions.add_argument("--ignore-ssl-errors")
        # myOptions.add_argument('--headless')
        # myOptions.add_argument('--disable-gpu') 
        # myOptions.add_argument('--no-proxy-server')
        self.driver = webdriver.Chrome(chrome_options= myOptions)

        url = r'https://online.agah.com'
        self.driver.get(url)

        if self.cookies is not None:
            # self.driver.execute_cdp_cmd('Network.enable', {})
            for cookie in self.cookies:
                self.driver.add_cookie({'name': cookie , 'value': self.cookies[cookie]})
                # self.driver.execute_cdp_cmd('Network.setCookie', cookie)
            # self.driver.execute_cdp_cmd('Network.disable', {})
            self.driver.get(url)
        else:
            time.sleep(30)
        
        self.wait = WebDriverWait(self.driver, 1)

    def refresh_page(self):
        with workFlag:
            url = r'https://online.agah.com'
            self.driver.get(url)
            time.sleep(0.1)
            self.close_frames()
            self.switch_to_watchlist('MyWatch')

    def get_cookies(self):
        self.driver.get_cookies()
        cookieDict = {}
        cookies = self.driver.get_cookies()
        for cookie in cookies:
            key = cookie['name']
            value = cookie['value']
            cookieDict[key] = value
        return cookieDict

    def close_frames(self):
        frames:list[WebElement] = self.driver.find_elements_by_xpath('//div[@class="modalHeader ui-draggable-handle"]/i[@class="windowCloseBtn"]')
        for frame in frames:
            frame.click()

    def engage_broker(self):
        with workFlag:
            self.close_frames()
            GetAccountDiv:WebElement = self.driver.find_element_by_xpath('//div[@class="stock ng-scope"]')
            GetAccountDiv.click()
            time.sleep(0.1)
            GetAccountDiv.click()
    
    def switch_to_watchlist(self, watchlistName):
        watchList: WebElement = self.driver.find_element_by_xpath('//div[@class="watching-list ng-scope"]')
        hover = ActionChains(self.driver).move_to_element(watchList)
        hover.perform()
        time.sleep(0.05)
        watchLists: list[WebElement] = self.driver.find_elements_by_xpath('//span[@class="content ng-binding"]')
        for watch in watchLists:
            title = watch.text
            if title == watchlistName:
                watch.click()
                break
        time.sleep(0.05)
        
    def monitor_chrome(self):
        while True:
            try:
                if self.hadError:
                    raise Exception('Had Error Exception!!')
                self.engage_broker()
                self.is_server_responding()
                self.cookies = self.get_cookies()
            except Exception as e :
                print('Warning!! Exception at engage_broker.===> Refreshing Page...')
                try:
                    self.refresh_page()
                    self.cookies = self.get_cookies()
                    self.hadError = False
                except Exception as e :
                    print("Warning!! Exception at refresh page.===> Restarting Chrome...")
                    try:
                        try:
                            self.driver.close()
                        except:
                            xc = 1
                        self.start_chrome_browser()
                        self.cookies = self.get_cookies()
                    except Exception as e :
                        print('ERROR!! Exception at starting chrome.===> Exiting...')
                        self.cookies = None
                        time.sleep(30)
                        break
                    finally:
                        try:
                            self.close_frames()
                            self.switch_to_watchlist('MyWatch')
                            self.hadError = False
                        except:
                            print('Warning!! Exception at close_frames & switch_to_watchlist.')

            time.sleep(monitorPeriod)
           
    def raise_error_flag(self):
        self.hadError = True

    def lower_error_flag(self):
        self.hadError = False

    def add_instrument_to_watchlist(self, instrumentName):
        try:
            searchBox:WebElement = self.wait.until(EC.element_to_be_clickable((By.XPATH,\
                    '//div[@class="search-part searchable select-watch-list"]')))
            searchBox.click()
            # time.sleep(0.02)
            inputBox = self.wait.until(EC.element_to_be_clickable((By.XPATH,\
                    '//div[@class="search-part searchable select-watch-list"]/div/input')))
            inputBox.clear()
            inputBox.send_keys(instrumentName)
            # time.sleep(0.02)
            firstItem:WebElement = self.wait.until(EC.element_to_be_clickable((By.XPATH,\
                                            '//div/div//table//tbody//tr[1]')))
            firstItemText = firstItem.find_element_by_xpath('//td[1]').text
            print(firstItemText)
            if firstItemText == instrumentName:
                firstItem.click()
            else:
                print('Names not matching!!')
            return True
        except Exception as e :
            print('Warning!! Exception at add_instrument_to_watchlist\t', e)
            return None

    def cancel_order(self, tickerName):
        with workFlag:
            try:
                self.switch_to_watchlist('MyWatch')
                a:list[WebElement] = self.driver.find_elements_by_xpath('//div[@class="ag-body-container ag-layout-normal"]/div')
                for item in a:
                    ticker = item.find_element_by_xpath('//div[@class="ag-cell ag-cell-not-inline-editing ag-cell-with-height ag-cell-no-focus yekan bold ag-cell-value ng-scope"]')
                    if ticker.text == tickerName:
                        cancelBtn = item.find_element_by_xpath('//i[@class="Font Ico-trash-o ng-scope"]')
                        cancelBtn.click()
                        return True
                else:
                    return True # hard coded

            except Exception as e :
                print('Warning!! Error at cancel_order.')
                return False

    def edit_order_price(self, tickerName, newPrice):
        '''Returns True if operation was successful. Else returns false.'''
        with workFlag:
            try:
                self.switch_to_watchlist('MyWatch')
                a:list[WebElement] = self.driver.find_elements_by_xpath('//div[@class="ag-body-container ag-layout-normal"]/div')
                for item in a:
                    ticker = item.find_element_by_xpath('//div[@class="ag-cell ag-cell-not-inline-editing ag-cell-with-height ag-cell-no-focus yekan bold ag-cell-value ng-scope"]')
                    if ticker.text == tickerName:
                        cancelBtn = item.find_element_by_xpath('//i[@class="Font Ico-edit ng-scope"]')
                        cancelBtn.click()

                        time.sleep(0.02)
                        priceInput:WebElement = self.wait.until(EC.element_to_be_clickable((By.XPATH,\
                                '//div[@class="quantity-part price"]/div/input')))
                        priceInput.clear()
                        priceInput.send_keys(newPrice)
                        time.sleep(0.02)

                        orderButton:WebElement = self.wait.until(EC.element_to_be_clickable((By.XPATH,\
                                    f'//div[@class="btn-part"]/button[3]')))
                        orderButton.click()
                        time.sleep(0.1)
                        return True
                else:
                    return False

            except Exception as e :
                print('Warning!! Error at cancel_order.')
                return False

    def send_order(self, orderType: orderType, price, quantity):
        try:
            icon:WebElement = self.wait.until(EC.element_to_be_clickable((By.XPATH,\
                                f'//i[@class="icon-online {orderType.value}"]')))
            # icon:WebElement = self.driver.find_element_by_xpath(f'//i[@class="icon-online {orderType.value}"]')                    
            icon.click()
            # time.sleep(0.02)

            priceInput:WebElement = self.wait.until(EC.element_to_be_clickable((By.XPATH,\
                                '//div[@class="quantity-part price"]/div/input')))
            # priceInput:WebElement = self.driver.find_element_by_xpath('//div[@class="quantity-part price"]/div/input')
            priceInput.send_keys(price)
            # time.sleep(0.02)

            quantityInput:WebElement = self.wait.until(EC.element_to_be_clickable((By.XPATH,\
                                    '//div[@class="quantity-part"]/div/input')))
            # quantityInput:WebElement = self.driver.find_element_by_xpath('//div[@class="quantity-part"]/div/input')
            quantityInput.send_keys(quantity)
            # time.sleep(0.02)

            index = 2 if orderType.value =='buy' else 3
            orderButton:WebElement = self.wait.until(EC.element_to_be_clickable((By.XPATH,\
                                    f'//div[@class="btn-part"]/button[{index}]')))
            # orderButton:WebElement = self.driver.find_element_by_xpath(f'//div[@class="btn-part"]/button[{index}]')
            orderButton.click()
            # time.sleep(0.02)
            return True
        except Exception as e :
                print('Warning!!\t', e)
                return None
                
    # =============================<< Api-Based Operations >>============================= #
    def is_server_responding(self):
        result = requests.get(agahUrls.pingUrl, timeout = defaultTimeOut)
        if result.ok:    
            content = result.json()
            response = content['Response']
            if response == 'pong': 
                # print('Ping => Pong')
                return True 
            else:
                raise Exception('Server Not Responding...')

    def get_account_balance(self)-> int:
        try:
            result = requests.get(agahUrls.getQuickBalanceDataUrl,
                                     cookies= self.get_cookies(), timeout = defaultTimeOut)
            if result.ok:    
                content = result.json()
                balance = content['LastBalance']
                return balance
            return None
        except Exception as e :
            print(e)
            return None

    def get_instrument_info(self, Isin:str):
        if Isin is None:
            raise Exception('No valid Isin is provided!')
        url = agahUrls.getInstrumentInfoUrl.format(Isin)
        try:
            result = requests.get(url,cookies= self.get_cookies(), timeout = defaultTimeOut)
            if result.ok:    
                content = result.json()
                instrumentId = content['InstrumentId']
                stateId = content['StateId']
                return (True, instrumentId) if stateId == 2 else (False, instrumentId)
            return None
        except Exception as e :
            print(e)
            return None

    def get_customer_instrument_count(self, Isin)->int:
        if Isin is None:
            raise Exception('No valid Isin is provided!')
        customerId = SettingsService.account.get_agah_customer_id()
        result = self.get_instrument_info(Isin)
        if result is None:
            print('Warning!! Provided Id is not valid or connection error.')
            return
        instrumentId = result[1]
        url = agahUrls.getCustomerInstrumentAssetUrl.format(customerId, instrumentId)
        try:
            result = requests.get(url,cookies= self.get_cookies(), timeout = defaultTimeOut)
            if result.ok:    
                content = int(result.text)
                return content
            return None
        except Exception as e :
            print(e)
            return None

    def get_portfolio(self):
        customerId = SettingsService.account.get_agah_customer_id()
        url = agahUrls.getPortfolioUrl
        try:
            result = requests.get(url,cookies= self.get_cookies(), timeout = defaultTimeOut)
            if result.ok:    
                content = result.json()
                if 'data' in content:
                    portfolio = {}
                    instruments = content['data']
                    for thisInstrument in instruments:
                        isin = thisInstrument['InstrumentIsin']
                        count = thisInstrument['NumberOfShares']
                        portfolio[isin] =  count
                    return portfolio
            return None
        except Exception as e :
            print(e)
            return None

    def get_last_order(self):
        url = agahUrls.getTodayOrdersListUrl
        try:
            result = requests.get(url,cookies= self.get_cookies(), timeout = defaultTimeOut)
            if result.ok:    
                content = result.json()
                if 'data' in content:
                    orders = content['data']
                    if len(orders) > 0:
                        lastOrder = orders[0]
                        return lastOrder
                    else:
                        return None
            return None
        except Exception as e :
            print(e)
            return None
    
    def is_new_order(self, order):
        ''' Compares the time of provided order object with last setted time and returns true if it is
        bigger and updates the last order time.
        '''
        time = int(order['ResponseTime'].split('(')[1].split(')')[0])
        if time is None:
            raise Exception('Unable to get time from order object provided!!')

        if time > self.lastOrderTime:
            self.lastOrderTime = time
            return True
        return False

    def get_new_order_status(self):
        lastOrder = self.get_last_order()
        if lastOrder is None:
            return None
        isNewOrder = self.is_new_order(lastOrder)
        if not isNewOrder:
            return None
        orderStatusId = lastOrder['DecisionStatus']
        if orderStatusId == 4 or orderStatusId == 5:
            print('Success!')
            return orderStatus.Success
        elif orderStatusId == 2:
            print('Partial success!')
            return orderStatus.PartialSuccess
        elif orderStatusId == 1:
            print('Fail!')
            return orderStatus.Fail

    def get_today_orders(self):
        url = agahUrls.getTodayOrdersListUrl
        result = requests.get(url,cookies= self.get_cookies(), timeout = defaultTimeOut)
        if result.ok:    
            content = result.json()
            if 'data' in content:
                orders = content['data']
                if len(orders) > 0:
                    return orders
                else:
                    return []
        return None

    def get_order_detail(self, order):
        orderDetail = agahOrderDetail()
        orderDetail.name= order['InstrumentName'].split(' ')[0]
        orderDetail.responseTime = int(order['ResponseTime'].split('(')[1].split(')')[0])
        orderDetail.tradedQuantity = order['TradedQuantity']
        orderDetail.price = order['Price']
        
        orderSideId = order['OrderSide']
        if orderSideId == 1:
            orderDetail.orderSide = orderType.Buy
        else:
            orderDetail.orderSide = orderType.Sell

        orderStateId = order['DecisionState']
        if orderStateId == 2:
            orderDetail.state = orderState.Active
        else:
            orderDetail.state = orderState.Deactive

        orderStatusId = order['DecisionStatus']
        if orderStatusId == 5:
            orderDetail.status = orderStatus.Success
        elif orderStatusId == 3:
            orderDetail.status = orderStatus.Active
        elif orderStatusId in [4, 10, 11, 12, 13]:
            orderDetail.status = orderStatus.PartialSuccess
        else:
            orderDetail.status = orderStatus.Fail

        return orderDetail         
            
    def generate_orders_report(self):
        orders = self.get_today_orders()
        ordersDetail = []
        for order in orders:
            orderDetail = self.get_order_detail(order)
            ordersDetail.append(orderDetail)

        return ordersDetail

    def analyze_orders_report(self):
        try:
            ao = agahOrders()
            orders:list[agahOrderDetail] = self.generate_orders_report()
            if len(orders) == 0 :
                return None

            for order in orders[::-1]:
                if order.orderSide == orderType.Buy:
                    if order.state == orderState.Deactive:
                        if order.status != orderStatus.Fail:
                            for order2 in orders[::-1]:
                                if order2.orderSide == orderType.Sell and order2.responseTime > order.responseTime and\
                                                order2.name == order.name and order2.state == orderState.Deactive:
                                    # Replacement of old code
                                    ao.closedOrders.append(order)
                                    break
                                    order.tradedQuantity -= order2.tradedQuantity
                                    if order.tradedQuantity == 0:
                                        ao.closedOrders.append(order)
                                        break
                                    if order.tradedQuantity < 0:
                                        # print('Warning!! Asset quantity below zero.')
                                        ao.closedOrders.append(order)
                                        break
                            else:
                                if order.tradedQuantity > 0:
                                    ao.openOrders.append(order)

                    elif order.state == orderState.Active:
                        # Success --> Not possible
                        # Partial --> add to partial list
                        if order.status == orderStatus.PartialSuccess:
                            ao.partialSuccessBuyOrders.append(order)

                        # active  --> add to active list
                        if order.status == orderStatus.Active:
                            ao.activeBuyOrders.append(order)
                    else:
                        print('Warning!! Error at analyze_orders_report.')

                if order.orderSide == orderType.Sell:
                    if order.state == orderState.Active:
                        # Success --> Not Possible
                        # Active --> Add to active sell list
                        if order.status == orderStatus.Active:
                            ao.activeSellOrders.append(order)

                        # Partial --> Add to partial sell list
                        if order.status == orderStatus.PartialSuccess:
                            ao.partialSuccessSellOrders.append(order)

            return ao
        except Exception as e:
            print('Warning!! Error at analyze_orders_report')
            print(e)
            self.raise_error_flag()
            return None

    # =============================<< Integrated Operations >>============================= #
    def execute_order(self, _orderType: orderType, tickerId, price, quantity):
        # Get ticker Date => add instrument to watchlist => send order => [Deprecated Step] check success of order
        # Getting ticker data
        instrument = self.get_ticker(tickerId)
        if instrument is None:
            print('Instrument not found in tickers dict!')
            return False
        Isin = instrument['isin']
        name = instrument['name']

        tradeQuantity = quantity
        if _orderType == orderType.Sell:
            available = self.get_customer_instrument_count(Isin)
            tradeQuantity = max(available, quantity)
        print(f'Before add instrument Time: {datetime.now()}')
        with workFlag:
            # Adding instrument to watchlist
            result = self.add_instrument_to_watchlist(name)
            if result is None:
                return False

            print(f'Before send order Time: {datetime.now()}')
            # Sending order
            result = self.send_order(_orderType, price, tradeQuantity)
            if result is None:
                return False
            return True



