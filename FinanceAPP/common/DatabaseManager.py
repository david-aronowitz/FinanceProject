import sqlite3
from datetime import datetime

class DatabaseManager():
    def __init__(self):
        self.db_path = "FinanceAPP.db"
        self.con = sqlite3.connect(self.db_path)
        self.cur = self.con.cursor()
        self.init_db()

    def init_db(self):
        self.cur.execute(
            """
            SELECT name FROM sqlite_master WHERE type='table' AND name='anomalies';
        """
        )
        table_exists = self.cur.fetchone()
        if (not table_exists):
            self.cur.execute("CREATE TABLE anomalies(id INTEGER PRIMARY KEY AUTOINCREMENT, symbol, price, z_score, timestamp)")
            self.con.commit()

    def save_anomaly(self, symbol, price, z_score):
        timestamp = datetime.now().isoformat()
        self.cur.execute(
            "INSERT INTO anomalies VALUES ( ?, ?, ?, ?)",
            (symbol, price, z_score, timestamp)
        )
        self.con.commit()