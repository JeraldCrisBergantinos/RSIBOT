import os
from dotenv import load_dotenv
from flask import Flask, jsonify, request, render_template
from rsi_trading_bot import RSITradingBot

# Load environment variables from .env file
load_dotenv()
api_key = os.getenv("API_KEY")
api_secret = os.getenv("API_SECRET")

app = Flask(__name__)

# Initialize the trading bot using environment variables for secure API credentials
bot = RSITradingBot(
    symbol='ETHUSDT',
    trade_quantity=0.006,
    api_key=api_key,
    api_secret=api_secret,
    rsi_period=14,
    overbought=70,
    oversold=30,

    # 1 minute interval
    #socket_url="wss://stream.binance.com:9443/ws/ethusdt@kline_1m"

    # For checking and demo purposes, the interval is 1 second
    socket_url="wss://stream.binance.com:9443/ws/ethusdt@kline_1s"
)

@app.route('/')
def dashboard():
    """
    Render the dashboard template showing the current status of the bot and recent logs.
    """
    status = bot.get_status()
    logs = bot.get_logs(100)  # Get the last 100 log messages
    return render_template('dashboard.html', status=status, logs=logs)

@app.route('/start', methods=['POST'])
def start_bot():
    """
    API endpoint to start the trading bot.
    """
    if not bot.running:
        bot.start()
        return jsonify({"status": "Bot started"}), 200
    else:
        return jsonify({"status": "Bot is already running"}), 200

@app.route('/stop', methods=['POST'])
def stop_bot():
    """
    API endpoint to stop the trading bot.
    """
    if bot.running:
        bot.stop()
        return jsonify({"status": "Bot stopped"}), 200
    else:
        return jsonify({"status": "Bot is not running"}), 200

@app.route('/status', methods=['GET'])
def status():
    """
    API endpoint to return the current status of the bot.
    """
    return jsonify(bot.get_status()), 200

@app.route('/logs', methods=['GET'])
def logs():
    """
    #API endpoint to return the latest logs from the trading bot.
    API endpoint to return all logs from the trading bot.
    """
    #return jsonify(bot.get_logs(100)), 200
    return jsonify(bot.get_logs()), 200

if __name__ == '__main__':
    # Run Flask app in debug mode for development
    app.run(debug=True)
