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
from fyers_api import fyersModel
import json
import os
from os.path import join, dirname
from dotenv import load_dotenv

dotenv_path = join(dirname(__file__), ".env")
load_dotenv(dotenv_path)

APP_ID = os.environ.get("APP_ID")
ACCESS_TOKEN = os.environ.get("ACCESS_TOKEN")

nse = Nse()
dri = Driver()
dt = datetime.datetime
weekno = dt.today().weekday()

# l = [{'a': 123,'c':123}, {'b': 123}, {'a': 123,'c':123}]
# l = [dict(t) for t in {tuple(d.items()) for d in l}]
# d=dri.get_ticker_data(interval='15m',range='1d',ticker='CUB.ns')
# print((datetime_object + datetime.timedelta(days=3)).strftime("%d-%m-%Y"))

risk = 0.5
reward = 2
p = 10000
amount = p
IB = 7


def calcPL(dayData):
    # print(dayData)
    boughtAt = dayData["Open"].iloc[IB]
    sl = boughtAt - (boughtAt * (0.01 * risk))
    target = boughtAt + (boughtAt * (0.01 * reward))
    dayData = dayData[IB + 1 :]
    # print(dayData[(dayData["Close"] > target) | (dayData["Close"] < sl)])
    # reduce first row inorder to prevent same candle sell
    soldAtRow = (
        dayData[(dayData["Close"] > target) | (dayData["Close"] < sl)].iloc[0]
        if not dayData[(dayData["Close"] > target) | (dayData["Close"] < sl)].empty
        else dayData.iloc[-2]
    )
    soldAt = soldAtRow["Close"]
    soldOn = soldAtRow.name

    # print(dayData)
    print(f"stoploss {sl},target {target}")
    print(f"Bought at {boughtAt}")
    print(f"Sold on {soldOn} at {soldAt}")

    pl = ((soldAt - boughtAt) * (math.floor(amount / boughtAt))) * 5
    print(f"P or L for the day is {pl}")
    return pl


