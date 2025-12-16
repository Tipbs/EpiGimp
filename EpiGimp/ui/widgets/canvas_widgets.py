from PySide6.QtWidgets import QWidget, QPushButton
from PySide6.QtGui import QPainter, QImage, QColor
from PySide6.QtCore import Qt, QSize, Signal, QPoint
from typing import override

import numpy as np
from EpiGimp.core.fileio.file_loader import FileLoader
from EpiGimp.core.fileio.file_saver import FileSaver

class CanvasWidget(QWidget):
    drawing_changed = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(400, 300)
        self._image = QImage(800, 600, QImage.Format_RGBA8888)
        self._image.fill(Qt.white)

        self._canvas_size = self._image.size().toTuple()
        self._drawing = False  # Fixed: Should start as False
        self._last_point = QPoint()
        self._brush_size = 5
        self._brush_color = QColor(0, 0, 0, 255)
        self._brush_opacity = 1.0

    def _toggle_drawing_mode(self):
        self._drawing = not self._drawing
        self._drawButton.setText("Stop Drawing" if self._drawing else "Draw")

    @override
    def sizeHint(self):
        return QSize(800, 600)

    def paintEvent(self, event):
        painter = QPainter(self)
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

    def get_numpy(self):
        width = self._image.width()
        height = self._image.height()
        ptr = self._image.constBits()
        arr = np.frombuffer(ptr, dtype=np.uint8).reshape((height, width, 4)).copy()
        return arr

    def set_numpy(self, arr: np.ndarray):
        h, w, c = arr.shape
        assert c == 4
        qimg = QImage(arr.data, w, h, 4 * w, QImage.Format_RGBA8888)
        self._image = qimg.copy()
        self.update()

    def _sync_numpy_to_image(self, layer_data: np.ndarray):
        """Sync modified numpy data back to QImage"""
        h, w = layer_data.shape[:2]
        qimg = QImage(layer_data.data, w, h, 4 * w, QImage.Format_RGBA8888)
        self._image = qimg.copy()
        self.update()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            if self._drawing == True:
                self._last_point = self._widget_to_canvas_coords(event.position().toPoint())
                self._draw_point(self._last_point)

    def mouseMoveEvent(self, event):
        if self._drawing and event.buttons() & Qt.LeftButton:
            current_point = self._widget_to_canvas_coords(event.position().toPoint())
            self._draw_line(self._last_point, current_point)
            self._last_point = current_point

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drawing_changed.emit()

    def _widget_to_canvas_coords(self, widget_point: QPoint) -> QPoint:
        widget_rect = self.rect()
        canvas_w, canvas_h = self._canvas_size
        
        scale_x = canvas_w / widget_rect.width()
        scale_y = canvas_h / widget_rect.height()
        
        canvas_x = int(widget_point.x() * scale_x)
        canvas_y = int(widget_point.y() * scale_y)
        
        canvas_x = max(0, min(canvas_w - 1, canvas_x))
        canvas_y = max(0, min(canvas_h - 1, canvas_y))
        
        return QPoint(canvas_x, canvas_y)

    def _draw_point(self, point: QPoint):
        """Draw a single point on the active layer"""
        # Get fresh numpy data from image
        layer_data = self.get_numpy()  # Fixed: Get fresh data
        x, y = point.x(), point.y()
        
        self._draw_brush_stroke(layer_data, x, y)
        self._sync_numpy_to_image(layer_data)  # Fixed: Sync back to image

    def _draw_line(self, start: QPoint, end: QPoint):
        """Draw a line between two points using Bresenham's algorithm"""
        # Get fresh numpy data from image
        layer_data = self.get_numpy()  # Fixed: Get fresh data
        
        x1, y1 = start.x(), start.y()
        x2, y2 = end.x(), end.y()
        
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        
        x_step = 1 if x1 < x2 else -1
        y_step = 1 if y1 < y2 else -1
        
        error = dx - dy
        x, y = x1, y1
        
        while True:
            self._draw_brush_stroke(layer_data, x, y)
            if x == x2 and y == y2:
                break
                
            error2 = 2 * error
            
            if error2 > -dy:
                error -= dy
                x += x_step
                
            if error2 < dx:
                error += dx
                y += y_step
        
        self._sync_numpy_to_image(layer_data)  # Fixed: Sync back to image

    def _draw_brush_stroke(self, layer_data: np.ndarray, center_x: int, center_y: int):
        """Draw a circular brush stroke at the specified position"""
        h, w = layer_data.shape[:2]
        radius = self._brush_size // 2
        
        r = self._brush_color.red()
        g = self._brush_color.green()
        b = self._brush_color.blue()
        brush_alpha = int(self._brush_color.alpha() * self._brush_opacity)
        
        for dy in range(-radius, radius + 1):
            for dx in range(-radius, radius + 1):
                if dx * dx + dy * dy <= radius * radius:
                    px = center_x + dx
                    py = center_y + dy
                    
                    if 0 <= px < w and 0 <= py < h:
                        alpha = brush_alpha / 255.0
                        inv_alpha = 1.0 - alpha
                        
                        layer_data[py, px, 0] = int(layer_data[py, px, 0] * inv_alpha + r * alpha)
                        layer_data[py, px, 1] = int(layer_data[py, px, 1] * inv_alpha + g * alpha)
                        layer_data[py, px, 2] = int(layer_data[py, px, 2] * inv_alpha + b * alpha)
                        
                        current_alpha = layer_data[py, px, 3] / 255.0
                        new_alpha = current_alpha + alpha * (1.0 - current_alpha)
                        layer_data[py, px, 3] = int(new_alpha * 255)

    # Helper methods for external use
    def set_brush_size(self, size: int):
        self._brush_size = max(1, size)

    def set_brush_color(self, color: QColor):
        self._brush_color = color

    def set_brush_opacity(self, opacity: float):
        self._brush_opacity = max(0.0, min(1.0, opacity))