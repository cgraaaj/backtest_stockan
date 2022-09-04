from dataclasses import dataclass
import os
from time import sleep
import pandas as pd
import numpy as np
import datetime
from nsetools.nse import Nse
from stock_analyzer.driver import Driver
from nsetools.yahooFinance import YahooFinance as yf
import math

nse = Nse()
dri = Driver()
dt = datetime.datetime
weekno = dt.today().weekday()

# l = [{'a': 123,'c':123}, {'b': 123}, {'a': 123,'c':123}]
# l = [dict(t) for t in {tuple(d.items()) for d in l}]
# d=dri.get_ticker_data(interval='15m',range='1d',ticker='CUB.ns')
# print((datetime_object + datetime.timedelta(days=3)).strftime("%d-%m-%Y"))

risk = 1
reward = 2
p=10000
amount = p


def calcPL(dayData):
    # print(dayData)
    boughtAt = dayData["Open"].iloc[0]
    sl = boughtAt - (boughtAt * (0.01 * risk))
    target = boughtAt + (boughtAt * (0.01 * reward))
    soldAtRow = dayData[(dayData['Close']> target) | (dayData['Close'] <sl)].iloc[1]
    # soldAt = next(
    #     (
    #         cp
    #         for cp in dayData["Close"].tolist()
    #         if cp > target or cp < sl
    #     ),
    #     dayData["Close"].iloc[-1],
    # )
    soldAt = soldAtRow['Close']
    soldOn = soldAtRow.name
    
    # print(dayData)
    print(f'stoploss {sl},target {target}')
    print(f'Bought at {boughtAt}')
    print(f'Sold on {soldOn} at {soldAt}')

    pl = ((soldAt - boughtAt) * (math.floor(amount / boughtAt))) * 5
    return pl


def getPLfortheDay(date, stock):
    global amount
    # date = date + ' 10:00:00'
    # datetime_object = dt.strptime(date, "%a %b %d %Y %X")
    datetime_object = dt.strptime(date, "%a %b %d %Y")
    monthDatadf = dri.get_ticker_data(interval="5m", range="60d", ticker=stock + ".NS")
    dayData = []
    # print(monthDatadf)
    try:
        if datetime_object.weekday() == 4:
                dayData = monthDatadf[
                    (monthDatadf.index > datetime_object + datetime.timedelta(days=3))
                    & (monthDatadf.index < datetime_object + datetime.timedelta(days=4))
                ]
                amount = amount + calcPL(dayData)
        else:
                dayData = monthDatadf[
                    (monthDatadf.index > datetime_object + datetime.timedelta(days=1))
                    & (monthDatadf.index < datetime_object + datetime.timedelta(days=2))
                ]
                amount = amount + calcPL(dayData)
    except Exception as ex:
        print(f"---- Exception ***{ex}*** occured for {stock} ----")
        # print(dayData)


os.chdir(os.path.dirname(__file__))

df = pd.read_csv("lastmonth.csv")
for index, row in df.iterrows():
    if index >= 0 :
        # sleep(3)
        print(f'calclulating for stock {row["stock"]}, index is {index}')
        getPLfortheDay(row["date"], row["stock"])
        print(amount)
print(f'Final PL for the principal amount {amount} is {amount-p} which is {((amount-p)/p)*100}%')
# getPLfortheDay()
