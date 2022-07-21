
from cmath import nan
import datetime
import threading
import time
from matplotlib import pyplot as plt

import numpy as np
from Application.Services.WriteData.GetOnlineDataService import get_last_clientType_Data, get_marketWatch_data_tse_method
from Application.Utility.AdvancedPlot import advancedPlot
from Infrastructure.Repository.OfflineDataRepository import offlineData_repo
from TelegramProject.TelegramBot import *
import timeit, os, sys

from TelegramProject.main import print_error


# output = get_marketWatch_data_tse_method(init= 1)
# output = get_marketWatch_data_tse_method(heven= 100000, refid= 10434169200)
# output = get_marketWatch_data_tse_method(heven= output['Heven'], refid= output['Refid'])


# while True:

# try:
#     ctData = get_last_clientType_Data()

#     print(ctData[31049085025064185]['RealBuyNumber'], ctData[31049085025064185]['RealSellNumber'])

# except:
#     print('Error')

# class testClass:

#     def __init__(self) -> None:
#         print('\ntestClass inited')

#     def __del__(self):
#         print("deleted")

#     def Hello(self):
#         print('waiting...')
#         time.sleep(10)
#         print('start')
#         self.a = []
#         for i in range(3000000):
#             # print(' ', i, end= '\r')
#             self.a.append(i)
#         print('end')



# testObj = testClass()
# testObj.Hello()


# time.sleep(10)


# testObj = testClass()
# testObj.Hello()

# input()

# testObj.a = []

# input()

num_threads = threading.active_count()

print(num_threads)


