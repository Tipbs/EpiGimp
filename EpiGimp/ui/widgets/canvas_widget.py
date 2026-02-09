from PySide6.QtCore import Qt, QPoint, Signal, Slot
from PySide6.QtWidgets import QTabWidget, QWidget
from PySide6.QtGui import QImage, QPainter, QPixmap

from EpiGimp.core.fileio.loader_png import *

from EpiGimp.core.canva import Canva

class CanvasWidget(QTabWidget):
    mouse_moved = Signal(QPoint)
    def __init__(self, parent=None):
        super().__init__(parent)
        # self.canvas_widget: List[CanvaWidget] = canvas
        self.currentChanged.connect(self.handleCurrentChanged)
        # self.btn_add = QPushButton("+", self)
        # self.btn_add.clicked.connect(self.add_canva)
        # self.addTab(self.btn_add, "+")

    @Slot()
    def add_canva(self, canva):
        self.addTab(CanvaWidget(canva), "New Canva")

    def handleCurrentChanged(self, index):
        # self.setCurrentWidget(self.canvas_widget[index])
        pass

    def mouseMoveEvent(self, event: PySide6.QtGui.QMouseEvent, /) -> None:
        self.mouse_moved.emit(event.position().toPoint())
        super().mouseMoveEvent(event)
        self.currentWidget().update()

    def current_canva_widget(self) -> CanvaWidget:
        if self.currentWidget():
            return self.currentWidget()
        return None


class CanvaWidget(QWidget):
    # drawing_changed = Signal()
    layer_changed = Signal(Canva)

    def __init__(self, canva: Canva, parent=None):
        super().__init__(parent)
        self.canva: Canva = canva
        self.canvas_buffer = QPixmap(*canva.shape[:2])
        self.setMinimumSize(400, 300)
        self.layer_changed.connect(self.draw_canva)
        self.layer_changed.emit(canva)
        # self.setFocusPolicy(Qt.StrongFocus)  # Enable keyboard focus
        # self._image = QImage(800, 600, QImage.Format_RGBA8888)
        # self._image.fill(Qt.white)
        # self.canvas: List[Canva] = []
        self.canva_selected = 0
        # self._image = QImage(800, 600, QImage.Format_RGBA8888)
        # self._image.fill(Qt.white)
        # self._canvas_size = self._image.size().toTuple()
        # self._drawing = False
        # self._last_point = QPoint()
        # self._brush_size = 5
        # self._brush_color = QColor(0, 0, 0, 255)
        # self._brush_opacity = 1.0
        
        # Circle drawing state
        # self._circle_mode = False
        # self._circle_start = QPoint()
        # self._circle_preview = False
        # self._circle_radius = 0
        
        # Selection and move state
        # self._selection_mode = False
        # self._selecting = False
        # self._moving = False
        # self._selection_start = QPoint()
        # self._move_start = QPoint()
        # self._selection_rect = QRect()
        # self._has_selection = False
        # self._selection_content = None
        # self._temp_image = None
        
        # Clipboard for copy/paste
        # self._clipboard = None

    def add_layer(self):
        self.canva.add_layer()
        self.layer_changed.emit(self.canva)

    def del_layer(self, idx: int):
        if len(self.canva.layers) <= 0:
            return
        self.canva.del_layer(idx)
        self.layer_changed.emit(self.canva)

    def swap_layer(self, fst: int, snd: int):
        if len(self.canva.layers) <= 0:
            return
        self.canva.swap_layer(fst, snd)
        self.layer_changed.emit(self.canva)

    # def _toggle_drawing_mode(self):
    #     self._drawing = not self._drawing
    #     self._drawButton.setText("Stop Drawing" if self._drawing else "Draw")

    # @override
    # def sizeHint(self):
    #     return QSize(800, 600)

    # def keyPressEvent(self, event: QKeyEvent):
    #     """Handle keyboard shortcuts"""
    #     # Copy: Ctrl+C
    #     if event.matches(QKeySequence.StandardKey.Copy):
    #         self.copy_selection()
    #         event.accept()
    #
    #     # Paste: Ctrl+V
    #     elif event.matches(QKeySequence.StandardKey.Paste):
    #         self.paste_from_clipboard()
    #         event.accept()
    #
    #     # Cut: Ctrl+X
    #     elif event.matches(QKeySequence.StandardKey.Cut):
    #         self.cut_selection()
    #         event.accept()
    #
    #     # Delete/Clear: Delete or Backspace
    #     elif event.key() in (Qt.Key_Delete, Qt.Key_Backspace):
    #         self.delete_selection()
    #         event.accept()
    #
    #     # Select All: Ctrl+A
    #     elif event.matches(QKeySequence.StandardKey.SelectAll):
    #         self.select_all()
    #         event.accept()
    #
    #     # Deselect: Ctrl+D or Escape
    #     elif event.key() == Qt.Key_Escape or (event.key() == Qt.Key_D and event.modifiers() & Qt.ControlModifier):
    #         self.clear_selection()
    #         event.accept()
    #
    #     else:
    #         super().keyPressEvent(event)


    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawPixmap(0, 0, self.canvas_buffer)

    def draw_canva(self):
        painter = QPainter(self.canvas_buffer)
        self.canvas_buffer.fill(Qt.GlobalColor.white)
        np_img = self.get_img()
        h, w, _ = np_img.shape
        qimg = QImage(
            np_img.data,
            w,
            h,
            w * 4,
            QImage.Format.Format_RGBA8888
        ).copy()
        painter.drawImage(0, 0, qimg)
        self.update()

    def load_image(self, path: str):
        # loader = FileLoader(path)
        # layers, metadata = loader.load_project()
        # if layers:
        #     layer_data = layers[0]['data']
        #     self.set_numpy(layer_data)
        #     self._canvas_size = self._image.size().toTuple()
        # img = QImage(path)
        # if img.isNull():
        #     return
        # self._image = img.convertToFormat(QImage.Format_RGBA8888)
        # self.update()

        img = LoaderPng(path).get_img()
        canva = Canva.from_img(img)
        # self.canvas.append(canva)
        # self.canvas[len(self.canvas) - 1].project_path = path
        # self.update()


