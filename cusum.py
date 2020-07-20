from detecta import detect_cusum
import numpy as np
import matplotlib.pyplot as plt
import sys
import math
from marketstack import getAvailableTickersFromMarketstack, getDailyDataFromMarketstack
from covid import getPostCovidMaxFromFile, getPostCovidMinFromFile
import pandas as pd
import logging

def transactionTax(investAmount):
  return (3500+(investAmount*0.008))*1.19

def getLastFallDelta(dateValueList):
  dateValueList = dateValueList.sort_values(by=['Date'], ascending=False)
  i = 0
  delta = 0
  logging.debug(dateValueList)
  while  i < len(dateValueList) - 1:
    #logging.debug(i, " -  i: ", dateValueList['Value'][i], "i+1: ", dateValueList['Value'][i+1])
    if(dateValueList['Value'][i] > dateValueList['Value'][i+1]):
      return delta * -1
    delta = dateValueList['Value'][i] - dateValueList['Value'][i+1]
    logging.debug( "delta: %s", delta)
    i += 1
  return delta

def getAdjustedStocksToBuy(stockPrice, investAmount):
  if stockPrice > 0:
    stocksToBuy = math.floor(investAmount/stockPrice)
    logging.debug("stocksToBuy: %s", stocksToBuy)
    return stocksToBuy
  return 0

def analyseStocks(symbol, investAmount, thresholdMargin=50000):
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

  #logging.debug("minClose: ", minClose, " maxClose: ", maxClose, "lastClose: ", lastClose, " diffMinMax: ", difMinMax, ' lastFallDelta: ', lastFallDelta)

  ta, tai, taf, amp = detect_cusum(df['Close'], 200, .05, True, False)

  #logging.debug(ta, tai, taf, amp)

  stocksToBuy = getAdjustedStocksToBuy(lastClose, investAmount)
  totalInvestCost = lastClose*stocksToBuy + transactionTax(investAmount)
  
  logging.debug("totalinvestcost: %s", totalInvestCost)
  potentialStocksSold = maxClose*stocksToBuy + transactionTax(investAmount)
  potentialRevenue = potentialStocksSold - totalInvestCost

  logging.info("potentialRevenue last fall: %s", potentialRevenue)

  if(int(potentialRevenue) > thresholdMargin):
    logging.debug("Comprar")
    return ('buy', symbol, lastClose, potentialRevenue)
  
  return ('pass', symbol, lastClose, potentialRevenue)

def analizeCovidContext(symbol, investAmount, lastClose, thresholdMargin=50000):

  stocksToBuy = getAdjustedStocksToBuy(lastClose, investAmount)
  totalInvestCost = lastClose*stocksToBuy + transactionTax(investAmount)

  logging.debug("totalinvestcostCovid: %s", totalInvestCost)

  covidMaxClose = getPostCovidMaxFromFile(symbol)
  potentialStocksSold = covidMaxClose*stocksToBuy + transactionTax(investAmount)
  potentialRevenue = potentialStocksSold - totalInvestCost

  logging.info("potentialRevenueCovid: %s", potentialRevenue)

  if(int(potentialRevenue) > thresholdMargin):
    logging.info("Comprar")
    return ('buy', symbol, potentialRevenue)
  
  return ('pass', symbol, potentialRevenue)


def main(argv):
  logging.basicConfig(level=logging.INFO)

  logging.info('Starting analysis')

  availableTickers = getAvailableTickersFromMarketstack()

  toBuy = {}
  toBuyCovid = {}
  investAmount = 500000
  thresholdMargin = 50000

  for symbol in availableTickers:
    logging.info("Analysing stock: %s", symbol)
    
    (action, symbol, lastClose, revenue) = analyseStocks(symbol, investAmount, thresholdMargin)
    if(action == 'buy'):
      logging.info("Adding to buy: %s - %s", symbol, revenue)
      toBuy[symbol] = revenue
    
    (action, symbol, revenue) = analizeCovidContext(symbol, investAmount, lastClose, thresholdMargin)
    if(action == 'buy'):
      logging.info("Adding to buy covid: %s - %s", symbol, revenue)
      toBuyCovid[symbol] = revenue
  
  logging.info(toBuy)
  logging.info(">>>>>>>>>>>>>>>>>>>>>>>>>")
  logging.info(toBuyCovid)

if __name__ == "__main__":
    main(sys.argv[1:])