import time
from common.DatabaseManager import DatabaseManager
from ingestion.anomaly_detector import AnomalyDetector
import websocket
import json

class BinanceWebSocket():
    def __init__(self, symbol, detector):
        self.detector = detector
        self.symbol = symbol
        self.db = DatabaseManager()
        self.url = f"wss://stream.binance.com:9443/ws/{self.symbol.lower()}@ticker"

    def on_message(self, ws, message):
        try:
            data = json.loads(message)
            price = float(data['c'])
        except (ValueError, KeyError):
            return
        is_anomaly, z_score = self.detector.process_price(price)
        self.db.save_tick(self.symbol,price)
        if (is_anomaly):
            self.db.save_anomaly(self.symbol, price, z_score)
            #print(f"ANOMALY DETECTED! Price: {price}, Z-Score: {z_score}")

    def start(self):
        ws_app = websocket.WebSocketApp(self.url, on_message=self.on_message)
        while True:
            try:
                ws_app.run_forever()
            except Exception:  # שינוי: except Exception במקום except חשוף (שבלע גם Ctrl+C)
                time.sleep(10)


if (__name__ == "__main__"):
    detector = AnomalyDetector(2.0, 20)
    client = BinanceWebSocket("btcusdt",detector)
    client.start()