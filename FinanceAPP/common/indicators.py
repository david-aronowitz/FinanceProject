from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import IsolationForest
import pandas as pd
import numpy as np

def detect_cusum_anomalies(df, threshold=5, drift=1):
    returns = df['Close'].pct_change().fillna(0)
    mean = returns.mean()
    std = returns.std()
    n = len(returns)
    sum_positive = [0]*n
    sum_negative = [0]*n
    is_anomaly = []
    yield_at_time_t = (returns.iloc[0] - mean)/ std if std != 0 else 0
    sum_positive[0] = max(0,yield_at_time_t - drift)
    sum_negative[0] = max(0,-yield_at_time_t - drift)
    if sum_positive[0] > threshold or sum_negative[0] > threshold:
        is_anomaly.append(True)
        sum_positive[0] = 0
        sum_negative[0] = 0
    else:
        is_anomaly.append(False)

    for t in range(1,len(df)):
        yield_at_time_t = (returns.iloc(t) - mean)/ std if std != 0 else 0
        sum_positive[t] = max(0,sum_positive[t-1] + yield_at_time_t - drift)
        sum_negative[t] = max(0,sum_negative[t-1] - yield_at_time_t - drift)
        if (sum_positive[t] > threshold or sum_negative[t] >threshold):
            is_anomaly.append(True)
            sum_negative[t] = 0
            sum_positive[t] = 0
        else:
            is_anomaly.append(False)

def detect_ml_anomalies(df, contamination=0.02):
    pass

