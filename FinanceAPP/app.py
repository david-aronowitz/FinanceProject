from common.DatabaseManager import DatabaseManager
from trading.portfolio import Portfolio
from ingestion.indicators import analyze_stock
from trading.stock_client import StockTracker
from flask import Flask, jsonify, render_template, request
from werkzeug.security import check_password_hash, generate_password_hash
import json

app = Flask(__name__)
app.secret_key = 'my_super_secret_development_key'
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
    data = request.json or {}
    symbol = data.get('symbol')
    if not symbol:
        return jsonify({"error": "יש לספק symbol"}), 400

    result = analyze_stock(symbol)
    if "error" in result:
        return jsonify(result), 400
    return jsonify(result)

@app.route('/trading/portfolio/trades', methods=['POST'])
def make_a_trade():
    data = request.json
    symbol = data.get('symbol')
    action = data.get('action')
    amount = float(data.get('amount'))
    print("received:", repr(symbol))
    print(request.json)
    stock = StockTracker(symbol)
    price = stock.get_current_price()
    print("get to action")
    if action == 'buy':
        print("buying")
        work = current_Portfolio.buy_asset(symbol, price, amount)
    else:
        print("selling")
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

@app.route('/login', methods=['POST'])
def login():
    global current_Portfolio
    data = request.json or {}
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"success": False, "error": "יש לספק שם משתמש וסיסמה"}), 400

    user = db.get_user(username)
    if user and check_password_hash(user['password'], password):
        current_Portfolio = Portfolio(user['id'])
        return jsonify({"success": True})
    else:
        return jsonify({"success": False, "error": "שם משתמש או סיסמה שגויים"}), 401

@app.route('/register', methods=['POST'])
def register():
    data = request.json or {}
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"success": False, "error": "יש לספק שם משתמש וסיסמה"}), 400

    existing_user = db.get_user(username)
    if existing_user:
        return jsonify({"success": False, "error": "שם המשתמש כבר קיים"}), 400

    hashed_password = generate_password_hash(password)
    db.add_user(username, hashed_password)
    return jsonify({"success": True})

if __name__ == '__main__':
    app.run(debug=True, port=5000)