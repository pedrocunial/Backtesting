from backtesting import evaluateHist
from strategy import Strategy
from order import Order
import numpy as np

class BuynHold(Strategy):
  
  def __init__(self):
    self.bought = False

  def push(self, event):
    # If didnt buy yet, do it
    if not self.bought:
      self.bought = True
      # Send one buy order once
      return [Order(event.instrument, 1, 0)]
    
    # If you need partial result in case of feedback training
    # result = self.partialResult()

    return []

class MAVG(Strategy):
  
  def __init__(self):
    self.signal = 0
    self.prices = []
    self.sizeq = 17 
    self.sizes = 72
    self.std = 0
    self.ref = 0

  def push(self, event):
    price = event.price[3]
    self.prices.append(price)
    orders = []

    if len(self.prices) >= self.sizeq:
      maq = sum(self.prices[-self.sizeq:])/self.sizeq
    if len(self.prices) == self.sizes:
      mas = sum(self.prices)/self.sizes

      if maq > mas and self.signal != 1:
        if self.signal == -1:
          orders.append(Order(event.instrument, 1, 0))
        orders.append(Order(event.instrument, 1, 0))
        self.signal = 1
      elif maq < mas and self.signal != -1:
        if self.signal == 1:
          orders.append(Order(event.instrument, -1, 0))
        orders.append(Order(event.instrument, -1, 0))
        self.signal = -1


      del self.prices[0]

    return orders

print(evaluateHist(BuynHold(), {'IBOV':'^BVSP.csv'}))
print(evaluateHist(MAVG(), {'IBOV':'^BVSP.csv'}))