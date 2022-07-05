from time import sleep
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
import requests


driver = webdriver.Chrome()

url = r'https://online.agah.com'
driver.get(url)


input()

script = """function agah_order(){

  let xhr = new XMLHttpRequest();
  xhr.open("POST", "https://online.agah.com/Order/SendOrder", false);
  xhr.setRequestHeader("Accept", "application/json, text/plain, */*");
  xhr.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
  xhr.onreadystatechange = function () {
      if (xhr.readyState === 4){
          console.log(this.response.text)
          if (xhr.status != '200'){
              console.log('Error sending...')  
              return false
          }
          else{
              console.log(this.response)
              return true
          }
      }
  };

var data = `{
  "orderModel": {
      "Id": 0,
      "CustomerId": 165921860,
      "CustomerTitle": "علی شکوری گنبری ",
      "OrderSide": "Buy",
      "OrderSideId": 1,
      "Price": 7460,
      "Quantity": 200000,
      "Value": 0,
      "ValidityDate": null,
      "MinimumQuantity": null,
      "DisclosedQuantity": null,
      "ValidityType": 1,
      "InstrumentId": 390,
      "InstrumentIsin": "IRO1PNES0001",
      "InstrumentName": "شپنا",
      "BankAccountId": 0,
      "ExpectedRemainingQuantity": 0,
      "TradedQuantity": 0,
      "CategoryId": "e546e2ad-e53b-43b4-b281-e81b9f397665",
      "RemainingQuantity": 200000,
      "OrderExecuterId": 3
  },
  "nonce": ` + generate_nounce() + `}`
  xhr.send(data);
}

function generate_nounce(){

  let xhr = new XMLHttpRequest();
  xhr.open("POST", "https://online.agah.com/Order/GenerateNonce", false);
  xhr.setRequestHeader("Accept", "application/json, text/plain, */*");
  xhr.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
  xhr.onreadystatechange = function () {
      if (xhr.readyState === 4){
          if (xhr.status != '200'){
              console.log('Error sending...')  
          }
      }
  };

  xhr.send(null);
  return xhr.responseText
}
agah_order()
"""
  
# generate a alert via javascript
driver.execute_script(script)

# xhr.open("POST", "https://online.agah.com/Order/GenerateNonce", false);
# xhr.setRequestHeader("Accept", "application/json, text/plain, */*");
# xhr.setRequestHeader("Content-Type", "application/json;charset=UTF-8");


















# import json
# import requests
# import urllib.request
# from PIL import Image
 
# # load page
# response = requests.post("https://online.agah.com/") # , json=data
# print("Status Code", response.status_code)
# csrftoken = response.text.split('csrftoken="')[1][:32]
# print(csrftoken)

# # # get image
# # urllib.request.urlretrieve('https://online.agah.com/Auth/Captcha', 'code')
# # img = Image.open('code')
# # img.show()

# # captcha = input()
# captcha = 'skrtgjs'

# url = "https://online.agah.com/Auth/login?returnUrl=/"
# headers = {"Content-Type": "application/x-www-form-urlencoded"}
#             # "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
#             # "Accept-Encoding": "gzip, deflate, br",
#             # "Accept-Language": "en-US,en;q=0.9,fa;q=0.8",
#             # "Cache-Control": "max-age=0",
#             # "Connection": "keep-alive",
#             # 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36'}

# data = 'username=shakouri20&password=agah1362086&captcha=' + captcha + '&otp=&tknfv=' + csrftoken
# payload = {
#     'username': 'shakouri20', 
#     'password': 'agah1362086', 
#     'captcha': captcha, 
#     'otp': '',
#     'tknfv': csrftoken
# }
# print(data)
# # print(payload)
# response = requests.post(url, headers=headers, data= data.encode('utf-8'))  #.encode('utf-8') json.dumps(payload)

# print("Status Code", response.status_code)
# print("JSON Response ", response.text)

# url = "https://online.agah.com/Order/GenerateNonce"
# headers = {"Content-Type": "application/json; charset=utf-8",
#             "Accept": "application/json, text/plain, */*",
#             'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36'}
# response = requests.post(url, headers=headers) # , json=data

# print("Status Code", response.status_code)
# print("JSON Response ", response.text)
 