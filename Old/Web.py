from selenium import webdriver
import time
from unidecode import unidecode
import pandas as pd

browser = webdriver.Chrome()
url = 'https://d.easytrader.emofid.com/'
browser.get(url)
time.sleep(4)
usernameStr = '09146308782'
passwordStr = 'Mofid1362086'
username = browser.find_element_by_id('Username')
username.send_keys(usernameStr)
Password = browser.find_element_by_id('Password')
Password.send_keys(passwordStr)
time.sleep(4)
nextButton = browser.find_element_by_id('submit_btn')
nextButton.click()
time.sleep(4)
try:
    UpdateConfirmation = browser.find_element_by_xpath('/html/body/app-root/d-release-notes/div/div/button')
    UpdateConfirmation.click()
except:
    time.sleep(1)

# search ticker
search = browser.find_element_by_xpath('//*[@id="root"]/main/div[2]/div[1]/ul[1]/li[2]/span')
search.click()
time.sleep(1)
search = browser.find_element_by_xpath('//*[@id="root"]/main/d-search-management/search-panel/div/div[1]/input')
search.send_keys('خودرو')
time.sleep(1)
clickTicker = browser.find_element_by_xpath('//*[@id="0"]/div[1]/div/div/b')
clickTicker.click()
time.sleep(1)
# Buy
Buy = browser.find_element_by_xpath('//*[@id="root"]/main/div[3]/div/div/as-split/as-split-area/app-layout-selector/app-layout2/as-split/as-split-area[2]/div/div[1]/div/button[1]')
Buy.click()
time.sleep(1)
Quantity= browser.find_element_by_xpath('//*[@id="quantity"]/div/div[1]/input')
Quantity.send_keys('150000')
time.sleep(1)
Price = browser.find_element_by_xpath('//*[@id="price"]/div/div[1]/input')
Price.click()
Price.send_keys('2047')
time.sleep(1)
BuySend = browser.find_element_by_xpath('//*[@id="root"]/main/div[3]/d-order-list/div/div[2]/div/order-form/div/div/form/div[3]/button[1]')
BuySend.click()
time.sleep(1)
# Sell
Buy = browser.find_element_by_xpath('//*[@id="root"]/main/div[3]/div/div/as-split/as-split-area/app-layout-selector/app-layout2/as-split/as-split-area[2]/div/div[1]/div/button[2]')
Buy.click()
time.sleep(1)
Quantity= browser.find_element_by_xpath('//*[@id="quantity"]/div/div[1]/input')
Quantity.send_keys('120000')
time.sleep(1)
Price = browser.find_element_by_xpath('//*[@id="price"]/div/div[1]/input')
Price.click()
Price.send_keys('2100')
time.sleep(1)
BuySend = browser.find_element_by_xpath('//*[@id="root"]/main/div[3]/d-order-list/div/div[2]/div/order-form/div/div/form/div[3]/button[1]')
BuySend.click()

# The Rest of Money
Money = browser.find_element_by_xpath('//*[@id="root"]/main/div[3]/div/div/div/market-data/div/div[2]/div/span[2]').text
Money = int(float(unidecode(Money.replace(',', ''))))
print('Money:', Money)

Portfoy = browser.find_element_by_xpath('//*[@id="root"]/main/div[2]/div[1]/ul[2]/li[2]/span')
Portfoy.click()
time.sleep(8)

TickerNumber = 1
df = pd.DataFrame(columns=['Name', 'ShareNumber'])

while True:
    try:
        Ticker = browser.find_element_by_xpath('//*[@id="root"]/main/div[3]/div/div/as-split/as-split-area/app-layout-selector/app-layout2/as-split/as-split-area[1]/div/as-split/as-split-area/d-portfolio-watch-container/d-portfolio/div/div[2]/div/ag-grid-angular/div/div[2]/div[2]/div[3]/div[3]/div[{}]/div/div/span/app-symbol-state-renderer'.format(TickerNumber))
        ShareNumber = browser.find_element_by_xpath('//*[@id="root"]/main/div[3]/div/div/as-split/as-split-area/app-layout-selector/app-layout2/as-split/as-split-area[1]/div/as-split/as-split-area/d-portfolio-watch-container/d-portfolio/div/div[2]/div/ag-grid-angular/div/div[2]/div[2]/div[3]/div[2]/div/div/div[{}]/div[1]/app-d-portfolio-item-quantity/div'.format(TickerNumber))
        Ticker = Ticker.text[::-1]
        ShareNumber = int(float(ShareNumber.text.replace(',', '')))
        # print(TickerNumber, Ticker.text[::-1], int(float(ShareNumber.text.replace(',', ''))))
        TickerNumber += 1
        df = df.append({'Name': Ticker, 'ShareNumber': ShareNumber}, ignore_index=True)
    except:
        break

print(df.to_string(index=False))

while True:
    time.sleep(3)
