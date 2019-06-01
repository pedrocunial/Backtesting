from backtesting import evaluateHist, evaluate, evaluateIntr
from marketdata import MarketData
from strategy import Strategy
from order import Order

from dataPedro.train_model import load_model

import numpy as np


PETR = 'PETR3.csv'
STOCK = 'stock'
COIN = 'coin'


class SAR(Strategy):

    def __init__(self):
        self.sar = []
        self.highs = []
        self.lows = []
        self.accel_min = 0.01
        self.accel_max = 0.1
        self.accel = self.accel_min
        self.crescent = True
        self.buying = 0

    def push(self, event):
        high = event.price[1]
        low = event.price[2]
        price = event.price[3]
        orders = []
        if self.sar:
            price = event.price[3]
            sar_prev = self.sar[-1]
            if self.crescent:
                sar_predict = sar_prev + self.accel * (self.highs[-1] -
                                                       sar_prev)
                if sar_predict > price:
                    self.crescent = False
                    if self.buying == 1:
                        orders += [Order(event.instrument, -1, 0),
                                   Order(event.instrument, -1, 0)]
                        self.buying = -1
                    elif self.buying == 0:
                        orders.append(Order(event.instrument, -1, 0))
                        self.buying = -1
                    self.accel = self.accel_min
                else:
                    self.accel = min(self.accel * 2, self.accel_max)
            else:
                sar_predict = sar_prev + self.accel * (self.lows[-1] -
                                                       sar_prev)
                if sar_predict < price:
                    self.crescent = True
                    if self.buying == -1:
                        orders += [Order(event.instrument, 1, 0),
                                   Order(event.instrument, 1, 0)]
                        self.buying = 1
                    elif self.buying == 0:
                        orders.append(Order(event.instrument, 1, 0))
                        self.buying = 1
                    self.accel = self.accel_min
                else:
                    self.accel = min(self.accel * 2, self.accel_max)
        else:
            sar_predict = price
        self.highs.append(high)
        self.lows.append(low)
        self.sar.append(sar_predict)
        return orders


class PedroStrategy(Strategy):

    def __init__(self, model=load_model('dataPedro/model')):
        self.model = model
        self.stack = []
        self.buying = 0

    def act(self, goal, instrument):
        if self.buying == 0:
            return [Order(instrument, goal, 0)]
        elif self.buying == goal:
            return []
        else:
            return [Order(instrument, goal, 0), Order(instrument, goal, 0)]

    def push(self, event):
        self.stack.append([event.price[3]])
        if not self.is_stacking:
            predict = self.model.predict(np.array([self.stack[-10:]]))
            return self.act(-1 if predict < event.price[3] else 1,
                            event.instrument)
        return []

    @property
    def is_stacking(self):
        return len(self.stack) < 10


class PedroIntr(Strategy):

    def __init__(self, stock=None, coin=None, petr=None,
                 a=2.80049207, b=0, F=2):
        self.stock = stock
        self.coin = coin
        self.petr = petr
        self.tc = b
        self.F = F
        self.ti = a / self.F
        self.buying = 0

    def pushCoin(self, event):
        self.coin = event.price[2]
        if self.petr is None:
            return []
        pbr = (self.petr / self.coin) * (self.F * self.ti)
        order = None
        if pbr < 2 * self.petr:
            order = [Order(COIN, 1, (self.petr + pbr) / 2),
                     Order(PETR, -1, self.coin)]
            buy = True
        elif pbr > 2 * self.petr:
            order = [Order(COIN, -1, self.coin),
                     Order(PETR, 1, (self.petr + pbr) / 2)]
            buy = False

        result = []
        if order is not None:
            if self.buying == 0:
                result = order
            elif self.buying == -1:
                if buy:
                    result = 2 * order
            else:
                if not buy:
                    result = 2 * order
        return result

    def pushPetr(self, event):
        self.petr = event.price[2]
        if self.coin is None:
            return []
        pbr = self.petr / self.coin * (self.F * self.ti)
        order = None
        if pbr < self.petr:
            order = [Order(PETR, -1, (self.petr + pbr) / 2),
                     Order(COIN, 1, self.coin)]
            buy = True
        elif pbr > self.petr:
            order = [Order(COIN, -1, self.coin),
                     Order(PETR, 1, (self.petr + pbr) / 2)]
            buy = False

        result = []
        if order is not None:
            if self.buying == 0:
                result = order
            elif self.buying == -1:
                if buy:
                    result = 2 * order
            else:
                if not buy:
                    result = 2 * order
        return result

    def fill(self, instrument, price, quantity, status):
        super().fill(instrument, price, quantity, status)

    def push(self, event):
        if event.instrument == STOCK:
            print(STOCK)
            return []
        elif event.instrument == COIN:
            return self.pushCoin(event)
        elif event.instrument == PETR:
            return self.pushPetr(event)
        else:
            raise ValueError('Event instrument not accepted')
        return []


print(evaluateHist(SAR(), {'IBOV': '^BVSP.csv'}))
print(evaluateHist(PedroStrategy(), {'IBOV': 'dataPedro/test_data.csv'}))
print(evaluateIntr(PedroIntr(), {
    STOCK: None,
    COIN: [
        'USDBRL.csv',
        ';',
        '%d/%m/%Y %H:%M:%S'
    ],
    PETR: [
        PETR,
        ';',
        '%d/%m/%Y %H:%M:%S'
    ],
}, has_config=True))
