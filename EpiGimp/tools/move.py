from PySide6.QtCore import QPoint, QRect
from PySide6.QtGui import QPainter, QImage
import numpy as np

from EpiGimp.core.layer import Layer
from EpiGimp.tools.base_tool import BaseTool


class MoveSelection(BaseTool):
    """
    Move Selection Tool.
    
    Allows moving the content of a selected region to a new location.
    Works with active selections (rectangle or ellipse).
    """
    
    def __init__(self):
        super().__init__("Move Selection", "Move selected content")
        self.start_drag_point = None
        self.current_offset = QPoint(0, 0)
        self.selection_backup = None
        self.original_rect = None
        self.is_moving = False
        
    def mouse_press(self, pos: QPoint):
        """Start moving if clicked inside selection"""
        super().mouse_press(pos)
        self.start_drag_point = QPoint(pos)
        self.current_offset = QPoint(0, 0)
        
    def mouse_move(self, pos: QPoint, layer: Layer = None):
        """Update position while dragging"""
        if self.is_drawing and self.start_drag_point:
            # Calculate offset from start point
            self.current_offset = pos - self.start_drag_point
            
    def mouse_release(self, pos: QPoint):
        """Finalize the move"""
        super().mouse_release(pos)
        self.start_drag_point = None
        
    def apply(self, pos: QPoint, layer: Layer):
        """Move tool doesn't apply to layer directly - handled by canvas"""
        return None
    
    def get_offset(self):
        """Get the current drag offset"""
        return self.current_offset
    
    def reset_offset(self):
        """Reset the offset"""
        self.current_offset = QPoint(0, 0)


class Move(BaseTool):
    """
    Move Tool.
    
    Allows moving layer content or selected regions.
    """
    
    def __init__(self):
        super().__init__("Move", "Move layers or selections")
        self.start_drag_point = None
        self.original_pixels = None
        self.moving_selection = False
        
    def mouse_press(self, pos: QPoint):
        """Start moving"""
        super().mouse_press(pos)
        self.start_drag_point = QPoint(pos)
        
    def mouse_move(self, pos: QPoint, layer: Layer = None):
        """Update position while dragging"""
        if self.is_drawing and self.start_drag_point and layer:
            offset_x = pos.x() - self.start_drag_point.x()
            offset_y = pos.y() - self.start_drag_point.y()
            
    def mouse_release(self, pos: QPoint):
        """Finalize the move"""
        super().mouse_release(pos)
        self.start_drag_point = None
        
    def apply(self, pos: QPoint, layer: Layer):
        """Move doesn't directly apply - handled by canvas widget"""
        return None
