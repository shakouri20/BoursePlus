import time
import requests

url = 'https://api.telegram.org/bot5306254202:AAF0tjiJqDrLhXtO97xqg-S5Wo2a6ofAeg4/sendMessage'
data = {'chat_id': '858421734', #'858421734' 79479102
        'text': 'علیک'}
proxies = {'https': "socks5h://127.0.0.1:1080"}

while True:
    try:
        x = requests.post(url, json= data, proxies= proxies) #
        print('Successfull!')
        break
    except:
        time.sleep(0.5)
        print('error')