#     def save_image(self, path: str):
#         saver = FileSaver(path)
#         arr = self.get_numpy()
#         layer = {
#             'name': 'Exported Layer',
#             'visible': True,
#             'opacity': 1.0,
#             'blend_mode': 'normal',
#             'position': (0, 0),
#             'data': arr
#         }
#         saver.save_project([layer])
#         self._image.save(path)
#         # self._image.save(path)
#
#     def get_numpy(self):
#         width = self._image.width()
#         height = self._image.height()
#         ptr = self._image.constBits()
#         arr = np.frombuffer(ptr, dtype=np.uint8).reshape((height, width, 4)).copy()
#         return arr

#     def set_numpy(self, arr: np.ndarray):
#         h, w, c = arr.shape
#         assert c == 4
#         qimg = QImage(arr.data, w, h, 4 * w, QImage.Format_RGBA8888)
#         self._image = qimg.copy()
#         self.update()
#
#     def mousePressEvent(self, event):
#         if event.button() == Qt.LeftButton:
#             canvas_point = self._widget_to_canvas_coords(event.position().toPoint())
#
#             if self._selection_mode:
#                 # Check if clicked inside existing selection
#                 if self._has_selection and self._selection_rect.contains(canvas_point):
#                     # Start moving the selection
#                     self._moving = True
#                     self._move_start = canvas_point
#                     self._copy_selection()
#                 else:
#                     # Start new selection
#                     self._selecting = True
#                     self._has_selection = False
#                     self._selection_start = canvas_point
#                     self._selection_rect = QRect(canvas_point, QSize(0, 0))
#
#             elif self._circle_mode:
#                 # Start circle drawing
#                 self._circle_start = canvas_point
#                 self._circle_preview = True
#
#             elif self._drawing:
#                 self._last_point = canvas_point
#                 self._draw_point(self._last_point)
#
#     def mouseMoveEvent(self, event):
#         canvas_point = self._widget_to_canvas_coords(event.position().toPoint())
#
#         if self._selection_mode and self._selecting and event.buttons() & Qt.LeftButton:
#             # Update selection rectangle
#             self._selection_rect = QRect(self._selection_start, canvas_point).normalized()
#             self.update()
#
#         elif self._selection_mode and self._moving and event.buttons() & Qt.LeftButton:
#             # Move selection
#             delta = canvas_point - self._move_start
#             self._update_move_preview(delta)
#
#         elif self._circle_mode and self._circle_preview and event.buttons() & Qt.LeftButton:
#             # Update circle preview radius
#             dx = canvas_point.x() - self._circle_start.x()
#             dy = canvas_point.y() - self._circle_start.y()
#             self._circle_radius = int(np.sqrt(dx * dx + dy * dy))
#             self.update()
#
#         elif self._drawing and event.buttons() & Qt.LeftButton:
#             self._draw_line(self._last_point, canvas_point)
#             self._last_point = canvas_point
#
#     def mouseReleaseEvent(self, event):
#         if event.button() == Qt.LeftButton:
#             if self._selection_mode and self._selecting:
#                 # Finalize selection
#                 self._selecting = False
#                 if self._selection_rect.width() > 5 and self._selection_rect.height() > 5:
#                     self._has_selection = True
#                 else:
#                     self._has_selection = False
#                     self._selection_rect = QRect()
#                 self.update()
#
#             elif self._selection_mode and self._moving:
#                 # Finalize move
#                 canvas_point = self._widget_to_canvas_coords(event.position().toPoint())
#                 delta = canvas_point - self._move_start
#                 self._finalize_move(delta)
#                 self._moving = False
#                 self._temp_image = None
#                 self.update()
#
#             elif self._circle_mode and self._circle_preview:
#                 # Finalize circle drawing
#                 canvas_point = self._widget_to_canvas_coords(event.position().toPoint())
#                 dx = canvas_point.x() - self._circle_start.x()
#                 dy = canvas_point.y() - self._circle_start.y()
#                 radius = int(np.sqrt(dx * dx + dy * dy))
#                 self.draw_circle(self._circle_start.x(), self._circle_start.y(), radius)
#                 self._circle_preview = False
#                 self._circle_radius = 0
#
#             self.drawing_changed.emit()
#
#     def _widget_to_canvas_coords(self, widget_point: QPoint) -> QPoint:
#         widget_rect = self.rect()
#         canvas_w, canvas_h = self._canvas_size
#
#         scale_x = canvas_w / widget_rect.width()
#         scale_y = canvas_h / widget_rect.height()
#
#         canvas_x = int(widget_point.x() * scale_x)
#         canvas_y = int(widget_point.y() * scale_y)
#
#         canvas_x = max(0, min(canvas_w - 1, canvas_x))
#         canvas_y = max(0, min(canvas_h - 1, canvas_y))
#
#         return QPoint(canvas_x, canvas_y)
#
#     def _copy_selection(self):
#         """Copy the selected area to a temporary buffer"""
#         if self._has_selection:
#             self._selection_content = self._image.copy(self._selection_rect)
#
#     def _paste_selection(self, top_left: QPoint):
#         """Paste the selection content at the given top-left position"""
#         if self._selection_content is not None:
#             painter = QPainter(self._image)
#             painter.setCompositionMode(QPainter.CompositionMode_SourceOver)
#             painter.drawImage(top_left, self._selection_content)
#             painter.end()
#             self.update()
#
#     def _update_move_preview(self, delta: QPoint):
#         """Update the preview of the moved selection"""
#         # Create temp image based on original
#         self._temp_image = self._image.copy()
#
#         # Clear the original selection area (make it white)
#         painter = QPainter(self._temp_image)
#         painter.setCompositionMode(QPainter.CompositionMode_Source)
#         painter.fillRect(self._selection_rect, Qt.white)
#
#         # Draw the selection content at new position
#         new_rect = self._selection_rect.translated(delta)
#         painter.setCompositionMode(QPainter.CompositionMode_SourceOver)
#         painter.drawImage(new_rect.topLeft(), self._selection_content)
#         painter.end()
#
#         self.update()
#
#     def _finalize_move(self, delta: QPoint):
#         """Finalize the move operation"""
#         # Apply the move to the actual image
#         painter = QPainter(self._image)
#         painter.setCompositionMode(QPainter.CompositionMode_Source)
#
#         # Clear original area
#         painter.fillRect(self._selection_rect, Qt.white)
#
#         # Draw at new position
#         new_rect = self._selection_rect.translated(delta)
#         painter.setCompositionMode(QPainter.CompositionMode_SourceOver)
#         painter.drawImage(new_rect.topLeft(), self._selection_content)
#         painter.end()
#
#         # Update selection rectangle to new position
#         self._selection_rect = new_rect
#         self._selection_content = None
#
#     def _draw_point(self, point: QPoint):
#         """Draw a single point using QPainter"""
#         painter = QPainter(self._image)
#
#         pen = QPen(self._brush_color, self._brush_size, Qt.SolidLine, Qt.RoundCap)
#         painter.setPen(pen)
#         painter.setOpacity(self._brush_opacity)
#
#         painter.drawPoint(point)
#
#         painter.end()
#         self.update()
#
#     def _draw_line(self, start: QPoint, end: QPoint):
#         """Draw a line between two points using QPainter"""
#         painter = QPainter(self._image)
#
#         pen = QPen(self._brush_color, self._brush_size, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
#         painter.setPen(pen)
#         painter.setOpacity(self._brush_opacity)
#
#         painter.setRenderHint(QPainter.Antialiasing, True)
#
#         painter.drawLine(start, end)
#
#         painter.end()
#         self.update()
#
#     def draw_circle(self, center_x: int, center_y: int, radius: int, filled: bool = False):
#         """Draw a circle using Qt's built-in drawing functions"""
#         painter = QPainter(self._image)
#
#         painter.setRenderHint(QPainter.Antialiasing, True)
#
#         pen = QPen(self._brush_color, self._brush_size)
#         painter.setPen(pen)
#
#         if filled:
#             brush = QBrush(self._brush_color)
#             painter.setBrush(brush)
#         else:
#             painter.setBrush(Qt.NoBrush)
#
#         painter.setOpacity(self._brush_opacity)
#
#         painter.drawEllipse(QPoint(center_x, center_y), radius, radius)
#
#         painter.end()
#         self.update()
#
#     # Clipboard operations
#     def copy_selection(self):
#         """Copy selection to clipboard (Ctrl+C)"""
#         if self._has_selection:
#             self._clipboard = self._image.copy(self._selection_rect)
#             print("Selection copied to clipboard")
#         else:
#             print("No selection to copy")
#
#     def cut_selection(self):
#         """Cut selection to clipboard (Ctrl+X)"""
#         if self._has_selection:
#             self._clipboard = self._image.copy(self._selection_rect)
#             painter = QPainter(self._image)
#             painter.fillRect(self._selection_rect, Qt.white)
#             painter.end()
#             self.clear_selection()
#             self.update()
#             print("Selection cut to clipboard")
#         else:
#             print("No selection to cut")
#
#     def paste_from_clipboard(self):
#         """Paste from clipboard (Ctrl+V)"""
#         if self._clipboard is not None:
#             # Paste at center of canvas or at last selection position
#             if self._has_selection:
#                 paste_pos = self._selection_rect.topLeft()
#             else:
#                 # Paste at center
#                 canvas_w, canvas_h = self._canvas_size
#                 clip_w = self._clipboard.width()
#                 clip_h = self._clipboard.height()
#                 paste_pos = QPoint((canvas_w - clip_w) // 2, (canvas_h - clip_h) // 2)
#
#             painter = QPainter(self._image)
#             painter.setCompositionMode(QPainter.CompositionMode_SourceOver)
#             painter.drawImage(paste_pos, self._clipboard)
#             painter.end()
#
#             # Create selection around pasted content
#             self._selection_rect = QRect(paste_pos, self._clipboard.size())
#             self._has_selection = True
#             self._selection_mode = True
#
#             self.update()
#             print("Pasted from clipboard")
#         else:
#             print("Clipboard is empty")
#
#     def select_all(self):
#         """Select entire canvas (Ctrl+A)"""
#         canvas_w, canvas_h = self._canvas_size
#         self._selection_rect = QRect(0, 0, canvas_w, canvas_h)
#         self._has_selection = True
#         self._selection_mode = True
#         self.update()
#         print("Selected all")
#
#     # Helper methods for external use
#     def set_brush_size(self, size: int):
#         self._brush_size = max(1, size)
#
#     def set_brush_color(self, color: QColor):
#         self._brush_color = color
#
#     def set_brush_opacity(self, opacity: float):
#         self._brush_opacity = max(0.0, min(1.0, opacity))
#
#     def set_circle_mode(self, enabled: bool):
#         """Enable or disable circle drawing mode"""
#         self._circle_mode = enabled
#         self._selection_mode = False
#         self._circle_preview = False
#         self._circle_radius = 0
#         if enabled:
#             self._drawing = False
#
#     def set_selection_mode(self, enabled: bool):
#         """Enable or disable selection mode"""
#         self._selection_mode = enabled
#         self._circle_mode = False
#         self._drawing = False
#         if not enabled:
#             self._has_selection = False
#             self._selection_rect = QRect()
#             self._selecting = False
#             self._moving = False
#             self._temp_image = None
#             self.update()
#
#     def set_move_mode(self, enabled: bool):
#         """Enable or disable move mode for the current selection"""
#         if self._has_selection:
#             self._moving = enabled
#             self._selecting = False
#             if not enabled:
#                 self._temp_image = None
#                 self.update()
#
#     def clear_selection(self):
#         """Clear the current selection (Escape or Ctrl+D)"""
#         self._has_selection = False
#         self._selection_rect = QRect()
#         self._selection_content = None
#         self._selecting = False
#         self._moving = False
#         self._temp_image = None
#         self.update()
#         print("Selection cleared")
#
#     def delete_selection(self):
#         """Delete the selected area (Delete or Backspace)"""
#         if self._has_selection:
#             painter = QPainter(self._image)
#             painter.fillRect(self._selection_rect, Qt.white)
#             painter.end()
#             self.clear_selection()
#             self.update()
#             print("Selection deleted")
#         else:
#             print("No selection to delete")
#
#     def enable_selection_mode(self):
#         self.set_selection_mode(not self._selection_mode)
#
# # Convenience bridge to numpy (pixels as H x W x 4 uint8)
#     def get_numpy(self):
#         # Get image dimensions
#         width = self._image.width()
#         height = self._image.height()
#
#         # Get the raw bytes
#         ptr = self._image.constBits()
#
#         # Convert to numpy array
#         arr = np.frombuffer(ptr, dtype=np.uint8).reshape((height, width, 4)).copy()
#         return arr
#
#
#     def set_numpy(self, arr):
#         h, w, c = arr.shape
#         assert c == 4
#         qimg = QImage(arr.data, w, h, 4 * w, QImage.Format_RGBA8888)
# # keep a copy of data to avoid GC issues
#         self._image = qimg.copy()
#         self.update()

# Convenience bridge to numpy (pixels as H x W x 4 uint8)
    def get_img(self):
        return self.canva.get_img().get_pixels()
    
    def transform(self, operation: str):
        if operation == 'flip_horizontal':
            self.canva.flip_horizontal()
        elif operation == 'flip_vertical':
            self.canva.flip_vertical()
        elif operation == 'rotate_90_clockwise':
            self.canva.rotate_90_clockwise()
        elif operation == 'rotate_90_counterclockwise':
            self.canva.rotate_90_counterclockwise()
        elif operation == 'rotate_180':
            self.canva.rotate_180()
        self.update()
