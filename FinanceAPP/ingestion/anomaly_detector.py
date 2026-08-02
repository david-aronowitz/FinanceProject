import numpy as np
from ring_buffer import RingBuffer

class AnomalyDetector():
    def __init__(self, threshold,size):
        self.threshold = threshold
        self.Data = RingBuffer(size)

    def process_price(self,price):
        self.Data.add(price)
        if (not self.Data.is_full()):
            return (False, 0.0)
        values = self.Data.get_all()
        mean = np.mean(values)
        std = np.std(values)
        if (std == 0):
            return (False, 0.0)
        z_score = (price - mean) / std
        is_anomaly = (abs(z_score) > self.threshold)
        return (is_anomaly,z_score)

