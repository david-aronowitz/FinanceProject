from common.DatabaseManager import DatabaseManager
from trading.portfolio import Portfolio
from ingestion.indicators import analyze_stock
from trading.stock_client import StockTracker
from flask import Flask, jsonify, render_template, request
import json

app = Flask(__name__)
db = DatabaseManager()
current_Portfolio = Portfolio()

@app.route('/trading/health', methods=['GET'])
def health_check():
    return jsonify({"status": "ok"})

@app.route('/trading/anomalies', methods=['GET'])
def get_anomalies():
    anomalies_list = db.get_anomalies()
    return jsonify(anomalies_list)

@app.route("/trading/ticks/latest", methods=['GET'])
def get_ticks():
    return jsonify(db.get_ticks("btcusdt"))


@app.route('/trading/stock/analyze', methods=['POST'])
def analyze_stock_route():
    data = request.get_json() or {}
    symbol = data.get('symbol')

    print(f"--> Request received for symbol: {symbol}")
    result = analyze_stock(symbol)
    print(f"--> analyze_stock returned: {result} (Type: {type(result)})")

    # מקרה 1: הפונקציה החזירה tuple מסוג (dict, status_code)
    if isinstance(result, tuple):
        res_data, status_code = result
        return jsonify(res_data), status_code

    # מקרה 2: הפונקציה החזירה dict בלבד
    if isinstance(result, dict):
        return jsonify(result), 200

    # מקרה 3: הפונקציה החזירה None
    return jsonify({"error": f"לא התקבלו נתונים עבור הסימול '{symbol}'"}), 500

@app.route('/trading/portfolio/trades', methods=['POST'])
def make_a_trade():
    data = request.json
    symbol = data.get('symbol')
    action = data.get('action')
    amount = float(data.get('amount'))
    stock = StockTracker(symbol)
    price = stock.get_current_price()
    if action == 'buy':
        work = current_Portfolio.buy_asset(symbol, price, amount)
    else:
        work = current_Portfolio.sell_asset(symbol, price, amount)
    return jsonify({"worked: ": work})


@app.route('/trading/total_worth', methods=['GET'])
def get_total_worth():
    stocks = {}
    for i in current_Portfolio.assets.keys():
        stock = StockTracker(i)
        stocks[i] = stock.get_current_price()
    return jsonify(current_Portfolio.total_value_of_portfolio(stocks))

@app.route("/")
def index():
    return render_template("index.html")

@app.route('/trading/portfolio/balance', methods=['GET'])
def get_balance():
    return jsonify({"balance": current_Portfolio.balance})

@app.route('/trading/portfolio/holdings', methods=['GET'])
def get_holdings():
    return jsonify(current_Portfolio.assets)

@app.route('/trading/portfolio/history', methods=['GET'])
def get_history():
    transactions = db.get_transactions(limit=5)
    return jsonify(transactions)

if __name__ == '__main__':
    app.run(debug=True, port=5000)