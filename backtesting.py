from marketdata import MarketData
from tradingsystem import TradingSystem
from strategy import Strategy

def evaluate(strategy, type, files, *, has_config=False):
  strategy.clear()
  data = MarketData()

  ts = TradingSystem()  
  
  for instrument, file_data in files.items():
    ts.createBook(instrument)
    ts.subscribe(instrument, strategy)
    if type == MarketData.TICK:
      data.loadBBGTick(file_data, instrument)
    elif type == MarketData.HIST:
      data.loadYAHOOHist(file_data, instrument)
    elif type == MarketData.INTR:
      if has_config:
        data.loadBBGIntr(file_data[0], instrument, separator=file_data[1],
                         date_format=file_data[2])
      else:
        data.loadBBGIntr(file_data, instrument)


  data.run(ts)

  ts.submit(strategy.id, strategy.close())
  return strategy.summary()

def evaluateTick(strategy, files):
  return evaluate(strategy, MarketData.TICK, files)

def evaluateHist(strategy, files):
  return evaluate(strategy, MarketData.HIST, files)

def evaluateIntr(strategy, files, has_config=False):
  return evaluate(strategy, MarketData.INTR, files, has_config=has_config)
