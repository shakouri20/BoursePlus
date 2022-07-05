from Domain.Models.Order import Order, order_validation


class tradeLog():
    def __init__(self) -> None:
        self.orderList:list[Order] = []

    @order_validation
    def add_order_to_log(self, order:Order) -> None:
        self.orderList.append(order)

    