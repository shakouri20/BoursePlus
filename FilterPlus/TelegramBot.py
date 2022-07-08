import requests

hostName = '127.0.0.1'
port = '1080'
token = 'bot5306254202:AAF0tjiJqDrLhXtO97xqg-S5Wo2a6ofAeg4'

myTelegramAcountChatID = '858421734'
marketTrendChatID = '-1001648422452'

proxy = {'https': "socks5h://" + hostName + ":1080"}

def send_message(chatID, message):
    url = 'https://api.telegram.org/' + token + '/sendMessage'
    data = {'chat_id': chatID, 'text': message}

    for _ in range(5):
        try:
            requests.post(url, json= data, proxies= proxy)
            return True
        except:
            pass
    else:
        return False

def send_photo(chatID, filePath, caption):
    url = 'https://api.telegram.org/' + token + '/sendPhoto'
    data = {'chat_id': chatID, 'caption': caption}
    file = {'photo': open(filePath, 'rb')}

    for _ in range(5):
        try:
            requests.post(url, data= data, proxies= proxy, files= file)
            return True
        except:
            pass
    else:
        return False