from detecta import detect_cusum
import numpy as np
import matplotlib.pyplot as plt
import sys
import requests
import pandas as pd
import math

def getAvailableTickersFromMarketstack():
  params = {
    'access_key': '6149e9af91483588ecfb15ce01dd434d',
    'limit': '1000'
  }

  api_result = requests.get('http://api.marketstack.com/v1/exchanges/xsgo/tickers', params)
  api_response = api_result.json()

  availableTicker = []
  for tickers in api_response['data']['tickers']:
    print(tickers['has_eod'])
    if(tickers['has_eod']):
      print("Adding: ", tickers['symbol'])
      availableTicker.append(tickers['symbol'])

  return availableTicker
  
def getDailyDataFromMarketstack(symbol):
  params = {
    'access_key': '6149e9af91483588ecfb15ce01dd434d',
    'symbols': symbol,
    'sort': 'DESC',
    'date_from': '2020-07-01',
    'limit': '1000'
  }

  api_result = requests.get('http://api.marketstack.com/v1/eod', params)

  api_response = api_result.json()

  dataDict = api_response['data']

  if not dataDict:
    return pd.DataFrame()

  df = pd.DataFrame.from_dict(dataDict)
  df = df.reset_index()

  df = df.rename(index=str, columns={"date": "Date", "open": "Open",
                                        "high": "High", "low": "Low", "close": "Close"})
                                  
  df['Date'] = pd.to_datetime(df['Date'])
  df['Date'] = df['Date'].dt.tz_localize(None)

  df = df.sort_values(by=['Date'])

  #define as int cause does not matter decimal for CLP
  df.Open = df.Open.astype(int)
  df.Close = df.Close.astype(int)
  df.High = df.High.astype(int)
  df.Low = df.Low.astype(int)

  return df

def transactionTax(investAmount):
  return (3500+(investAmount*0.008))*1.19

def getLastFallDelta(dateValueList):
  dateValueList = dateValueList.sort_values(by=['Date'], ascending=False)
  i = 0
  delta = 0
  print(dateValueList, len(dateValueList))
  while  i < len(dateValueList) - 1:
    print(i, " -  i: ", dateValueList['Value'][i], "i+1: ", dateValueList['Value'][i+1])
    if(dateValueList['Value'][i] > dateValueList['Value'][i+1]):
      return delta * -1
    delta = dateValueList['Value'][i] - dateValueList['Value'][i+1]
    print( "delta: ", delta)
    i += 1
  return delta

def getAdjustedStocksToBuy(stockPrice, investAmount):
  if stockPrice > 0:
    stocksToBuy = math.floor(investAmount/stockPrice)
    print("stocksToBuy: ", stocksToBuy)
    return stocksToBuy
  return 0

def analyseStocks(symbol):
  df = getDailyDataFromMarketstack(symbol)

  if df.empty:
    return ('empty', symbol, 0)

  investAmount = 500000
  
  minClose = min(df['Close'])
  maxClose = max(df['Close'])
  lastClose = df['Close'][-1]
  difMinMax = maxClose - minClose

  dateValue = pd.DataFrame()
  dateValue['Date'] = df['Date']
  dateValue['Value'] = df['Close']

  lastFallDelta = getLastFallDelta(dateValue)

  print("minClose: ", minClose, " maxClose: ", maxClose, "lastClose: ", lastClose, " diffMinMax: ", difMinMax, ' lastFallDelta: ', lastFallDelta)

  ta, tai, taf, amp = detect_cusum(df['Close'], 200, .05, True, False)

  print(ta, tai, taf, amp)

  stocksToBuy = getAdjustedStocksToBuy(lastClose, investAmount)
  totalInvestCost = lastClose*stocksToBuy + transactionTax(investAmount)
  print("totalinvestcost: ", totalInvestCost)

  potentialStocksSold = maxClose*stocksToBuy + transactionTax(investAmount)

  potentialRevenue = potentialStocksSold - totalInvestCost

  print("potentialRevenue: ", potentialRevenue)

  if(int(potentialRevenue) > 40000):
    print("Comprar")
    return ('buy', symbol, potentialRevenue)
  
  return ('pass', symbol, potentialRevenue)

def main(argv):

  availableTickers = getAvailableTickersFromMarketstack()

  toBuy = {}
  for symbol in availableTickers:
    print("Analysing stock: ", symbol)
    (action, symbol, revenue) = analyseStocks(symbol)
    if(action == 'buy'):
      print("Adding to buy: ", symbol, revenue)
      toBuy[symbol] = revenue
  
  print(toBuy)


  

if __name__ == "__main__":
    main(sys.argv[1:])