from PySide6.QtGui import QPainter
from PySide6.QtCore import Qt, QPoint, QRectF

from EpiGimp.tools.base_tool import BaseTool

class Eraser(BaseTool):
    def __init__(self, size=20):
        # We don't need a color for the eraser
        super().__init__("Eraser", "EraserTool") 
        self.spacing = 0.25
        self.size = size
        # self.sprite = self._generate_sprite()

    # def _generate_sprite(self):
    #     """
    #     Creates a 'mask' sprite. 
    #     The color doesn't matter here, only the alpha (opacity).
    #     Anything opaque in this sprite will be erased from the layer.
    #     """
    #     pixmap = QPixmap(self.size, self.size)
    #     pixmap.fill(Qt.transparent)
    #
    #     painter = QPainter(pixmap)
    #     painter.setRenderHint(QPainter.Antialiasing)
    #     painter.setPen(Qt.NoPen)
    #     # painter.setBrush(Qt.black) 
    #     # painter.drawEllipse(0, 0, self.size, self.size)
    #     painter.end()
    #     return pixmap

    def apply(self, pos: QPoint, layer):
        painter = QPainter(layer.qimage)
        painter.setCompositionMode(QPainter.CompositionMode_Source)
        painter.setBrush(Qt.transparent)
        painter.setPen(Qt.NoPen) # No outline
        radius = self.size / 2
        rect = QRectF(pos.x() - radius - 5, pos.y() - radius - 27, 
                      self.size, self.size)
        painter.drawEllipse(rect)
        painter.end()
        # Pass to update to only update surface
        return rect.toRect().adjusted(-2, -2, 2, 2)
