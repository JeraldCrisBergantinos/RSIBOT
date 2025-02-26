from flask import Flask, jsonify, request, render_template
from rsi_trading_bot import RSITradingBot
import config  # Ensure this file contains your API_KEY and API_SECRET

app = Flask(__name__)

# Initialize the trading bot with appropriate configuration
bot = RSITradingBot(
    symbol='ETHUSDT',
    trade_quantity=0.006,
    api_key=config.API_KEY,
    api_secret=config.API_SECRET,
    rsi_period=14,
    overbought=70,
    oversold=30,
    socket_url="wss://stream.binance.com:9443/ws/ethusdt@kline_1m"
)

@app.route('/')
def dashboard():
    """
    Render the dashboard template showing the current status of the bot.
    """
    status = bot.get_status()
    return render_template('dashboard.html', status=status)

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

if __name__ == '__main__':
    # Run Flask app in debug mode for development
    app.run(debug=True)
