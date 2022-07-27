import json
import requests

hostName = '127.0.0.1'
port = '1080'
token = 'bot5306254202:AAF0tjiJqDrLhXtO97xqg-S5Wo2a6ofAeg4'
useProxy = False

myTelegramAcountChatID = '858421734'
filterPlusGroupChatID = '-1001589960704'
marketTrendChatID = '-1001648422452'
positiveRangeChatID = '-1001788821558'
doroshtBinChatID = '-1001645245212'

proxy = {'https': "socks5h://" + hostName + ":1080"} if useProxy else {}

def send_message(chatID, message, replyMessageID= None):
    url = 'https://api.telegram.org/' + token + '/sendMessage'
    if replyMessageID != None:
        data = {'chat_id': chatID, 'text': message, 'parse_mode': 'HTML', 'reply_to_message_id': replyMessageID}
    else:
        data = {'chat_id': chatID, 'text': message, 'parse_mode': 'HTML'}

    for _ in range(2):
        try:
            response = requests.post(url, json= data, proxies= proxy, timeout= 2)
            return json.loads(response.text)['result']['message_id']
        except:
            pass
    else:
        print('Telegram Error...')
        return False

def send_photo(chatID, filePath, caption):
    url = 'https://api.telegram.org/' + token + '/sendPhoto'
    data = {'chat_id': chatID, 'caption': caption, 'parse_mode': 'HTML'}
    file = {'photo': open(filePath, 'rb')}

    for _ in range(5):
        try:
            requests.post(url, data= data, proxies= proxy, files= file, timeout= 5)
            return True
        except:
            pass
    else:
        return False

def get_updates(offset= None):
    url = 'https://api.telegram.org/' + token + '/getUpdates'
    if offset != None:
        data = {'offset': offset}
    else:
        data = {}

    for _ in range(5):
        try:
            response = requests.post(url, json= data, proxies= proxy)
            return json.loads(response.text)
        except:
            pass
    else:
        return False