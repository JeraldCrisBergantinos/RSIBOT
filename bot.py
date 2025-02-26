import websocket, json, pprint, talib, numpy
import config
from binance.client import Client
from binance.enums import *

SOCKET = "wss://stream.binance.com:9443/ws/ethusdt@kline_1m"
#SOCKET = "wss://stream.binance.com:9443/ws/ethusdt@kline_15m"

RSI_PERIOD = 14
RSI_OVERBOUGHT = 70
RSI_OVERSOLD = 30
TRADE_SYMBOL = 'ETHUSDT'
#TRADE_QUANTITY = 0.009

# 20 USD (2021-08-10)
TRADE_QUANTITY = 0.006

# 7 days
#TRADE_QUANTITY = 0.063

closes = []
in_position = False
total_profit = 0.0

#client = Client(config.API_KEY, config.API_SECRET, tld='us')
client = Client(config.API_KEY, config.API_SECRET)

def order(side, quantity, symbol, order_type=ORDER_TYPE_MARKET):
        try:
                print("sending order")
                order = client.create_test_order(symbol=symbol, side=side, type=order_type, quantity=quantity)
                #order = client.create_order(symbol=symbol, side=side, type=order_type, quantity=quantity)
                print(order)
        except Exception as e:
                print("An exception occurred - {}".format(e))
                return False

        return True

def on_open(ws):
    print('opened connection')

def on_close(ws):
    print('closed connection')

def on_message(ws, message):
    global closes, in_position, total_profit

    json_message = json.loads(message)
    #pprint.pprint(json_message)

    candle = json_message['k']

    is_candle_closed = candle['x']
    close = candle['c']

    if is_candle_closed:
        print("candle closed at {}".format(close))
        closes.append(float(close))
        print("closes")
        print(closes)
        print("Close Count:", len(closes), "RSI_PERIOD:", RSI_PERIOD)
        print("=== === ===")

        if len(closes) > RSI_PERIOD:
                print("computing rsis")
                np_closes = numpy.array(closes)
                rsi = talib.RSI(np_closes, RSI_PERIOD)
                print("all rsis calculated so far")
                print(rsi)
                last_rsi = rsi[-1]
                print("the last rsi is {}".format(last_rsi))

                if last_rsi > RSI_OVERBOUGHT:
                        if in_position:
                                print("Overbought! Sell! Sell! Sell!")
                                # put binance sell order logic here
                                # no more selling for this week
                                order_succeeded = order(SIDE_SELL, TRADE_QUANTITY, TRADE_SYMBOL)
                                if order_succeeded:
                                        in_position = False
                                        profit = float(close) * TRADE_QUANTITY
                                        total_profit = total_profit + profit
                        else:
                                print("It is overbought but we don't own any. Nothing to do.")

                if last_rsi < RSI_OVERSOLD:
                        if in_position:
                                print("It is oversold but you already own it, nothing to do.")
                        else:
                                print("Oversold! Buy! Buy! Buy!")
                                # put binance buy order logic here
                                order_succeeded = order(SIDE_BUY, TRADE_QUANTITY, TRADE_SYMBOL)
                                if order_succeeded:
                                        in_position = True
                                        profit = float(close) * TRADE_QUANTITY
                                        total_profit = total_profit - profit

        print("total profit:", total_profit)

ws = websocket.WebSocketApp(SOCKET, on_open=on_open, on_close=on_close, on_message=on_message)
ws.run_forever()