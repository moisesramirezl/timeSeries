from marketstack import getAvailableTickersFromMarketstack, getDailyDataFromMarketstack
import sys
import numpy as np


def getPostCovidMinMax(symbol):
  df = getDailyDataFromMarketstack(symbol, '2020-03-01', '2020-03-30')
  
  if df.empty:
    return (0,0)

  minClose = np.min(df['Close'])
  minCloseDate = df[df['Close'] == minClose]['Date']
  minCloseDate = minCloseDate[minCloseDate.index[0]]

  maxClose = np.max(df['Close'])
  maxCloseDate = df[df['Close'] == maxClose]['Date']
  maxCloseDate = maxCloseDate[maxCloseDate.index[0]]


  return (minClose, minCloseDate, maxClose, maxCloseDate)
 

def main(argv):
  availableTickers = getAvailableTickersFromMarketstack()

  (minCovidClose, maxCovidClose) = []

  for symbol in availableTickers:
    #print("Analysing stock: ", symbol)
    (minClose, minCloseDate, maxClose, maxCloseDate) = getPostCovidMinMax(symbol)
    #print(">>>>>>>>>> symbol: ", symbol, " ,minClose: ", minClose, " ,minCloseDate: ", minCloseDate, " ,maxClose: ", maxClose, " ,maxCloseDate: ", maxCloseDate)
    print(symbol, ",", minClose, ",", minCloseDate, ",", maxClose, ",", maxCloseDate)
    minCovidClose.append({"symbol": symbol, "minClose": minCloseDate, "minCloseDate": minCloseDate})
    maxCovidClose.append({"symbol": symbol, "maxClose": maxCloseDate, "maxCloseDate": maxCloseDate})
    print(minCovidClose)

if __name__ == "__main__":
    main(sys.argv[1:])
