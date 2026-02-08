# from EpiGimp.tools.base_tool import BaseTool

class Brush():
    def __init__(self, size=20, color=Qt.black):
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

    def draw(self, pos: QPoint, layer: Layer):
        # layer = self.current_layer 
            
        # 2. Create a painter that targets the LAYER (not the widget)
        # Since layer.qimage is linked to layer.pixels, this updates the NumPy array!
        painter = QPainter(layer.qimage)
        
        # Setup your pen
        painter.setPen(QPen(Qt.red, 5)) 

        # Draw (Using your previous logic or simple lines)
        painter.drawLine(self.last_point, event.position())
        painter.drawPixmap(target_rect.toRect(), self.sprite)
        painter.end() # Important: Save the painting

        self.last_point = event.position()
        
        # 3. Trigger a visual refresh
        self.update()
