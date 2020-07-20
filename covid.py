from marketstack import getAvailableTickersFromMarketstack, getDailyDataFromMarketstack
import sys
import numpy as np
from datetime import datetime
import json

def getPostCovidMaxFromFile(symbol):
  with open('maxCovid.json') as jsonMaxFile:
    maxData = json.load(jsonMaxFile)
  
  for symbolInfo in maxData:
    if symbolInfo['symbol'] == symbol: return symbolInfo['maxClose']
  return -1

def getPostCovidMinFromFile(symbol):

  with open('minCovid.json') as jsonMinFile:
    minData = json.load(jsonMinFile)
  
  for symbolInfo in minData:
    if symbolInfo['symbol'] == symbol: return symbolInfo['minClose']
  return -1


def getPostCovidMinMax(symbol):
  verbose = False
  
  df = getDailyDataFromMarketstack(symbol, '2020-03-16', '2020-07-21', verbose)
  
  now = datetime.now()

  if df.empty:
    return (0,now,0,now)

  minClose = np.min(df['Close'])
  minCloseDate = df[df['Close'] == minClose]['Date']
  minCloseDate = minCloseDate[minCloseDate.index[0]]

  maxClose = np.max(df['Close'])
  maxCloseDate = df[df['Close'] == maxClose]['Date']
  maxCloseDate = maxCloseDate[maxCloseDate.index[0]]

  return (minClose, minCloseDate, maxClose, maxCloseDate)
 

def main(argv):
  availableTickers = getAvailableTickersFromMarketstack(False)

  min = getPostCovidMinFromFile('FALABELLA.XSGO')
  max = getPostCovidMaxFromFile('FALABELLA.XSGO')

  print("min: ", min, " max: ", max)
  return

  # minCovidClose = []
  # maxCovidClose = []

  # for symbol in availableTickers:
  #   (minClose, minCloseDate, maxClose, maxCloseDate) = getPostCovidMinMax(symbol)
  #   print(symbol, ",", minClose, ",", minCloseDate, ",", maxClose, ",", maxCloseDate)
  #   minCovidClose.append({"symbol": symbol, "minClose": minClose, "minCloseDate": minCloseDate.strftime("%Y-%m-%d")})
  #   maxCovidClose.append({"symbol": symbol, "maxClose": maxClose, "maxCloseDate": maxCloseDate.strftime("%Y-%m-%d")})

  # print(minCovidClose)
  # print(maxCovidClose)


if __name__ == "__main__":
    main(sys.argv[1:])
