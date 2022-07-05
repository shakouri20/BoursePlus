from selenium import webdriver
import time
from unidecode import unidecode
import pandas as pd
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import winsound


browser = webdriver.Chrome()
url = 'https://superapp.snappfood.ir/'
browser.get(url)

input()

browser.execute_script("window.scrollTo(0, 1000)") 

while True:

    try:
        orderElement = WebDriverWait(browser, 2).until(
        EC.presence_of_element_located((By.XPATH, '//*[@id="orderTab"]')))
        orderElement.click()

        topTabElement = WebDriverWait(browser, 2).until(
        EC.presence_of_element_located((By.XPATH, '//*[@id="app"]/nav/div/div[2]')))
        

        homeElement = WebDriverWait(browser, 2).until(
        EC.presence_of_element_located((By.XPATH, '//*[@id="homeTab"]')))
        homeElement.click()

        foodPartyElement = WebDriverWait(browser, 2).until(
        EC.presence_of_element_located((By.XPATH, '//*[@id="app-shell"]/div/div/div[3]/div/div[1]/span')))

        pecElement = WebDriverWait(browser, 2).until(
        EC.presence_of_element_located((By.XPATH, '//*[@id="app-shell"]/div/div/div[3]/div/div[2]/div/section[1]/div[1]/div[2]/div/div/div[1]/span[1]')))
        prcNum = int(float(unidecode(pecElement.text))) 
        print(prcNum)
        if prcNum >= 70:
            pecElement.click()
            winsound.Beep(500, 1500)
            input()
    except:
        browser.execute_script("window.scrollTo(0, 1000)") 
    
