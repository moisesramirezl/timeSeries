import requests
import pandas as pd


def getAvailableTickersFromMarketstack():
  params = {
    'access_key': 'c130f968b5793fb9767f9c8625253b71',
    'limit': '1000'
  }

  api_result = requests.get('http://api.marketstack.com/v1/exchanges/xsgo/tickers', params)
  api_response = api_result.json()

  availableTicker = []
  for tickers in api_response['data']['tickers']:
    #print(tickers['has_eod'])
    if(tickers['has_eod']):
      #print("Adding: ", tickers['symbol'])
      availableTicker.append(tickers['symbol'])

  return availableTicker
  
def getDailyDataFromMarketstack(symbol, dateFrom, dateTo=''):
  params = {
    'access_key': 'c130f968b5793fb9767f9c8625253b71',
    'symbols': symbol,
    'sort': 'DESC',
    'date_from': dateFrom,
    'date_to': dateTo,
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
