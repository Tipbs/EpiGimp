from PySide6.QtWidgets import QWidget 
from PySide6.QtGui import QImage, QPainter
from PySide6.QtCore import QSize
from typing import override, List
from EpiGimp.core.fileio.loader_png import *

from EpiGimp.core.canva import Canva

class CanvasWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(400, 300)
        self.canvas: List[Canva] = []
        self.canva_selected = 0
        # self._image = QImage(800, 600, QImage.Format_RGBA8888)
        # self._image.fill(Qt.white)


    @override
    def sizeHint(self):
        return QSize(800, 600)


    @override
    def paintEvent(self, event):
        if len(self.canvas) == 0:
            return
        painter = QPainter(self)
# Simple scaling to fit widget
        # l = Layer((5000, 5000), (255, 0, 0, 0))
        # np_img = l.get_pixels()
        np_img = self.get_img()
        # np_img = np.zeros((5000, 5000, 4), dtype=np.uint8)
        # np_img[:] = (255, 0, 0, 255)

        h, w, _ = np_img.shape

        qimg = QImage(
            np_img.data,
            w,
            h,
            w * 4,
            QImage.Format.Format_RGBA8888
        ).copy()

        painter.drawImage(0, 0, qimg)


    def load_image(self, path: str):
        img = LoaderPng(path).get_img()
        canva = Canva.from_img(img)
        self.canvas.append(canva)
        self.update()


    def save_image(self, path: str):
        # self._image.save(path)
        pass


# Convenience bridge to numpy (pixels as H x W x 4 uint8)
    def get_img(self):
        if len(self.canvas) == 0:
            raise Exception('No canva')
        canva = self.canvas[self.canva_selected]
        return canva.get_img().get_pixels()
