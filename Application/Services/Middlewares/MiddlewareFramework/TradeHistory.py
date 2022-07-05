from datetime import datetime
from Domain.Models.Setting import backTestModel
from Domain.ImportEnums import *
from Application.Services.Middlewares.MiddlewareFramework.Position import position, position_validation
from Settings import SettingsService

class tradeHistory():
    def __init__(self) -> None:
        self.positionsDict : dict[str,position] = {}
        operationMode = SettingsService.operation.get_runType_setting()
        if operationMode == runType.RealTime:
            self.read_trade_history_from_db()

    @position_validation
    def add_position_to_history(self, uuid, _position:position) -> None:
        if uuid in self.positionsDict:
            raise Exception('Provided uuid is repetitive.')
        self.positionsDict[uuid] = _position

    def get_position_by_order(self, tickerId:int, timeSpan:orderTimeSpan):
        '''Returns the asset matching the order by checking tickerId and timeSpan.
        Returns None if no matching open position is found.
        Position must be open!'''
        for positionKey in self.positionsDict:
            if self.positionsDict[positionKey].is_position_fit_to_order(tickerId, timeSpan):
                return self.positionsDict[positionKey]
        return None

    def get_trade_history_data(self, startDate: str = '1360-01-01', endDate:str = '3000-12-12')-> tuple:
        _startDate = datetime.strptime(startDate, '%Y-%m-%d')
        _endDate = datetime.strptime(endDate, '%Y-%m-%d')
        customTradeList : list[dict]  = []
        profit = 0
        tradeCount = 0
        closedCount = 0
        for uuid in self.positionsDict:
            if self.positionsDict[uuid].get_start_time() >= _startDate and \
                        self.positionsDict[uuid].get_start_time() <= _endDate:
                customTradeList.append(self.positionsDict[uuid].get_position_report())
                tradeCount += 1
                if self.positionsDict[uuid].is_closed():
                    closedCount += 1
                    profit += self.positionsDict[uuid].get_profit()

        return (customTradeList, profit, tradeCount, closedCount)

    def read_trade_history_from_db(self):
        pass

    def __str__(self) -> str:
        print('Representing class...')