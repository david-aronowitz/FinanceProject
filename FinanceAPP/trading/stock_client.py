import yfinance as yf

class StockTracker():
    def __init__(self, symbol):
        self.symbol = symbol
        self.ticker = yf.Ticker(self.symbol)

    def get_current_price(self):
        data = self.ticker.history(period="1d")
        return float(data['Close'].squeeze().iloc[-1])

    def get_historical_data(self, period="1mo"):
        return self.ticker.history(period=period)

if __name__ == "__main__":
    tracker = StockTracker("AAPL")
    print(tracker.get_current_price())
    print(tracker.get_historical_data())