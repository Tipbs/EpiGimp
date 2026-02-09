# from EpiGimp.tools.base_tool import BaseTool

from PySide6.QtCore import QRectF
from PySide6.QtGui import QPainter, QPixmap, Qt, QPen

from EpiGimp.tools.base_tool import BaseTool


class Brush(BaseTool):
    def __init__(self, size=20, color=Qt.GlobalColor.black):
        super().__init__("Brush", "Paintbrush")
        self.spacing = 0.25  # 25% of size (standard for smooth lines)
        self.size = size
        self.color = color
        self.sprite = self._generate_sprite()

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
        # layer = self.current_layer 
            
        # 2. Create a painter that targets the LAYER (not the widget)
        # Since layer.qimage is linked to layer.pixels, this updates the NumPy array!
        # print(pos, layer.name)
        painter = QPainter(layer.qimage)
        # print(layer.pixels)
        brush_size = self.size
        offset = brush_size / 2
        
        # Setup your pen
        painter.setPen(QPen(Qt.GlobalColor.red, 5)) 

        # Draw (Using your previous logic or simple lines)
        # painter.drawLine(self.last_point, event.position())
        target_rect = QRectF(pos.x() - offset - 5, pos.y() - offset - 27, 
                             brush_size, brush_size)
        painter.drawPixmap(target_rect.toRect(), self.sprite)
        painter.end() # Important: Save the painting

        # self.last_point = event.position()
        
        # 3. Trigger a visual refresh
        # self.update()
