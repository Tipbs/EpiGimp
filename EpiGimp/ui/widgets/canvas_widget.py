from __future__ import annotations
import typing
from typing import Optional, Dict

from PySide6.QtCore import Qt, QPoint, Signal, Slot
from PySide6.QtWidgets import QTabWidget, QWidget
from PySide6.QtGui import QPainter, QPixmap, QMouseEvent, QPaintEvent, QImage, QPen

from EpiGimp.core.fileio.loader_png import LoaderPng
from EpiGimp.core.canva import Canva

if typing.TYPE_CHECKING:
    from EpiGimp.core.layer import Layer


class CanvasWidget(QTabWidget):
    """
    A container widget (Tabbed Interface) that holds multiple CanvaWidget instances.
    
    This acts as the central view controller for open images.
    """
    
    mouse_moved = Signal(QPoint)

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """
        Initialize the CanvasWidget.

        Args:
            parent (Optional[QWidget]): The parent widget.
        """
        super().__init__(parent)
        self.setMouseTracking(True) # Ensure mouse move events are captured

    @Slot(Canva)
    def add_canva(self, canva: Canva) -> None:
        """
        Create a new tab containing a widget for the provided Canva object.

        Args:
            canva (Canva): The core image data object.
        """
        widget = CanvaWidget(canva)
        self.addTab(widget, "New Canva")
        # Optional: Switch to the new tab immediately
        self.setCurrentWidget(widget)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        """
        Capture mouse movement over the tab area and emit coordinates.
        
        Args:
            event (QMouseEvent): The mouse event.
        """
        # 
        if event.buttons() & Qt.LeftButton:
            self.mouse_moved.emit(event.position().toPoint())
            super().mouseMoveEvent(event)
            
            # Trigger repaint on the specific active canvas widget
            current = self.currentWidget()
            if current:
                current.update()

    def current_canva_widget(self) -> Optional[CanvaWidget]:
        """
        Retrieve the currently active CanvaWidget.

        Returns:
            Optional[CanvaWidget]: The active widget, or None if no tabs exist.
        """
        widget = self.currentWidget()
        if isinstance(widget, CanvaWidget):
            return widget
        return None


