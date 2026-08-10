import yfinance as yf

class StockTracker():
    def __init__(self, symbol):
        self.symbol = symbol
        self.ticker = yf.Ticker(self.symbol)

    def get_current_price(self):
        try:
            price = self.ticker.fast_info.get('lastPrice')
            if price is not None and not list(map(str, [price]))[0] == 'nan':
                return float(price)
        except Exception:
            pass

        data = self.ticker.history(period="5d")

        if data.empty or "Close" not in data or data["Close"].empty:
            raise ValueError(f"Could not retrieve price data for stock {self.symbol}. This may be due to a communication issue with Yahoo Finance.")

        return float(data["Close"].dropna().iloc[-1])

    def get_historical_data(self, period="1mo"):
        return self.ticker.history(period=period)

if __name__ == "__main__":
    tracker = StockTracker("AAPL")
    print(tracker.get_current_price())
    print(tracker.get_historical_data())