#!/usr/bin/python3

import pandas as pd
import colored
from datetime import datetime as dt
import time
from sys import argv

# custom yahoo finance api module
# from core import yahoofinance as yf
from core import chart
from util import logger as log

# if the time is between 9:30am and 4:00pm
# TODO: check if its a weekend or market holiday
market_open = lambda: 570 <= dt.now().hour * 60 + dt.now().minute <= 960

def main():
    log.level_stdout = 0
    filename = ''
    use_color = False
    use_polybar = False
    use_unicode = False

    # enumerate through arguments
    for idx, arg in enumerate(argv):
        if arg in ['-f', '--file']:
            filename = argv[idx + 1]
        if arg in ['-c', '--color']:
            use_color = True
        if arg in ['-p', '--polybar']:
            use_polybar = True
        if arg in ['-u', '--unicode']:
            use_unicode = True

    
    log.debug(f'filename = {filename}')
    log.debug(f'use_color = {use_color}')
    log.debug(f'use_polybar = {use_polybar}')
    log.debug(f'use_unicode = {use_unicode}')

    # load portfolio and get current stock prices
    portfolio, metadata = load_portfolio(filename)
    # calculate the total buy value
    totalbuy = portfolio_buy_value(portfolio)
    # calculate current value (using live-ish stock prices)
    totalcurrent = portfolio_current_value(portfolio)
    # overall change = current price - buy price
    change = totalcurrent - totalbuy
    changep = (change / totalbuy) * 100

    # Unicode arrow symbols
    arrow = ('\uf431 ' if change > 0 else '\uf433 ') if use_unicode else ''
    # Three way ternary operator!  Credit: https://stackoverflow.com/a/14029300
    # stdout and polybar use different color formats, so these set the output format based
    # on which one is enabled.  If none are enabled, then dont use them.
    greenfg = colored.fg('green') if use_color else "%{F#98c379}" if use_polybar else ''
    redfg = colored.fg('red') if use_color else "%{F#e06c75}" if use_polybar else '' 
    reset = colored.attr('reset') if use_color else '%{F-}' if use_polybar else ''
    # use green for profit, red for loss
    outcolor = greenfg if change > 0 else redfg
    # add plus symbol if profit
    symbol = '+' if change > 0 else ''
    # if market is closed, add closed message
    closedmsg = f'({redfg}closed{reset})' if not market_open() else ''

    print(f'{outcolor}{arrow}{symbol}{change:.2f}{reset} ({outcolor}{symbol}{changep:.3f}%{reset}) {closedmsg}')
    

# a portfolio can contain the same ticker multiple times if it was purchased at different
# prices, but the live-ish price checker only needs to get it once, so to fix that, the
# tickers are kept in a set so that each one is only retrieved once
tickers = set()
# to store information outside of stock assets
metadata = {}

def update_tickers():
    """
    Gets the live price for each registered ticker

    Returns:
        dict: A dictionary where the key is the ticker and the value is the price
    """
    log.trace('update_tickers()')
    prices = {}
    # for each unique ticker
    for t in tickers:
        # get the stock price from yahoo finance
        prices[t] = chart.get_stock_price(t)

    return prices

def load_portfolio(filename):
    """
    Loads the portfolio file into `portfolio`

    Args:
        TODO: update this
        file (File): Portfolio file as a file object (return value of open())

    Returns:
        pd.DataFrame: Updated portfolio

    """

    log.trace('load_portfolio()')
    portfolio = pd.DataFrame(columns=['ticker', 'buy', 'shares', 'current'])
    metadata = {}
    metadata['cash'] = 0

    with open(filename, 'r') as file:
        for line in file.readlines():
            entry = line.split(' ')

            # store the portfolio buying power (non-stock assets)
            # used to measure total portfolio value
            if entry[0] == 'BUYPOWER':
                metadata['cash'] = float(entry[1])
                log.debug('loaded cash from portfolio')
            else:
                # load each stock from the portfolio file
                position = {}
                tickers.add(entry[0])
                position['ticker'] = entry[0]
                position['buy'] = float(entry[1])
                position['shares'] = int(entry[2])
                position['current'] = chart.get_stock_price(position['ticker'])
                portfolio = portfolio.append(position, ignore_index=True)
                log.debug(f'loaded {entry[0]} from portfolio')
        return portfolio, metadata

def portfolio_buy_value(portfolio):
    """
    Calculates the total buy value of the portfolio

    The buy value is equal to the combined cost of all stocks at the prices
    they were **purchased** at.  If multiple shares of the same stock were
    purchased at different prices, this lets the portfolio keep track of this.

    Args:
        portfolio(pd.DataFrame): Portfolio DataFrame

    Returns:
        float: The portfolio's total buy value
    """
    log.trace('portfolio_buy_value()')
    buyvalue = 0
    for idx, position in portfolio.iterrows():
        buyvalue += position['buy'] * position['shares']

    return buyvalue


def portfolio_current_value(portfolio):
    """
    Calculates the total current value of the portfolio

    The current value is equal to the combined cost of all stocks at the prices
    they are **currently** at.

    Args:
        portfolio(pd.DataFrame): Portfolio DataFrame

    Returns:
        float: The portfolio's total current value
    """
    log.trace('portfolio_current_value()')
    currvalue = 0
    for idx, position in portfolio.iterrows():
        currvalue += position['current'] * position['shares']

    return currvalue

def update_portfolio(portfolio):
    """
    Updates the current price values in the portfolio

    Args:
        portfolio (pd.DataFrame): Portfolio DataFrame

    Returns:
        pd.DataFrame: Updated portfolio
    """
    log.trace('update_portfolio()')
    # get the prices of all stock tickers
    prices = update_tickers()

    # for each position, set the variable of the current price
    for idx, position in portfolio.iterrows():
        portfolio.loc[idx, 'current'] = prices[position['ticker']]

if __name__ == "__main__":
    main()