def api_call(symbol, date, isFriday, access_token, appId, log_path):
    functionName = "api_call"
    """
        :param access_token: "https://XXXXXX.com"
        :param app_id: "XXXXXXXXXXX"
        :param log_path: "home/gfxcgv/vgghvb/xxxx"
    """

    # If you want to make asynchronous API calls then assign the below variable as True and then pass it in the functions, by default its value is False
    is_async = False

    # Creating an instance of fyers model in order to call the apis
    fyers = fyersModel.FyersModel(
        token=access_token, is_async=is_async, log_path=log_path, client_id=appId
    )

    # Setting the AccessToken
    fyers.token = access_token

    ## uncomment the any of the following requests to send a particular request and get the required data
    datetime_object = dt.strptime(date, "%a %b %d %Y")
    fromDate = ""
    toDate = ""
    if isFriday:
        fromDate = (datetime_object + datetime.timedelta(days=3)).strftime("%Y-%m-%d")
        toDate = (datetime_object + datetime.timedelta(days=3)).strftime("%Y-%m-%d")
    else:
        fromDate = (datetime_object + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
        toDate = (datetime_object + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
    data = {
        "symbol": symbol,
        "resolution": "15",
        "date_format": "1",
        "range_from": fromDate,
        "range_to": toDate,
        "cont_flag": "1",
    }
    res = fyers.history(data)
    if res["candles"] != []:
        jdata = json.dumps(res)
        loader = json.loads(jdata)
        data = np.array(loader["candles"])
        data = np.concatenate([[["", "Open", "High", "Low", "Close", "Volume"]], data])
        df = pd.DataFrame(data=data[1:, 1:], index=data[1:, 0], columns=data[0, 1:])
        df = df.applymap(lambda x: float(x))
        df.index = [datetime.datetime.fromtimestamp(int(float(x))) for x in df.index]
        # print(df)
        return df
    return None
    # print(fyers.get_profile())
    # print(fyers.tradebook())
    # print(fyers.positions())
    # print(fyers.holdings())
    # print(fyers.convert_position({"symbol":"MCX:SILVERMIC20AUGFUT","positionSide":"1","convertQty":"1","convertFrom":"MARGIN","convertTo":"INTRADAY"}))
    # print(fyers.funds())
    # print(fyers.orderbook())
    # print(fyers.cancel_order({'id':'8080582117761'}))
    # print(fyers.place_order({"symbol":"MCX:SILVERMIC20AUGFUT","qty":"1","type":"1","side":"1","productType":"INTRADAY","limitPrice":"76700","stopPrice":"0","disclosedQty":"0","validity":"DAY","offlineOrder":"False","stopLoss":"0","takeProfit":"0"}))
    # print(fyers.modify_order({"id":"808058117761", "qty":"0","type":"1","limitPrice":"71100","stopPrice":"0"})) #modify instead of update
    # print(fyers.minquantity())
    # print(fyers.get_orders({'id':'808078094451'}))
    # print(fyers.market_status())
    # print(fyers.exit_positions({"id":"MCX:SILVERMIC20AUGFUT-MARGIN"}))
    # print(fyers.generate_data_token({"vendorApp":"0KMS0EZVXI"}))
    # print(fyers.cancel_basket_orders([{"id":"120080780536"},{"id":"120080777069"}]))
    # print(fyers.place_basket_orders([{"symbol":"NSE:SBIN-EQ","qty":"1","type":"1","side":"1","productType":"INTRADAY","limitPrice":"191","stopPrice":"0","disclosedQty":"0","validity":"DAY","offlineOrder":"False","stopLoss":"0","takeProfit":"0"},{"symbol":"NSE:SBIN-EQ","qty":"1","type":"1","side":"1","productType":"INTRADAY","limitPrice":"191","stopPrice":"0","disclosedQty":"0","validity":"DAY","offlineOrder":"False","stopLoss":"0","takeProfit":"0"}]))
    # print(fyers.modify_basket_orders([{"id":"120080780536", "type":1, "limitPrice": 190, "stopPrice":0},{"id":"120080777069", "type":1, "limitPrice": 190}]))


def isPositiveTrend(data):
    # print(dayData)
    if data is None:
        return False
    atNine15 = data["Open"].iloc[0]
    atEleven = data["Close"].iloc[IB]
    return atEleven - atNine15 > 0


positive = []
negative = []


def getPLfortheDay(date, stock):
    global amount
    # date = date + ' 10:00:00'
    # datetime_object = dt.strptime(date, "%a %b %d %Y %X")
    datetime_object = dt.strptime(date, "%a %b %d %Y")
    dayData = []
    access_token = ACCESS_TOKEN

    # The app id we get after creating the app
    appId = APP_ID

    # The system path where we want to store the logs e.g-c:\user\vvvv\xxxx\nnnn
    log_path = r"/home/cgraaaj/Desktop/PROJECTS/EODA1/python"
    symbol = "NSE:NIFTY50-INDEX"
    if datetime_object.weekday() == 4:
        nifty50Data = api_call(symbol, date, True, access_token, appId, log_path)
    else:
        nifty50Data = api_call(symbol, date, False, access_token, appId, log_path)
    if isPositiveTrend(nifty50Data):
        pl = 0
        try:
            symbol = f"NSE:{stock}-EQ"
            if datetime_object.weekday() == 4:
                dayData = api_call(symbol, date, True, access_token, appId, log_path)
                pl = calcPL(dayData)
            else:
                dayData = api_call(symbol, date, False, access_token, appId, log_path)
                pl = calcPL(dayData)
        except Exception as ex:
            print(f"---- Exception ***{ex}*** occured for {stock} ----")
            # print(dayData)
        if pl > 0:
            positive.append({"name": stock, "pl": pl})
        else:
            negative.append({"name": stock, "pl": pl})
        amount = amount + pl
    else:
        print(f"********Skipped for the stock {stock} as trend is Negative**********")


os.chdir(os.path.dirname(__file__))


df = pd.read_csv("lastmonth.csv")
for index, row in df.iterrows():
    if index >= 0:
        # sleep(3)
        print(f'calclulating for stock {row["stock"]}, index is {index}')
        getPLfortheDay(row["date"], row["stock"])
        print(f"EOD capital is {amount}")
print(
    f"Final PL for the principal amount {amount} is {amount-p} which is {((amount-p)/p)*100}%"
)
print(positive)
print(negative)
# getPLfortheDay()
