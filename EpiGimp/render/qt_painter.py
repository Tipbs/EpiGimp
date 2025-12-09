# Small helper to convert numpy arrays to QImage (reuse in canvas)
from PySide6.QtGui import QImage
import numpy as np

def numpy_to_qimage(arr: np.ndarray) -> QImage:
    h, w, c = arr.shape
    assert c == 4
    return QImage(arr.data, w, h, 4 * w, QImage.Format_RGBA8888).copy()
