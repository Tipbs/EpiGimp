from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QPainter, QImage
from PySide6.QtCore import Qt, QSize
import numpy as np

class CanvasWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(400, 300)
        self._image = QImage(800, 600, QImage.Format_RGBA8888)
        self._image.fill(Qt.white)


    def sizeHint(self):
        return QSize(800, 600)


    def paintEvent(self, event):
        painter = QPainter(self)
# Simple scaling to fit widget
        painter.drawImage(self.rect(), self._image)


    def load_image(self, path: str):
        img = QImage(path)
        if img.isNull():
            return
        self._image = img.convertToFormat(QImage.Format_RGBA8888)
        self.update()


    def save_image(self, path: str):
        self._image.save(path)


# Convenience bridge to numpy (pixels as H x W x 4 uint8)
    def get_numpy(self):
        ptr = self._image.bits()
        ptr.setsize(self._image.byteCount())
        arr = np.frombuffer(ptr, dtype=np.uint8).reshape((self._image.height(), self._image.width(), 4)).copy()
        return arr


    def set_numpy(self, arr: np.ndarray):
        h, w, c = arr.shape
        assert c == 4
        qimg = QImage(arr.data, w, h, 4 * w, QImage.Format_RGBA8888)
# keep a copy of data to avoid GC issues
        self._image = qimg.copy()
        self.update()
