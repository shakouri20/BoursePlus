
class middlewareOffline:

    def __init__(self, IDs: list) -> None:
        
        self.history = {}
        self.name = None

        for ID in IDs:
            self.history[ID] = {}

    def process():
        raise NotImplementedError()

    @staticmethod
    def adjust_price(price, adjustedClosePrice, unAdjustedClosePrice):
        dif = (unAdjustedClosePrice-adjustedClosePrice)/adjustedClosePrice*100
        if abs(dif) < 1:
            return price
        else:
            if type(price) == list:
                tempPrice = price.copy()
                return [int(thisPrice * adjustedClosePrice / unAdjustedClosePrice) for thisPrice in tempPrice]
            else:
                return int(price * adjustedClosePrice / unAdjustedClosePrice)

    @staticmethod
    def calc_heikinAshi(openPrice, closePrice, highPrice, lowPrice):

        if len(openPrice) == len(closePrice) == len(highPrice) == len(lowPrice):
            
            haOpenPrice = [0 for i in range(len(openPrice))]
            haClosePrice = [0 for i in range(len(openPrice))]
            haHighPrice = [0 for i in range(len(openPrice))]
            haLowPrice = [0 for i in range(len(openPrice))]
            
            for i in range(len(openPrice)):
                if i == 0:
                    haOpenPrice[i] = (openPrice[i]+closePrice[i])/2
                else:
                    haOpenPrice[i] = (haOpenPrice[i-1]+haClosePrice[i-1])/2
                haClosePrice[i] = (openPrice[i]+closePrice[i]+highPrice[i]+lowPrice[i])/4
                haHighPrice[i] = max(haOpenPrice[i], haClosePrice[i], highPrice[i])
                haLowPrice[i] = min(haOpenPrice[i], haClosePrice[i], lowPrice[i])

            return (haOpenPrice, haClosePrice, haHighPrice, haLowPrice)

        else:
            raise Exception
