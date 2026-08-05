from datetime import datetime
import sqlite3
import os

class DatabaseManager():
    def __init__(self):
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        self.db_path = os.path.join(BASE_DIR, "FinanceAPP.db")
        self.init_db()

    def init_db(self):
        with sqlite3.connect(self.db_path) as con:
            cur = con.cursor()
            cur.execute("CREATE TABLE IF NOT EXISTS anomalies(id INTEGER PRIMARY KEY AUTOINCREMENT, symbol, price, z_score, timestamp)")
            cur.execute("CREATE TABLE IF NOT EXISTS ticks(id INTEGER PRIMARY KEY AUTOINCREMENT, symbol, price, timestamp)")
            cur.execute("CREATE TABLE IF NOT EXISTS transactions(id , action, symbol, price, amount, timestamp)")
            cur.execute("CREATE TABLE IF NOT EXISTS holdings(id, symbol UNIQUE, price, amount)")
            cur.execute("CREATE TABLE IF NOT EXISTS portfolio_value_history(id , value, timestamp)")

            cur.execute("CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE, password TEXT)")

    def save_anomaly(self, symbol, price, z_score):
        timestamp = datetime.now().isoformat()
        with sqlite3.connect(self.db_path) as con:
            cur = con.cursor()
            cur.execute("INSERT INTO anomalies (symbol, price, z_score, timestamp) VALUES (?, ?, ?, ?)",(symbol, price, z_score, timestamp))

    def save_tick(self, symbol, price):
        timestamp = datetime.now().isoformat()
        with sqlite3.connect(self.db_path) as con:
            cur = con.cursor()
            cur.execute("INSERT INTO ticks (symbol, price, timestamp) VALUES (?, ?, ?)",(symbol, price, timestamp))

    def save_transaction(self,id, action, symbol,price, amount):
        timestamp = datetime.now().isoformat()
        with sqlite3.connect(self.db_path) as con:
            cur = con.cursor()
            cur.execute("INSERT INTO transactions (id, action, symbol, price, amount, timestamp) VALUES (?, ?, ?, ?, ?, ?)", (id, action, symbol, price, amount, timestamp))

    def update_holding(self, symbol , price, amount):
        with sqlite3.connect(self.db_path) as con:
            cur = con.cursor()
            if amount <= 0:
                cur.execute("DELETE FROM holdings WHERE symbol = ?", (symbol,))
            else:
                cur.execute("""
                    INSERT INTO holdings (symbol, price, amount) 
                    VALUES (?, ?, ?)
                    ON CONFLICT(symbol) DO UPDATE SET price = excluded.price, amount = excluded.amount
                """, (symbol, price, amount))

    def add_user(self,name,password):
        with sqlite3.connect(self.db_path) as con:
            cur = con.cursor()
            cur.execute("INSERT INTO users (name,password) VALUES (?,?)", (name,password))

    def get_users(self):
        with sqlite3.connect(self.db_path) as con:
            cur = con.cursor()
            cur.execute("SELECT id, name, password, amount FROM users ORDER BY id DESC")
            return cur.fetchall()

    def get_user(self, name):
        with sqlite3.connect(self.db_path) as con:
            cur = con.cursor()
            cur.execute("SELECT id, name, password FROM users WHERE name = ?", (name,))
            return cur.fetchone()

    def get_anomalies(self, limit=10):
        with sqlite3.connect(self.db_path) as con:
            cur = con.cursor()
            cur.execute("SELECT symbol, price, z_score, timestamp FROM anomalies ORDER BY id DESC LIMIT ?", (limit,))
            return cur.fetchall()

    def get_ticks(self, symbol=None, limit=10):
        with sqlite3.connect(self.db_path) as con:
            cur = con.cursor()
            if symbol:
                cur.execute("SELECT id, symbol, price, timestamp FROM ticks WHERE symbol = ? ORDER BY id DESC LIMIT ?",
                            (symbol, limit))
            else:
                cur.execute("SELECT id, symbol, price, timestamp FROM ticks ORDER BY id DESC LIMIT ?", (limit,))
            return cur.fetchall()

    def get_transactions(self, limit=100):
        with sqlite3.connect(self.db_path) as con:
            cur = con.cursor()
            cur.execute(
                "SELECT action, symbol, price, amount FROM transactions ORDER BY timestamp DESC LIMIT ?",
                (limit,))
            return cur.fetchall()

    def get_holdings(self, id=0):
        with sqlite3.connect(self.db_path) as con:
            cur = con.cursor()
            if (id == 0):
                cur.execute("SELECT id, symbol, price, amount FROM holdings")
            else:
                cur.execute("SELECT id, symbol, price, amount FROM holdings WHERE id = ?",(id,))
            return cur.fetchall()

    def get_portfolio_history(self, limit=100):
        with sqlite3.connect(self.db_path) as con:
            cur = con.cursor()
            cur.execute("SELECT id, value, timestamp FROM portfolio_value_history ORDER BY id DESC LIMIT ?", (limit,))
            return cur.fetchall()
