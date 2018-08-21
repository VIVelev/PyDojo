import numpy as np

__all__ = [
    "convert_assert",
]

def convert_assert(y, y_pred):
    y, y_pred = np.array(y), np.array(y_pred)
    assert y.size == y_pred.size

    return y, y_pred
