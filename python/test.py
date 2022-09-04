from nsetools.nse import Nse
from stock_analyzer.driver import Driver
from nsetools.yahooFinance import YahooFinance as yf

nse = Nse()
dri = Driver()

print(dri.get_ticker_data(ticker='^NSEI', range="60d", interval="5m"))