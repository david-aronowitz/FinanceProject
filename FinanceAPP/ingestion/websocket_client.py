from common.DatabaseManager import DatabaseManager
from anomaly_detector import AnomalyDetector
import websocket
import json

class BiananceWebSocket():
    def __init__(self, symbol, detector):
        self.detector = detector
        self.symbol = symbol
        self.manager = DatabaseManager()
        self.url = f"wss://stream.binance.com:9443/ws/{self.symbol.lower()}@ticker"

    def on_message(self, ws, message):
        data = json.loads(message)
        price = float(data['c'])
        is_anomaly, z_score = self.detector.process_price(price)
        if (is_anomaly):
            self.manager.save_anomaly(self.symbol, price, z_score)
            print(f"ANOMALY DETECTED! Price: {price}, Z-Score: {z_score}")

    def start(self):
        ws_app = websocket.WebSocketApp(self.url, on_message=self.on_message)
        ws_app.run_forever()


if (__name__ == "__main__"):
    detector = AnomalyDetector(2.0, 20)
    client = BiananceWebSocket("btcusdt",detector)
    client.start()