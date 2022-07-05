from Domain.Models.Order import order_validation
from Domain.ImportEnums import *
from Application.Services.Middlewares.MiddlewareFramework.Asset import asset, asset_validation
from Domain.Models.OrderMessageToManager import orderMessageToManager, Order


class portfolio():


    def __init__(self) -> None:
        self.assetList:list[asset] = []

    def __str__(self):
        counter = 0
        data = []
        for asset in self.assetList:
            counter += 1
            data.append(f'{counter}. Id:\t{asset.get_tickerId()}\tVolume:\t{asset.get_amount()}\n')
        return data

    def get_asset_from_portfolio(self, order:Order)-> asset:
        ''' Checks whether asset with same tickerId and timeSpan exists in portfolio and returns it. If asset is not in the portfolio returns None.'''
        for asset in self.assetList:
            if asset.get_tickerId() == order.get_tickerId() and asset.get_time_span() == order.get_time_span():
                return asset
        return None

    @asset_validation        
    def add_asset_to_portfolio(self, _asset:asset)-> None:
        # Check no same asset is in list (compare tickerId and TimeSpan)
        if self.get_asset_from_portfolio(_asset) is not None:
                raise Exception('Provided asset is in asset list. Can not add!!')
        # Everything is Ok, adding to asset list
        self.assetList.append(_asset)
        self.updateLog()

    @asset_validation
    def remove_asset_from_portfolio(self, _asset:asset)-> None:
        # Check whether asset is in the list (compare tickerId and TimeSpan)
        if not _asset in self.assetList:
            raise Exception('Provided asset is not in the asset list. Can not remove!!')
        # Everything is Ok, removing from the asset list
        self.assetList.remove(_asset)
        self.updateLog()

    def get_portfolio_list(self):
        '''Returns list of assets in portfolio. '''
        return self.assetList

    def get_asset_count(self):
        '''Returns number of assets in portfolio. '''
        return len(self.assetList)

    def is_order_in_portfolio(self, order: Order):
        ''' Checks whether asset with same tickerId and timeSpan exists in portfolio . If asset is not in the portfolio returns False.'''
        for asset in self.assetList:
            if asset.get_tickerId() == order.get_tickerId() and asset.get_time_span() == order.get_time_span():
                return True
        return False

    def updateLog(self):
        path = 'Portfolio.txt'
        with open(path, 'w') as f:
            f.writelines(self.__str__())