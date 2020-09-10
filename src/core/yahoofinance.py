import time
import sys, os
import requests
import bs4
import re

sys.path.append(os.path.realpath('.'))
from util import logger

get_stock_price = lambda t: get_current_stock_price(t)

result_cache = {}

def get_data_from_reactid(url, reactid):
    logger.trace(f'yahoofinance.get_data_from_reactid({url}, {reactid})')
    do_fetch = True

    # check if this url has already been downloaded
    if url in result_cache:
        logger.debug(f'url found in cache')
        # get cached result if it exists
        cache_entry = result_cache[url]

        # if cache entry is older than 10 seconds
        if time.time() - cache_entry['time'] < 10:
            # ...then dont download a new copy
            do_fetch = False
        else:
            logger.debug('cached url entry is too old')

    if do_fetch:
        # get page and init bs4
        page = requests.get(url)
        soup = bs4.BeautifulSoup(page.text, features='lxml')
        result_cache[url] = {'time': time.time(), 'data': soup}
        logger.debug(f'retrieved page and added to cache: {url}')

    else:
        soup = result_cache[url]['data']
        logger.debug(f'using from cache: {url}')

    # find all span tags
    spans = soup.findAll('span')

    # this better not change
    pricespan = [span for span in spans if f'data-reactid="{reactid}"' in str(span)]
    logger.debug(f'found {len(pricespan)} spans for reactid {reactid}')
    value_search = re.findall('\d+\.\d*', str(pricespan))[-1]
    return value_search

def get_current_stock_price(ticker):
    """
    Gets the stock price for a given ticker

    Args:
        ticker (str): The ticker to retrieve the price for

    Returns:
        float: The price of the given stock
    """
    logger.debug(f'yahoofinance.get_current_stock_price({ticker})')
    quote_url = 'https://finance.yahoo.com/quote/' + ticker
    return float(get_data_from_reactid(quote_url, 50))


def get_day_open(ticker):
    logger.debug(f'yahoofinance.get_day_open({ticker})')
    quote_url = 'https://finance.yahoo.com/quote/' + ticker
    return float(get_data_from_reactid(quote_url, 103))

def main():
    if len(sys.argv) > 1:
        try:
            ticker = sys.argv[1]
            print(f'Current: {get_stock_price(ticker)}')
            print(f'Open: {get_day_open(ticker)}')
        except IndexError:
            print('Error: Ticker does not exist.')
    else:
        print('Usage:')
        print('yahoofinance.py [TICKER]')


# if used as a command, use it to look up a stock price
if __name__ == "__main__":
    main()
