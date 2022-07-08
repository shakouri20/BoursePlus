import threading, time
from Application.Services.ReadData.ReadOnline.OnlineDataHandler import onlineDataHandler
from FilterPlus.TelegramBot import *
from Application.Services.WriteData.GetOnlineDataService import get_marketWatch_data_tse_method, get_last_clientType_Data

send_message(myTelegramAcountChatID, 'سلام')

firstTime = 1
heven = 0
refid = 0
dataReceivedValidation = 1

def run():

    timer = threading.Timer(5, run)
    timer.start()

    global firstTime
    global heven
    global refid
    global dataReceivedValidation

    try:
        if firstTime:

            t1 = time.perf_counter()
            output = get_marketWatch_data_tse_method(init= 1)
            mwData = output['Data']
            heven = output['Heven']
            refid = output['Refid']
            ctData = get_last_clientType_Data()
            dataHandler.update_data(mwData, ctData)
            firstTime = 0
            print('First', time.perf_counter()-t1)

        else:

            t1 = time.perf_counter()
            mwData = get_marketWatch_data_tse_method(heven= heven, refid= refid)
            ctData = get_last_clientType_Data()
            dataHandler.update_data(mwData, ctData)
            print('Next', time.perf_counter()-t1)

        dataReceivedValidation = 1

    except Exception as e:
        dataReceivedValidation = 0
        print('error in receiving data...')
        return

def update_history_10S():

    timer = threading.Timer(10, update_history_10S)
    timer.start()

    if dataReceivedValidation:
        dataHandler.update_history('10S')
        print('len', len(dataHandler.history['10S'][7745894403636165]['LastPrice']), ' updated')
    else:
        print('data is not valid')
        timer.cancel()
        timer = threading.Timer(3, update_history_10S)
        timer.start()


print('start')
dataHandler = onlineDataHandler(None, {'10S': 10, '1M': None})

run()
update_history_10S()
# mwData = get_marketWatch_data_tse_method(init= 1)
# mwData = get_marketWatch_data_tse_method(heven= mwData['Heven'], refid= mwData['Refid'])
# mwData = get_marketWatch_data_tse_method(heven= 122000, refid= mwData['Refid'])

# x = 1