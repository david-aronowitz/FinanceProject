from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import IsolationForest
from trading.stock_client import StockTracker
import pandas as pd
import numpy as np


def detect_cusum_anomalies(df, threshold=5, drift=1):
    if df is None or df.empty or 'Close' not in df.columns:
        return []

    close = df['Close'].squeeze()
    if isinstance(close, pd.DataFrame):
        close = close.iloc[:, 0]
    close = close.dropna()

    if len(close) < 2:
        return [False] * len(close)

    returns = close.pct_change().fillna(0)
    mean = returns.mean()
    std = returns.std()
    n = len(returns)

    if pd.isna(std) or std == 0:
        return [False] * n

    sum_positive = [0.0] * n
    sum_negative = [0.0] * n
    is_anomaly = []

    for t in range(n):
        r = returns.iloc[t]
        yield_at_time_t = (r - mean) / std
        prev_pos = sum_positive[t - 1] if t > 0 else 0.0
        prev_neg = sum_negative[t - 1] if t > 0 else 0.0

        sum_pos = max(0.0, prev_pos + yield_at_time_t - drift)
        sum_neg = max(0.0, prev_neg - yield_at_time_t - drift)

        if sum_pos > threshold or sum_neg > threshold:
            is_anomaly.append(True)
            sum_positive[t] = 0.0
            sum_negative[t] = 0.0
        else:
            is_anomaly.append(False)
            sum_positive[t] = sum_pos
            sum_negative[t] = sum_neg

    return is_anomaly


def _simple_moving_average(prices, window=20):
    if not prices:
        return []
    series = pd.Series(prices)
    sma = series.rolling(window=window, min_periods=1).mean()
    return [round(float(v), 2) if not pd.isna(v) else None for v in sma]


def analyze_stock(symbol, period="1mo"):
    if not symbol:
        return {"error": "לא צוין סימול מניה"}, 400

    try:
        tracker = StockTracker(symbol)
        df = tracker.get_historical_data(period=period)

        if df is None or df.empty or 'Close' not in df.columns:
            return {"error": f"לא נמצאו נתונים עבור '{symbol}'"}, 400

        close = df['Close'].squeeze()
        if isinstance(close, pd.DataFrame):
            close = close.iloc[:, 0]
        close = close.dropna()

        if close.empty:
            return {"error": f"אין מחירי סגירה תקינים עבור '{symbol}'"}, 400

        # המרה מפורשת של תאריכים למחרוזות Python רגילות
        dates = [str(d.date()) if hasattr(d, 'date') else str(d) for d in close.index]

        # המרה מפורשת של מחירים ל-float רגיל של Python (מניעת np.float64)
        prices = [float(p) for p in close.values]

        anomalies_raw = detect_cusum_anomalies(df)
        # המרה מפורשת ל-bool רגיל של Python (מניעת np.bool_)
        anomalies = [bool(a) for a in anomalies_raw]

        sma_raw = _simple_moving_average(prices, window=20)
        sma = [float(v) if v is not None and not np.isnan(v) else None for v in sma_raw]

        return {
            "symbol": str(symbol).upper(),
            "dates": dates,
            "prices": prices,
            "sma_20": sma,
            "anomalies": anomalies,
            "current_price": prices[-1] if prices else None,
        }
    except Exception as e:
        import traceback
        traceback.print_exc()  # מדפיס את השגיאה המלאה לטרמינל כדי שתוכל לראות אותה
        return {"error": f"שגיאה בעיבוד הנתונים: {str(e)}"}, 500