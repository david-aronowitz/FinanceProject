import numpy as np
import pandas as pd

from trading.stock_client import StockTracker


def detect_cusum_anomalies(df, threshold=5, drift=1):
    returns = df['Close'].pct_change().fillna(0)
    mean = returns.mean()
    std = returns.std()
    n = len(returns)
    sum_positive = [0] * n
    sum_negative = [0] * n
    is_anomaly = []

    yield_at_time_t = (returns.iloc[0] - mean) / std if std != 0 else 0
    sum_positive[0] = max(0, yield_at_time_t - drift)
    sum_negative[0] = max(0, -yield_at_time_t - drift)
    if sum_positive[0] > threshold or sum_negative[0] > threshold:
        is_anomaly.append(True)
        sum_positive[0] = 0
        sum_negative[0] = 0
    else:
        is_anomaly.append(False)

    for t in range(1, len(df)):
        yield_at_time_t = (returns.iloc[t] - mean) / std if std != 0 else 0
        sum_positive[t] = max(0, sum_positive[t - 1] + yield_at_time_t - drift)
        sum_negative[t] = max(0, sum_negative[t - 1] - yield_at_time_t - drift)
        if sum_positive[t] > threshold or sum_negative[t] > threshold:
            is_anomaly.append(True)
            sum_negative[t] = 0
            sum_positive[t] = 0
        else:
            is_anomaly.append(False)

    cusum_values = [round(float(max(p, n_val)), 2) for p, n_val in zip(sum_positive, sum_negative)]
    return is_anomaly, cusum_values


def _clean_series(series, round_digits=2):
    return [
        round(float(v), round_digits) if pd.notnull(v) else None
        for v in series
    ]


def calculate_rsi(series, window=14):
    delta = series.diff()
    gain = delta.where(delta > 0, 0.0)
    loss = -delta.where(delta < 0, 0.0)
    avg_gain = gain.ewm(alpha=1 / window, min_periods=1, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1 / window, min_periods=1, adjust=False).mean()
    rs = avg_gain / avg_loss
    return 100.0 - (100.0 / (1.0 + rs))


def analyze_stock(symbol, period="6mo"):
    if not symbol:
        return {"error": "לא צוין סימול מניה"}

    symbol = str(symbol).strip().replace('$', '').upper()

    try:
        tracker = StockTracker(symbol)
        df = tracker.get_historical_data(period=period)
    except Exception as e:
        return {"error": f"שגיאה בשליפת נתונים עבור '{symbol}': {str(e)}"}

    if df.empty or 'Close' not in df.columns:
        return {"error": f"לא נמצאו נתונים עבור '{symbol}'"}

    # 1. תאריכים ומחירי סגירה
    dates = [d.strftime("%Y-%m-%d") for d in df.index]
    prices = _clean_series(df['Close'])

    # 2. CUSUM & Anomalies
    anomalies, cusum_values = detect_cusum_anomalies(df)

    # 3. Recent Returns (אחוז תשואה יומי)
    daily_returns = df['Close'].pct_change() * 100
    returns_series = _clean_series(daily_returns)

    # 4. Moving Averages (SMA 20, SMA 50, EMA 9, EMA 21)
    sma_20 = _clean_series(df['Close'].rolling(window=20, min_periods=1).mean())
    sma_50 = _clean_series(df['Close'].rolling(window=50, min_periods=1).mean())
    ema_9 = _clean_series(df['Close'].ewm(span=9, adjust=False).mean())
    ema_21 = _clean_series(df['Close'].ewm(span=21, adjust=False).mean())

    # 5. Volatility (תנודתיות יומיות מנורמלת שנתית באחוזים - חלון של 20 יום)
    volatility_20d = df['Close'].pct_change().rolling(window=20, min_periods=1).std() * np.sqrt(252) * 100
    volatility_series = _clean_series(volatility_20d)

    # 6. Trading Volumes
    has_volume = 'Volume' in df.columns and not df['Volume'].empty
    volumes = [int(v) if pd.notnull(v) else 0 for v in df['Volume']] if has_volume else []
    volume_sma_20 = _clean_series(df['Volume'].rolling(window=20, min_periods=1).mean(), round_digits=0) if has_volume else []

    # 7. RSI (Relative Strength Index 14)
    rsi_14 = _clean_series(calculate_rsi(df['Close'], window=14))

    return {
        "symbol": symbol,
        "dates": dates,
        "prices": prices,
        "current_price": prices[-1] if prices else None,
        "anomalies": anomalies,
        "cusum_values": cusum_values,
        "returns": returns_series,
        "moving_averages": {
            "sma_20": sma_20,
            "sma_50": sma_50,
            "ema_9": ema_9,
            "ema_21": ema_21,
        },
        "volatility": volatility_series,
        "volume": {
            "values": volumes,
            "sma_20": volume_sma_20,
        },
        "rsi": rsi_14,
    }