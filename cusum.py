from detecta import detect_cusum
import numpy as np
import matplotlib.pyplot as plt
import sys
import math
from marketstack import getAvailableTickersFromMarketstack, getDailyDataFromMarketstack
from covid import getPostCovidMaxFromFile, getPostCovidMinFromFile
import pandas as pd


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

def analyseStocks(symbol, investAmount):
  df = getDailyDataFromMarketstack(symbol, '2020-07-01')

  if df.empty:
    return ('empty', symbol, 0, 0)
  
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
    return ('buy', symbol, lastClose, potentialRevenue)
  
  return ('pass', symbol, lastClose, potentialRevenue)

def analizeCovidContext(symbol, investAmount, lastClose):

  stocksToBuy = getAdjustedStocksToBuy(lastClose, investAmount)
  totalInvestCost = lastClose*stocksToBuy + transactionTax(investAmount)
  print("totalinvestcostCovid: ", totalInvestCost)

  covidMaxClose = getPostCovidMinFromFile(symbol)
  potentialStocksSold = covidMaxClose*stocksToBuy + transactionTax(investAmount)

  potentialRevenue = potentialStocksSold - totalInvestCost

  print("potentialRevenueCovid: ", potentialRevenue)

  if(int(potentialRevenue) > 40000):
    print("Comprar")
    return ('buy', symbol, potentialRevenue)
  
  return ('pass', symbol, potentialRevenue)


def main(argv):

  availableTickers = getAvailableTickersFromMarketstack()

  toBuy = {}
  toBuyCovid = {}
  investAmount = 500000

  for symbol in availableTickers:
    print("Analysing stock: ", symbol)
    (action, symbol, lastClose, revenue) = analyseStocks(symbol, investAmount)
    if(action == 'buy'):
      print("Adding to buy: ", symbol, revenue)
      toBuy[symbol] = revenue
    
    (action, symbol, revenue) = analizeCovidContext(symbol, investAmount, lastClose)
    if(action == 'buy'):
      print("Adding to buy covid: ", symbol, revenue)
      toBuyCovid[symbol] = revenue
  
  print(toBuy)
  print(">>>>>>>>>>>>>>>>>>>>>>>>>")
  print(toBuyCovid)

if __name__ == "__main__":
    main(sys.argv[1:])