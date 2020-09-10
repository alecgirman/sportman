import matplotlib.pyplot as plt
import sys, os
import requests
import pandas as pd
from datetime import datetime, timedelta

sys.path.append(os.path.realpath('.'))
from util import logger

def build_url(ticker: str, start: datetime, end: datetime,
              interval: str, include_prepost: bool):
    logger.trace(f'build_url()')
    base_url = f'https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?'

    # only verify 
    if not (interval[-1] in 'hmd'
            and interval[0].isnumeric()):
        print('Invalid interval format.')
        print('[0-9][hmd]')
        return None

    s = 'symbol=' + ticker + '&'
    a = 'period1=' + start.strftime('%s') + '&'
    b = 'period2=' + end.strftime('%s') + '&'
    c = 'interval=' + interval + '&'
    d = 'includePrePost=' + str(include_prepost).lower() + '&'
    e = 'events=div|split|earn&'
    f = 'lang=en-US'

    url =  base_url + s + a + b + c + d + e + f
    logger.debug(f'build_url: Returning url {url}')
    return url

def try_request(url):
    print(url)
    try:
        logger.debug(f'try_request: Trying HTTP get for url {url}')
        data = requests.get(url)
        return data
    except:
        logger.fatal(f'try_request: Exception occurred in requests.get()')

def get_raw_json(ticker: str, start: datetime, end: datetime,
              interval: str, include_prepost: bool):
    logger.trace(f'get_raw_json({ticker}, ...)')
    url = build_url(ticker, start, end, interval, include_prepost)
    req = try_request(url)
    return req.json()

def get_chart(ticker: str, start: datetime, end: datetime,
              interval: str, include_prepost: bool):
    logger.trace(f'get_chart({ticker}, ...)')
    json = get_raw_json(ticker, start, end, interval, include_prepost)
    return json['chart']['result'][0]

def build_simple_url(ticker):
    '''
    Builds a simple url for when start/end is not needed
    For example: retrieving the current price
    '''
    logger.trace(f'build_simple_url({ticker})')
    now = datetime.now()
    yst = now - timedelta(1)
    url = build_url(ticker, yst, now, '1m', True)
    logger.debug(f'build_simple_url: Return url: {url}')
    return url

def get_day_chart(ticker):
    logger.trace(f'get_day_chart({ticker})')
    req = try_request(build_simple_url(ticker))
    return req.json()['chart']['result'][0]

def get_stock_price(ticker):
    logger.trace(f'get_stock_price({ticker})')
    mktprice = get_day_chart(ticker)['meta']['regularMarketPrice']
    logger.debug(f'get_stock_price: Market price of {ticker} is {mktprice}')
    return mktprice
