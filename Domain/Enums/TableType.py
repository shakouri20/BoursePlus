import enum

class tableType(enum.Enum):
    # real
    Tickers = 'Tickers'
    TickerTypes = 'TickerTypes'
    IndustryTypes = 'IndustryTypes'
    MarketTypes = 'MarketTypes'

    OfflineData = 'OfflineData'
    OnlineData = 'OnlineData'

    # Mock
    MockOfflineData = 'MockOfflineData'
    MockOnlineData = 'MockOnlineData'