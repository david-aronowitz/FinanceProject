from collections import deque
import numpy as np

class RingBuffer:
    def __init__(self,size):
        self.size = size
        self.buffer = deque(maxlen=size)

    def __len__(self):
        return len(self.buffer)

    def add(self,item):
        self.buffer.append(item)

    def is_full(self):
        return len(self.buffer) == self.size

    def get_all(self):
        return np.array(self.buffer)


