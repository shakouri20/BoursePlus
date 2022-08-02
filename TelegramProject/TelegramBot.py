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

def send_message(chatID, message, replyMessageID= None, replyMarkup= None):
    url = 'https://api.telegram.org/' + token + '/sendMessage'
    data = {'chat_id': chatID, 'text': message, 'parse_mode': 'HTML'}
    if replyMessageID != None:
        data['reply_to_message_id'] = replyMessageID
    if replyMarkup != None:
        data['reply_markup'] = replyMarkup #{'inline_keyboard': [[{'text': 'Hello', 'callback_data': 'Pressed'}]]}

    for _ in range(2):
        try:
            response = requests.post(url, json= data, proxies= proxy, timeout= 2)
            return json.loads(response.text)['result']['message_id']
        except:
            pass
    else:
        print('Message Error...')
        return False

def send_photo(chatID, filePath, caption):
    url = 'https://api.telegram.org/' + token + '/sendPhoto'
    data = {'chat_id': chatID, 'caption': caption, 'parse_mode': 'HTML'}
    file = {'photo': open(filePath, 'rb')}

    for _ in range(3):
        try:
            response = requests.post(url, data= data, proxies= proxy, files= file, timeout= 10)
            data = json.loads(response.text)
            if data['ok']:
                return True
            else:
                pass
        except:
            pass
    else:
        print('Photo Error...')
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