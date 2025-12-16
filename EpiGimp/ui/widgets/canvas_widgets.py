from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QPainter, QImage
from PySide6.QtCore import Qt, QSize
import numpy as np
from EpiGimp.core.fileio.file_loader import FileLoader
from EpiGimp.core.fileio.file_saver import FileSaver

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
        loader = FileLoader(path)
        layers, metadata = loader.load_project()
        if layers:
            layer_data = layers[0]['data']
            self.set_numpy(layer_data)

    def save_image(self, path: str):
        saver = FileSaver(path)
        arr = self.get_numpy()
        layer = {
            'name': 'Exported Layer',
            'visible': True,
            'opacity': 1.0,
            'blend_mode': 'normal',
            'position': (0, 0),
            'data': arr
        }
        saver.save_project([layer])



# Convenience bridge to numpy (pixels as H x W x 4 uint8)
    def get_numpy(self):
        # Get image dimensions
        width = self._image.width()
        height = self._image.height()
        
        # Get the raw bytes
        ptr = self._image.constBits()
        
        # Convert to numpy array
        arr = np.frombuffer(ptr, dtype=np.uint8).reshape((height, width, 4)).copy()
        return arr


    def set_numpy(self, arr: np.ndarray):
        h, w, c = arr.shape
        assert c == 4
        qimg = QImage(arr.data, w, h, 4 * w, QImage.Format_RGBA8888)
# keep a copy of data to avoid GC issues
        self._image = qimg.copy()
        self.update()
