# from EpiGimp.tools.base_tool import BaseTool

from PySide6.QtCore import QRectF, QPoint
from PySide6.QtGui import QPainter, QPixmap, Qt

from EpiGimp.core.layer import Layer
from EpiGimp.tools.base_tool import BaseTool


class Brush(BaseTool):
    def __init__(self, size=20, color=Qt.GlobalColor.black):
        super().__init__("Brush", "Paintbrush")
        self.spacing = 0.25  # 25% of size (standard for smooth lines)
        self.size = size
        self.color = color
        self.sprite = self._generate_sprite()
        self.last_point = None

    def _generate_sprite(self):
        """Create the brush tip (a simple circle for now)"""
        pixmap = QPixmap(self.size, self.size)
        pixmap.fill(Qt.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(Qt.NoPen)
        painter.setBrush(self.color)
        painter.drawEllipse(0, 0, self.size, self.size)
        painter.end()
        return pixmap

    def apply(self, pos: QPoint, layer: Layer):
        painter = QPainter(layer.qimage)
        offset = self.size / 2
        rect = QRectF(pos.x() - offset, pos.y() - offset, 
                             self.size, self.size)
        painter.drawPixmap(rect.toRect(), self.sprite)
        painter.end() # Important: Save the painting
        return rect.toRect().adjusted(-2, -2, 2, 2)
