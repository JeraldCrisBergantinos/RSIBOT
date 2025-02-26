import json
import threading
import websocket
import talib
import numpy as np
from binance.client import Client
from binance.enums import *

class RSITradingBot:
    """
    A trading bot that connects to Binance's WebSocket to monitor market data,
    compute the Relative Strength Index (RSI), and execute orders based on RSI thresholds.
    """
    def __init__(self, symbol, trade_quantity, api_key, api_secret,
                 rsi_period=14, overbought=70, oversold=30,
                 socket_url="wss://stream.binance.com:9443/ws/ethusdt@kline_1m"):
        self.symbol = symbol
        self.trade_quantity = trade_quantity
        self.rsi_period = rsi_period
        self.overbought = overbought
        self.oversold = oversold
        self.socket_url = socket_url

        # Initialize Binance client with API credentials
        self.client = Client(api_key, api_secret)

        # Data storage and state variables
        self.closes = []
        self.in_position = False
        self.total_profit = 0.0
        self.running = False

        # WebSocket object; will be created in start()
        self.ws = None

    def order(self, side, order_type=ORDER_TYPE_MARKET):
        """
        Place an order on Binance using the test order endpoint.
        In production, you would switch to create_order.
        """
        try:
            print(f"Sending {side} order for {self.trade_quantity} {self.symbol}")
            order = self.client.create_test_order(
                symbol=self.symbol,
                side=side,
                type=order_type,
                quantity=self.trade_quantity
            )
            print("Order response:", order)
            return True
        except Exception as e:
            print("Exception occurred during order:", e)
            return False

    def on_open(self, ws):
        """Callback when WebSocket connection is opened."""
        print("WebSocket connection opened.")

    def on_close(self, ws):
        """Callback when WebSocket connection is closed."""
        print("WebSocket connection closed.")

    def on_message(self, ws, message):
        """
        Callback for handling incoming WebSocket messages.
        Processes closed candle data, computes RSI, and executes trades.
        """
        json_message = json.loads(message)
        candle = json_message.get('k', {})

        is_candle_closed = candle.get('x', False)
        close = candle.get('c', None)

        if is_candle_closed and close is not None:
            close_price = float(close)
            print(f"Candle closed at {close_price}")
            self.closes.append(close_price)

            # Only compute RSI if we have enough data points
            if len(self.closes) > self.rsi_period:
                np_closes = np.array(self.closes)
                rsi = talib.RSI(np_closes, self.rsi_period)
                last_rsi = rsi[-1]
                print(f"Computed RSI: {last_rsi}")

                # Execute trading logic based on RSI thresholds
                if last_rsi > self.overbought:
                    if self.in_position:
                        print("RSI indicates overbought - executing SELL order.")
                        if self.order(SIDE_SELL):
                            self.in_position = False
                            profit = close_price * self.trade_quantity
                            self.total_profit += profit
                    else:
                        print("RSI overbought but no position held; no action taken.")
                elif last_rsi < self.oversold:
                    if not self.in_position:
                        print("RSI indicates oversold - executing BUY order.")
                        if self.order(SIDE_BUY):
                            self.in_position = True
                            profit = close_price * self.trade_quantity
                            self.total_profit -= profit
                    else:
                        print("RSI oversold but already in position; no action taken.")

            print(f"Total Profit: {self.total_profit}")

    def start(self):
        """
        Start the trading bot by opening a WebSocket connection in a separate thread.
        """
        self.running = True
        self.ws = websocket.WebSocketApp(
            self.socket_url,
            on_open=self.on_open,
            on_close=self.on_close,
            on_message=self.on_message
        )
        # Run the WebSocket in a separate thread to avoid blocking the main thread
        ws_thread = threading.Thread(target=self.ws.run_forever)
        ws_thread.daemon = True
        ws_thread.start()
        print("RSI Trading Bot started.")

    def stop(self):
        """Stop the trading bot and close the WebSocket connection."""
        if self.ws:
            self.ws.close()
        self.running = False
        print("RSI Trading Bot stopped.")

    def get_status(self):
        """
        Retrieve the current status of the bot including trading position,
        total profit, and data points collected.
        """
        return {
            "symbol": self.symbol,
            "in_position": self.in_position,
            "total_profit": self.total_profit,
            "data_points": len(self.closes)
        }
