from ta.momentum import *
from ta.trend import *
from ta.volatility import *
import pandas as pd

# Calculating RSI of a ticker
def calculateRsi(priceList:list, length: int = 14, fillna: bool = False)-> list:
    """Returns the calculated Rsi from provided price list. """
    rsiObj = RSIIndicator(pd.Series(priceList), length, fillna)
    return rsiObj.rsi().to_list()
     
# Calculating MFI of a provided list of price and volume
def calculateMfi(priceList:list, volumeList:list, length: int = 14)-> list:
    """Returns the calculated Mfi from provided price and volume list. """
    return

# Calculating MACD of a provided list of price and volume 26 12 9
def calculateMacd(priceList:list, slowLength: int = 26, fastLength: int = 12, signalSmoothing: int = 9, fillna: bool = False)-> list:
    """Returns the list of calculated MACD from provided price list. """
    macdObj = MACD(pd.Series(priceList), slowLength, fastLength, signalSmoothing, fillna)
    # return macdObj.macd_diff().to_list()
    return macdObj.macd_diff().to_list()

# Calculating sma of a list
def calculateSma(priceList:list, window: int = 10, fillna: bool = False)-> list:
    """Returns the list of calculated sma from provided price list. """
    smaObj = SMAIndicator(pd.Series(priceList), window, fillna)
    return smaObj.sma_indicator().to_list()

# Calculating sma of a list
def calculateEma(priceList:list, window: int = 10, fillna: bool = False)-> list:
    """Returns the list of calculated sma from provided price list. """
    emaObj = EMAIndicator(pd.Series(priceList), window, fillna)
    return emaObj.ema_indicator().to_list()

# Calculating stock RSI of a ticker
def calculateStochRsi(priceList:list, window: int = 14, smooth1: int = 3, smooth2: int = 3, fillna: bool = False)-> list:
    """Returns the calculated stock Rsi from provided price list. """
    rsiObj = StochRSIIndicator(pd.Series(priceList), window, smooth1, smooth2, fillna)
    return rsiObj.stochrsi_d().to_list()

# Calculating BollingerBands of a ticker
def calculateBB(priceList:list, window: int = 20, window_dev: int = 2, fillna: bool = False)-> tuple:
    """Returns the calculated BollingerBands from provided price list. """
    bbObj = BollingerBands(pd.Series(priceList), window, window_dev, fillna)
    return (bbObj.bollinger_mavg().to_list(), bbObj.bollinger_hband().to_list(), bbObj.bollinger_lband().to_list())

# Calculating ichimoko of a ticker
def calculateIchimoko(highPrice:list, lowPrice:list, window1: int = 9, window2: int = 26, window3: int = 52, visual: bool = False, fillna: bool = False)-> tuple:
    """Returns the calculated BollingerBands from provided price list. """
    ichObj = IchimokuIndicator(pd.Series(highPrice), pd.Series(lowPrice), window1, window2, window3, visual, fillna)
    return (ichObj.ichimoku_conversion_line().to_list(), ichObj.ichimoku_base_line().to_list(), ichObj.ichimoku_a().to_list(), ichObj.ichimoku_b().to_list())
  