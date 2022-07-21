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
clientTypeAllUrl = r'http://www.tsetmc.com/tsev2/data/ClientTypeAll.aspx'
clientTypeIUrl = r'http://www.tsetmc.com/tsev2/data/clienttype.aspx?i={}' # requires .format() for i
marketWatchUrl = r'http://www.tsetmc.com/tsev2/data/MarketWatchPlus.aspx'
marketWatchInitUrl = r'http://www.tsetmc.com/tsev2/data/MarketWatchInit.aspx?h=0&r=0'
MarketWatchPlusUrl = r'http://www.tsetmc.com/tsev2/data/MarketWatchPlus.aspx?h={}&r={}'
shareHolderIUrl = r'http://tsetmc.com/tsev2/data/ShareHolder.aspx?i={}%2CIRO1IKCO0008' # requires .format() for i
pricesIUrl = r'http://members.tsetmc.com/tsev2/data/InstTradeHistory.aspx?i={}&Top={}&A=0' # requires .format() for i