class CanvaWidget(QWidget):
    """
    The visual representation of a single image project (Canva).
    
    Handles rendering the internal Layer stack to a QPixmap and 
    displaying it via QPainter.
    """
    
    layer_changed = Signal(Canva)

    def __init__(self, canva: Canva, parent: Optional[QWidget] = None) -> None:
        """
        Initialize the widget with a Canva object.

        Args:
            canva (Canva): The core image project to render.
            parent (Optional[QWidget]): Parent widget.
        """
        super().__init__(parent)
        self.canva: Canva = canva
        
        # Determine initial shape (Width, Height)
        # Note: Canva shape is usually (H, W), QPixmap takes (W, H)
        shape_wh = (canva.shape[1], canva.shape[0])
        self.canvas_buffer = QPixmap(*shape_wh)
        
        self.setMinimumSize(400, 300)
        self.setMouseTracking(True)
        
        # Color temperature state
        self.original_temp: float = 6500.0
        self.target_temp: float = 6500.0
        
        # Tool state
        self.current_tool = None
        
        # Move selection state
        self.moving_selection = False
        self.move_start_point = None
        self._temp_selection_offset = QPoint(0, 0)
        
        # Signals
        self.layer_changed.connect(self.draw_canva)
        
        # Initial draw
        self.layer_changed.emit(canva)

    # =========================================================================
    # Layer Operations
    # =========================================================================

    def add_layer(self) -> None:
        """Add a default layer to the internal Canva."""
        self.canva.add_layer()
        self.layer_changed.emit(self.canva)

    def import_image_as_layer(self, path: str) -> None:
        """
        Load an external image and add it as a new layer.

        Args:
            path (str): File path to the image.
        """
        try:
            img = LoaderPng(path).get_img()
            self.canva.add_img_layer(img, path)
            self.layer_changed.emit(self.canva)
        except Exception as e:
            print(f"Error importing layer: {e}")

    def del_layer(self, idx: int) -> None:
        """
        Delete a layer by index.

        Args:
            idx (int): Index of the layer to remove.
        """
        if not self.canva.layers:
            return
        self.canva.del_layer(idx)
        self.layer_changed.emit(self.canva)

    def swap_layer(self, fst: int, snd: int) -> None:
        """
        Swap two layers.

        Args:
            fst (int): First layer index.
            snd (int): Second layer index.
        """
        if not self.canva.layers:
            return
        self.canva.swap_layer(fst, snd)
        self.layer_changed.emit(self.canva)

    # =========================================================================
    # Drawing & Rendering
    # =========================================================================

    def paintEvent(self, event: QPaintEvent) -> None:
        """
        Qt Paint Event. Draws the internal buffer to the screen.
        """
        painter = QPainter(self)
        painter.drawPixmap(0, 0, self.canvas_buffer)
        
        # Draw selection overlay if there's an active selection
        if self.canva.has_selection():
            selection_rect, selection_type = self.canva.get_selection()
            if selection_rect and not selection_rect.isEmpty():
                # If moving, show selection at offset position
                display_rect = selection_rect
                if self.moving_selection and not self._temp_selection_offset.isNull():
                    display_rect = selection_rect.translated(self._temp_selection_offset)
                
                # Draw selection with dashed line
                pen = QPen(Qt.GlobalColor.black, 1, Qt.PenStyle.DashLine)
                painter.setPen(pen)
                painter.setBrush(Qt.BrushStyle.NoBrush)
                
                if selection_type == 'ellipse':
                    painter.drawEllipse(display_rect)
                else:  # rectangle
                    painter.drawRect(display_rect)
        
        # Draw current selection being created (if using selection tool)
        if self.current_tool and hasattr(self.current_tool, 'get_selection') and not self.moving_selection:
            temp_selection = self.current_tool.get_selection()
            if temp_selection and not temp_selection.isEmpty():
                pen = QPen(Qt.GlobalColor.white, 1, Qt.PenStyle.DashLine)
                painter.setPen(pen)
                painter.setBrush(Qt.BrushStyle.NoBrush)
                
                if hasattr(self.current_tool, 'name') and 'Ellipse' in self.current_tool.name:
                    painter.drawEllipse(temp_selection)
                else:
                    painter.drawRect(temp_selection)
        
        painter.end()

    @Slot()
    def draw_canva(self) -> None:
        """
        Render the Core Canva object into the GUI QPixmap buffer.
        
        This composites all layers in the Canva object and updates the UI.
        """
        # 
        
        # Check if buffer needs resizing (if canvas shape changed)
        # current_w, current_h = self.canva.shape[1], self.canva.shape[0]
        # if (self.canvas_buffer.width(), self.canvas_buffer.height()) != (current_w, current_h):
        #      self.canvas_buffer = QPixmap(current_w, current_h)

        # Begin painting on the off-screen buffer
        painter = QPainter(self.canvas_buffer)
        
        # 1. Clear background
        self.canvas_buffer.fill(Qt.GlobalColor.white)
        
        # 2. Get composited image from Core
        # Assumption: get_img() returns a Layer object which has a .qimage property
        layer: Layer = self.get_img()
        
        # 3. Draw to buffer
        if hasattr(layer, 'qimage'):
            qimg: QImage = layer.qimage.copy()
            painter.drawImage(0, 0, qimg)
        else:
            print("Warning: Rendered layer has no 'qimage' property.")

        painter.end()
        
        # 4. Schedule screen update
        self.update()

    def get_img(self) -> Layer:
        """
        Proxy method to get the composited image from the core Canva.

        Returns:
            Layer: The flattened image layer.
        """
        return self.canva.get_img()

    # =========================================================================
    # Transformations & Adjustments
    # =========================================================================

    def transform(self, operation: str) -> None:
        """
        Apply a geometric transformation to the canvas.

        Args:
            operation (str): The operation identifier (e.g., 'flip_horizontal').
        """
        operations = {
            'flip_horizontal': self.canva.flip_horizontal,
            'flip_vertical': self.canva.flip_vertical,
            'rotate_90_clockwise': self.canva.rotate_90_clockwise,
            'rotate_90_counterclockwise': self.canva.rotate_90_counterclockwise,
            'rotate_180': self.canva.rotate_180,
        }

        if func := operations.get(operation):
            func()
            self.draw_canva()

    def adjust_color_temperature(self, original_temp: float = 6500, target_temp: float = 6500, opacity: float = 1.0) -> None:
        """
        Apply color temperature adjustment.

        Args:
            original_temp (float): Source temperature in Kelvin.
            target_temp (float): Target temperature in Kelvin.
            opacity (float): Strength of the filter (0.0 - 1.0).
        """
        self.original_temp = original_temp
        self.target_temp = target_temp
        self.canva.adjust_color_temperature(original_temp, target_temp, opacity)
        self.draw_canva()

    def get_temperature_settings(self) -> Dict[str, float]:
        """Get current temperature settings."""
        return {
            'original_temp': self.original_temp,
            'target_temp': self.target_temp
        }

    def set_temperature_settings(self, original_temp: float, target_temp: float) -> None:
        """Set temperature settings without immediately applying."""
        self.original_temp = original_temp
        self.target_temp = target_temp

    # =========================================================================
    # I/O
    # =========================================================================

    def load_image(self, path: str) -> None:
        """
        Load a new image into this widget, replacing the current content.

        Args:
            path (str): File path to image.
        """
        # Note: This replaces the entire canvas logic in this widget
        try:
            img = LoaderPng(path).get_img()
            # Re-initialize Canva from this image
            self.canva = Canva.from_img(img)
            self.draw_canva()
        except Exception as e:
            print(f"Error loading image: {e}")

    # =========================================================================
    # Tool Management
    # =========================================================================

    def set_tool(self, tool) -> None:
        """
        Set the current active tool.

        Args:
            tool: The tool instance to use
        """
        self.current_tool = tool

    def mousePressEvent(self, event: QMouseEvent) -> None:
        """Handle mouse press events for tools"""
        if event.button() == Qt.MouseButton.LeftButton:
            pos = event.position().toPoint()
            
            # Check if clicking inside an active selection (for moving it)
            if self.canva.has_selection():
                selection_rect, selection_type = self.canva.get_selection()
                if selection_rect and selection_rect.contains(pos):
                    # Start moving the selection
                    self.moving_selection = True
                    self.move_start_point = QPoint(pos)
                    self._temp_selection_offset = QPoint(0, 0)
                    return
            
            # Otherwise, use the current tool
            if self.current_tool:
                self.current_tool.mouse_press(pos)
                
                # For drawing tools (not selection), apply immediately on press
                if self.canva.active_layer and not hasattr(self.current_tool, 'get_selection'):
                    self.current_tool.apply(pos, self.canva.active_layer)
                    self.draw_canva()
                
                self.update()

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        """Handle mouse move events for tools"""
        pos = event.position().toPoint()
        
        # Handle moving selection
        if self.moving_selection and self.move_start_point:
            self._temp_selection_offset = pos - self.move_start_point
            self.update()  # Redraw with temporary offset
            return
        
        # Otherwise, use the current tool
        if self.current_tool:
            # Call mouse_move to update tool state
            if self.canva.active_layer:
                self.current_tool.mouse_move(pos, self.canva.active_layer)
            
            # For drawing tools, apply the tool during mouse move when drawing
            if self.current_tool.is_drawing and self.canva.active_layer and not hasattr(self.current_tool, 'get_selection'):
                self.current_tool.apply(pos, self.canva.active_layer)
                self.draw_canva()
            
            self.update()

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        """Handle mouse release events for tools"""
        if event.button() == Qt.MouseButton.LeftButton:
            pos = event.position().toPoint()
            
            # Handle selection move completion
            if self.moving_selection and self.move_start_point:
                offset = pos - self.move_start_point
                
                # Only move if there's actual movement
                if not offset.isNull() and self.canva.active_layer:
                    selection_rect, selection_type = self.canva.get_selection()
                    if selection_rect:
                        # Calculate new top-left position
                        new_top_left = QPoint(selection_rect.x() + offset.x(), 
                                             selection_rect.y() + offset.y())
                        
                        # Move the selection content
                        self.canva.active_layer.move_selection(
                            selection_rect, 
                            new_top_left, 
                            selection_type, 
                            clear_source=True
                        )
                        
                        # Update selection rectangle to new position
                        new_rect = selection_rect.translated(offset)
                        self.canva.set_selection(new_rect, selection_type)
                        
                        self.draw_canva()
                
                self.moving_selection = False
                self.move_start_point = None
                self._temp_selection_offset = QPoint(0, 0)
                self.update()
                return
            
            # Otherwise, handle tool release
            if self.current_tool:
                self.current_tool.mouse_release(pos)
                
                # If using selection tool, save selection to canva
                if hasattr(self.current_tool, 'get_selection'):
                    selection = self.current_tool.get_selection()
                    if selection and not selection.isEmpty():
                        selection_type = 'ellipse' if 'Ellipse' in self.current_tool.name else 'rectangle'
                        self.canva.set_selection(selection, selection_type)
                
                self.update()
