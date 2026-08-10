import os
from functools import wraps
from common.DatabaseManager import DatabaseManager
from trading.portfolio import Portfolio
from ingestion.indicators import analyze_stock
from trading.stock_client import StockTracker
from flask import Flask, jsonify, render_template, request, session
from werkzeug.security import check_password_hash, generate_password_hash
import threading
from ingestion.websocket_client import BinanceWebSocket
from ingestion.anomaly_detector import AnomalyDetector

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY")
if not app.secret_key:
    raise RuntimeError("FLASK_SECRET_KEY לא מוגדר (ראי .env.example)")

db = DatabaseManager()

def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            return jsonify({"error": "צריך להתחבר קודם"}), 401
        return f(*args, **kwargs)
    return wrapper


def current_portfolio():
    return Portfolio(session["user_id"])


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

@app.route('/trading/portfolio/value_history', methods=['GET'])
@login_required
def get_value_history():
    rows = db.get_portfolio_history(session["user_id"], limit=365)
    return jsonify(list(reversed(rows)))


@app.route('/trading/portfolio/trades', methods=['POST'])
@login_required
def make_a_trade():
    data = request.json or {}
    symbol = data.get('symbol')
    action = data.get('action')
    if not symbol or action not in ('buy', 'sell'):
        return jsonify({"error": "צריך symbol ו-action תקין (buy/sell)"}), 400
    try:
        amount = float(data.get('amount'))
    except (TypeError, ValueError):
        return jsonify({"error": "amount חייב להיות מספר"}), 400

    stock = StockTracker(symbol)
    try:
        price = stock.get_current_price()
    except Exception:
        return jsonify({"error": f"לא הצלחנו לקבל מחיר עבור {symbol}"}), 400

    portfolio = current_portfolio()
    if action == 'buy':
        worked = portfolio.buy_asset(symbol, price, amount)
    else:
        worked = portfolio.sell_asset(symbol, price, amount)

    if not worked:
        return jsonify({"worked": False, "error": "הפעולה נדחתה (יתרה/כמות לא מספיקה)"}), 400
    return jsonify({"worked": True})


@app.route('/trading/total_worth', methods=['GET'])
@login_required
def get_total_worth():
    portfolio = current_portfolio()
    stocks = {}
    for i in portfolio.assets.keys():
        stock = StockTracker(i)
        try:
            stocks[i] = stock.get_current_price()
        except Exception:
            stocks[i] = None
    return jsonify(portfolio.total_value_of_portfolio(stocks))

@app.route("/")
def index():
    return render_template("index.html")

@app.route('/trading/portfolio/balance', methods=['GET'])
@login_required
def get_balance():
    return jsonify({"balance": current_portfolio().balance})

@app.route('/trading/portfolio/holdings', methods=['GET'])
@login_required
def get_holdings():
    return jsonify(current_portfolio().assets)

@app.route('/trading/portfolio/history', methods=['GET'])
@login_required
def get_history():
    transactions = db.get_transactions(session["user_id"], limit=5)
    return jsonify(transactions)

@app.route('/login', methods=['POST'])
def login():
    data = request.json or {}
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"success": False, "error": "Username and password are required"}), 400

    user = db.get_user(username)
    if user and check_password_hash(user[2], password):
        session['user_id'] = user[0]
        session['username'] = user[1]
        return jsonify({"success": True})
    else:
        return jsonify({"success": False, "error": "Invalid username or password"}), 401

@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({"success": True})

@app.route('/register', methods=['POST'])
def register():
    data = request.json or {}
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"success": False, "error": "Username and password are required"}), 400

    existing_user = db.get_user(username)
    if existing_user:
        return jsonify({"success": False, "error": "Username already exists"}), 400

    hashed_password = generate_password_hash(password)
    db.add_user(username, hashed_password)
    return jsonify({"success": True})

def start_binance():
    detector = AnomalyDetector(2.0, 20)
    client = BinanceWebSocket("btcusdt", detector)
    client.start()

if __name__ == '__main__':
    threading.Thread(target=start_binance, daemon=True).start()
    debug = os.environ.get("FLASK_DEBUG", "false").lower() == "true"
    app.run(debug=debug, host="0.0.0.0", port=int(os.environ.get("PORT", "5000")), use_reloader=False)