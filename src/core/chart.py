import matplotlib.pyplot as plt
import sys
import requests
import pandas as pd
from datetime import datetime, timedelta


def build_url(ticker: str, start: datetime, end: datetime,
              interval: str, include_prepost: bool):
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

    return base_url + s + a + b + c + d + e + f

def get_chart(ticker: str, start: datetime, end: datetime,
              interval: str, include_prepost: bool):
    url = build_url(ticker, start, end, interval, include_prepost)
    req = requests.get(url)
    return req.json()['chart']['result'][0]

def get_day_chart(ticker):
    now = datetime.now()
    yst = now - timedelta(1)
    url = build_url(ticker, yst, now, '1m', True)
    req = requests.get(url)
    return req.json()['chart']['result'][0]

print(get_day_chart('AMD'))
