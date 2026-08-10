from datetime import datetime
import psycopg2
import os

class DatabaseManager():
    def __init__(self):
        self.host = os.environ.get("DB_HOST")
        self.dbname = os.environ.get("DB_NAME", "postgres")
        self.user = os.environ.get("DB_USER", "postgres")
        self.password = os.environ.get("DB_PASS")
        self.port = os.environ.get("DB_PORT", "5432")
        if not self.host or not self.password:
            raise RuntimeError("DB_HOST ו-DB_PASS חייבים להיות מוגדרים (ראי .env.example)")
        self.init_db()

    def get_connection(self):
        return psycopg2.connect(
            host=self.host,
            dbname=self.dbname,
            user=self.user,
            password=self.password,
            port=self.port
        )

    def init_db(self):
        with self.get_connection() as con:
            with con.cursor() as cur:
                cur.execute("CREATE TABLE IF NOT EXISTS anomalies(id SERIAL PRIMARY KEY, symbol VARCHAR(20), price NUMERIC, z_score NUMERIC, timestamp TIMESTAMP)")
                cur.execute("CREATE TABLE IF NOT EXISTS ticks(id SERIAL PRIMARY KEY, symbol VARCHAR(20), price NUMERIC, timestamp TIMESTAMP)")
                cur.execute("CREATE TABLE IF NOT EXISTS transactions(id INT, action VARCHAR(10), symbol VARCHAR(20), price NUMERIC, amount NUMERIC, timestamp TIMESTAMP)")
                cur.execute("CREATE TABLE IF NOT EXISTS holdings(id INT, symbol VARCHAR(20), price NUMERIC, amount NUMERIC, PRIMARY KEY (id, symbol))")
                cur.execute("CREATE TABLE IF NOT EXISTS portfolio_value_history(id INT, value NUMERIC, timestamp TIMESTAMP)")
                cur.execute("CREATE TABLE IF NOT EXISTS users(id SERIAL PRIMARY KEY, name VARCHAR(50) UNIQUE, password TEXT, balance NUMERIC DEFAULT 1000000)")

    def save_anomaly(self, symbol, price, z_score):
        timestamp = datetime.now()
        with self.get_connection() as con:
            with con.cursor() as cur:
                cur.execute("INSERT INTO anomalies (symbol, price, z_score, timestamp) VALUES (%s, %s, %s, %s)", (symbol, price, z_score, timestamp))

    def save_tick(self, symbol, price):
        timestamp = datetime.now()
        with self.get_connection() as con:
            with con.cursor() as cur:
                cur.execute("INSERT INTO ticks (symbol, price, timestamp) VALUES (%s, %s, %s)", (symbol, price, timestamp))

    def save_transaction(self, id, action, symbol, price, amount):
        timestamp = datetime.now()
        with self.get_connection() as con:
            with con.cursor() as cur:
                cur.execute("INSERT INTO transactions (id, action, symbol, price, amount, timestamp) VALUES (%s, %s, %s, %s, %s, %s)", (id, action, symbol, price, amount, timestamp))

    def update_holding(self, id, symbol, price, amount):
        with self.get_connection() as con:
            with con.cursor() as cur:
                if amount <= 0:
                    cur.execute("DELETE FROM holdings WHERE id = %s AND symbol = %s", (id, symbol))
                else:
                    cur.execute("""
                        INSERT INTO holdings (id, symbol, price, amount)
                        VALUES (%s, %s, %s, %s)
                        ON CONFLICT (id, symbol)
                        DO UPDATE SET price = EXCLUDED.price, amount = EXCLUDED.amount
                    """, (id, symbol, price, amount))

    def add_user(self, name, password, initial_balance=1000000):
        with self.get_connection() as con:
            with con.cursor() as cur:
                cur.execute("INSERT INTO users (name, password, balance) VALUES (%s, %s, %s)", (name, password, initial_balance))

    def get_users(self):
        with self.get_connection() as con:
            with con.cursor() as cur:
                cur.execute("SELECT id, name, password, balance FROM users ORDER BY id DESC")
                return cur.fetchall()

    def get_user(self, name):
        with self.get_connection() as con:
            with con.cursor() as cur:
                cur.execute("SELECT id, name, password, balance FROM users WHERE name = %s", (name,))
                return cur.fetchone()

    def update_user_balance(self, id, new_balance):
        with self.get_connection() as con:
            with con.cursor() as cur:
                cur.execute("UPDATE users SET balance = %s WHERE id = %s", (new_balance, id))

    def get_anomalies(self, limit=10):
        with self.get_connection() as con:
            with con.cursor() as cur:
                cur.execute("SELECT symbol, price, z_score, timestamp FROM anomalies ORDER BY id DESC LIMIT %s", (limit,))
                return cur.fetchall()

    def get_ticks(self, symbol=None, limit=10):
        with self.get_connection() as con:
            with con.cursor() as cur:
                if symbol:
                    cur.execute("SELECT id, symbol, price, timestamp FROM ticks WHERE symbol = %s ORDER BY id DESC LIMIT %s", (symbol, limit))
                else:
                    cur.execute("SELECT id, symbol, price, timestamp FROM ticks ORDER BY id DESC LIMIT %s", (limit,))
                return cur.fetchall()

    def get_transactions(self, user_id, limit=100):
        # שינוי: מסננים לפי המשתמש. קודם הפונקציה החזירה את העסקאות של *כל* המשתמשים.
        with self.get_connection() as con:
            with con.cursor() as cur:
                cur.execute("SELECT action, symbol, price, amount FROM transactions WHERE id = %s ORDER BY timestamp DESC LIMIT %s", (user_id, limit))
                return cur.fetchall()

    def get_holdings(self, id=0):
        with self.get_connection() as con:
            with con.cursor() as cur:
                if id == 0:
                    cur.execute("SELECT id, symbol, price, amount FROM holdings")
                else:
                    cur.execute("SELECT id, symbol, price, amount FROM holdings WHERE id = %s", (id,))
                return cur.fetchall()

    def get_portfolio_history(self, id, limit=100):
        with self.get_connection() as con:
            with con.cursor() as cur:
                cur.execute("SELECT id, value, timestamp FROM portfolio_value_history WHERE id = %s ORDER BY timestamp DESC LIMIT %s", (id, limit))
                return cur.fetchall()