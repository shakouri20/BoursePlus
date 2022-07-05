from datetime import datetime
from math import ceil
from Domain.Enums.OrderTimeSpan import orderTimeSpan
from Settings import SettingsService

class fundInfo():
    def __init__(self) -> None:
        self.balance = None
        self.equity = None
        self.freeMargin = None
        self.marginRatio = None
        self.timeSpanBalance = {
                orderTimeSpan.Daily : None ,\
                orderTimeSpan.ShortTerm : None ,\
                orderTimeSpan.MidTerm : None ,\
                orderTimeSpan.LongTerm : None}
        self.maxTimeSpanBalance = {
                orderTimeSpan.Daily : None ,\
                orderTimeSpan.ShortTerm : None ,\
                orderTimeSpan.MidTerm : None ,\
                orderTimeSpan.LongTerm : None}

        self.set_max_time_span_balance()

#==================================================================<< Real Time >>===================================================

    def get_report(self):
        fundData = []
        fundData.append(f'Last Updated:\t{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n')
        fundData.append('============================<< Fund Data >>=============================\n')
        fundData.append(f'Balance:\t{round(self.balance/10**7,1)} M\n')
        fundData.append(f'FreeMargin: {round(self.freeMargin/10**7,1)} M\n')
        fundData.append(f'Daily:\t\t{round(self.timeSpanBalance[orderTimeSpan.Daily]/10**7,1)} / {round(self.maxTimeSpanBalance[orderTimeSpan.Daily]/10**7,1)} M\n')
        fundData.append(f'ShortTerm:\t{round(self.timeSpanBalance[orderTimeSpan.ShortTerm]/10**7,1)} / {round(self.maxTimeSpanBalance[orderTimeSpan.ShortTerm]/10**7,1)} M\n')
        fundData.append(f'MidTerm:\t{round(self.timeSpanBalance[orderTimeSpan.MidTerm]/10**7,1)} / {round(self.maxTimeSpanBalance[orderTimeSpan.MidTerm]/10**7,1)} M\n')
        fundData.append(f'LongTerm:\t{round(self.timeSpanBalance[orderTimeSpan.LongTerm]/10**7,1)} / {round(self.maxTimeSpanBalance[orderTimeSpan.LongTerm]/10**7,1)} M\n')
        fundData.append('\n')
        return fundData

    def set_balance(self, balance:int):
        if not isinstance(balance, int):
            raise Exception('Provided balance is not integer!')
        if balance < 0 :
            raise Exception('Provided balance is negative!')
        self.balance = balance

        # Updating max time span balance
        self.set_max_time_span_balance()

    def set_free_margin(self, freeMargin:int):
        if not isinstance(freeMargin, int):
            raise Exception('Provided freeMargin is not integer!')
        self.freeMargin = freeMargin

    def get_time_span_free_margin(self, timeSpan:orderTimeSpan):
        if self.freeMargin is None:
            raise Exception('Free margin has not been set!')
        if not isinstance(timeSpan, orderTimeSpan):
            raise Exception('Provided time span is not valid!')

        timeSpanFreeMargin = self.maxTimeSpanBalance[timeSpan] - self.timeSpanBalance[timeSpan]
        return timeSpanFreeMargin if self.freeMargin >= timeSpanFreeMargin else self.freeMargin

    def set_time_span_balance(self, timeSpan:orderTimeSpan, amount:int):
        if not isinstance(amount, int):
            raise Exception('Provided amount is not integer!')
        if amount < 0 :
            raise Exception('Provided amount is negative. Provide a positive integer number.')
        if not isinstance(timeSpan, orderTimeSpan):
            raise Exception('Provided time span is not valid!')

        self.timeSpanBalance[timeSpan] = amount

    # automatically called when set_balance is called
    def set_max_time_span_balance(self):
        balance = SettingsService.realTime.get_realTime_initial_balance()
        ratios = SettingsService.trade.get_time_span_major_ratios()
        for timeSpan in orderTimeSpan:
            self.maxTimeSpanBalance[timeSpan] = ceil(balance * ratios[timeSpan])

    def get_free_margin(self):
        return self.freeMargin



#==============================================================<< Others >>===========================================================
    def set_equity(self, equity:int):
        if not isinstance(equity, int):
            raise Exception('Provided equity is not integer!')
        self.equity = equity

    def get_balance(self):
        if self.balance is None:
            raise Exception('Balance has not been set!')
        return self.balance

    def get_equity(self):
        if self.equity is None:
            raise Exception('Equity has not been set!')
        return self.equity

    def get_margin_ratio(self):
        balance = self.get_balance()
        freeMargin = self.get_freeMargin()
        return round(freeMargin/balance* 100, 1)

    def has_free_margin(self, requiredMargin:int):
        freeMargin = self.get_freeMargin()
        if requiredMargin >= freeMargin:
            return True
        else:
            return False

    # For backtest mode
    def increase_time_span_balance(self, timeSpan:orderTimeSpan , amount:int):
        if not isinstance(amount, int):
            raise Exception('Provided amount is not integer!')
        if amount <= 0 :
            raise Exception('Provided amount is negative. Provide a positive integer number.')
        if not isinstance(timeSpan, orderTimeSpan):
            raise Exception('Provided time span is not valid!')

        self.timeSpanBalance[timeSpan] += amount

    # For backtest mode
    def decrease_time_span_balance(self, timeSpan:orderTimeSpan , amount:int):
        if not isinstance(amount, int):
            raise Exception('Provided amount is not integer!')
        if amount <= 0 :
            raise Exception('Provided amount is negative. Provide a positive integer number.')
        if not isinstance(timeSpan, orderTimeSpan):
            raise Exception('Provided time span is not valid!')
        if self.timeSpanBalance[timeSpan] < amount:
            raise Exception('Provided amount is larger than time span balance!')

        self.timeSpanBalance[timeSpan] -= amount

    def get_time_span_balance(self, timeSpan:orderTimeSpan):
        if not isinstance(timeSpan, orderTimeSpan):
            raise Exception('Provided time span is not valid!')
        # self.set_max_time_span_balance()
        return self.timeSpanBalance[timeSpan]
    
    

    def set_all_time_span_balance_to_zero(self):
        '''Sets the current balance of all time spans equal to zero. This is usually
            used for back test runs.'''
        for timeSpan in orderTimeSpan:
            self.timeSpanBalance[timeSpan] = 0

    

    def modify_balance(self, amount:int):
        if not isinstance(amount, int):
            raise Exception('Provided amount is not integer!')
        self.balance += amount

