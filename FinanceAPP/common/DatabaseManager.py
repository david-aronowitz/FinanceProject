import sqlite3
import datetime

class DatabaseManager():
    def __init__(self):
        self.db_path = "FinanceAPP.db"
        self.con = sqlite3.connect(self.db_path)
        self.cur = self.con.cursor()
        self.init_db()

    def init_db(self):
        pass

    def save_anomaly(self):
        pass
