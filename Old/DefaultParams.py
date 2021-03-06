# import os

# # Sql Server  Connection Settings
# server = os.environ['COMPUTERNAME']
# database = 'TseExpert'

# # TseClient Settings
# instrumentsPath = r'C:\Users\{}\AppData\Roaming\TseClient 2.0\Files\Instruments.csv'.format(os.environ['COMPUTERNAME'])
# selectedInstrumentsPath = r'C:\Users\{}\AppData\Roaming\TseClient 2.0\Files\SelectedInstruments.csv'.format(os.environ['COMPUTERNAME'])
# downloadPath = r'C:\Users\{}\Documents\TseClient 2.0\Adjusted'.format(os.environ['COMPUTERNAME'])
# tseClientExePath = r'C:\Program Files (x86)\TSETMC\TseClient 2.0'

import os
import getpass

userName = getpass.getuser()

# Sql Server  Connection Settings
server = os.environ['COMPUTERNAME']
host = '192.168.1.102:1433'
user = 'TSE'
password = 'AdminAdmin'
database = 'TseExpert'

# TseClient Settings
instrumentsPath = r'C:\Users\{}\AppData\Roaming\TseClient 2.0\Files\Instruments.csv'.format(userName)
selectedInstrumentsPath = r'C:\Users\{}\AppData\Roaming\TseClient 2.0\Files\SelectedInstruments.csv'.format(userName)
downloadPath = r'C:\Users\{}\Documents\TseClient 2.0\Adjusted'.format(userName)
tseClientExePath = r'C:\Program Files (x86)\TSETMC\TseClient 2.0'

# URLs
clientTypeAllUrl = r'http://www.tsetmc.com/tsev2/data/ClientTypeAll.aspx?h=0&r=1'
clientTypeIUrl = r'http://www.tsetmc.com/tsev2/data/clienttype.aspx?i={}' # requires .format() for i
marketWatchUrl = r'http://www.tsetmc.com/tsev2/data/MarketWatchInit.aspx?h=0&r=1'
newMarketWatchUrl = r'http://www.tsetmc.com/tsev2/data/MarketWatchPlus.aspx?h=181045&r=9278802875'
shareHolderIUrl = r'http://tsetmc.com/tsev2/data/ShareHolder.aspx?i={}%2CIRO1IKCO0008' # requires .format() for i
pricesIUrl = r'http://members.tsetmc.com/tsev2/data/InstTradeHistory.aspx?i={}&Top=100000&A=0' # requires .format() for i

