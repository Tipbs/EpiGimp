from PySide6.QtCore import QPoint, QRect
from PySide6.QtGui import QPainter, QPen, Qt

from EpiGimp.core.layer import Layer
from EpiGimp.tools.base_tool import BaseTool


class RectangleSelection(BaseTool):
    """
    Rectangular Selection Tool.
    
    Allows selecting rectangular regions on a layer or canvas.
    Multiple layers can be selected as a group within the selection bounds.
    """
    
    def __init__(self):
        super().__init__("Rectangle Selection", "Select rectangular regions")
        self.start_point = None
        self.end_point = None
        self.current_selection = None
        
    def mouse_press(self, pos: QPoint):
        """Start creating a selection rectangle"""
        super().mouse_press(pos)
        self.start_point = QPoint(pos)
        self.end_point = QPoint(pos)
        self.current_selection = None
        
    def mouse_move(self, pos: QPoint, layer: Layer = None):
        """Update the selection rectangle as mouse moves"""
        if self.is_drawing and self.start_point:
            self.end_point = QPoint(pos)
            # Create rectangle from start to current position
            self.current_selection = self._create_rect()
            
    def mouse_release(self, pos: QPoint):
        """Finalize the selection rectangle"""
        if self.start_point:
            self.end_point = QPoint(pos)
            self.current_selection = self._create_rect()
        super().mouse_release(pos)
        
    def _create_rect(self):
        """Create a QRect from start and end points"""
        if not self.start_point or not self.end_point:
            return None
            
        x1, y1 = self.start_point.x(), self.start_point.y()
        x2, y2 = self.end_point.x(), self.end_point.y()
        
        # Ensure we always have valid coordinates (top-left to bottom-right)
        left = min(x1, x2)
        top = min(y1, y2)
        width = abs(x2 - x1)
        height = abs(y2 - y1)
        
        return QRect(left, top, width, height)
    
    def apply(self, pos: QPoint, layer: Layer):
        """
        Apply tool action - for selection tool, this returns the selection bounds
        rather than modifying the layer directly
        """
        # Selection tool doesn't directly modify pixels
        # Instead, it creates a selection region that can be used for other operations
        return self.current_selection
    
    def get_selection(self):
        """Get the current selection rectangle"""
        return self.current_selection
    
    def clear_selection(self):
        """Clear the current selection"""
        self.start_point = None
        self.end_point = None
        self.current_selection = None
    
    def has_selection(self):
        """Check if there's an active selection"""
        return self.current_selection is not None and not self.current_selection.isEmpty()


class EllipseSelection(BaseTool):
    """
    Elliptical Selection Tool.
    
    Allows selecting elliptical/circular regions on a layer or canvas.
    """
    
    def __init__(self):
        super().__init__("Ellipse Selection", "Select elliptical regions")
        self.start_point = None
        self.end_point = None
        self.current_selection = None
        
    def mouse_press(self, pos: QPoint):
        """Start creating a selection ellipse"""
        super().mouse_press(pos)
        self.start_point = QPoint(pos)
        self.end_point = QPoint(pos)
        self.current_selection = None
        
    def mouse_move(self, pos: QPoint, layer: Layer = None):
        """Update the selection ellipse as mouse moves"""
        if self.is_drawing and self.start_point:
            self.end_point = QPoint(pos)
            # Ellipse is defined by its bounding rectangle
            self.current_selection = self._create_rect()
            
    def mouse_release(self, pos: QPoint):
        """Finalize the selection ellipse"""
        if self.start_point:
            self.end_point = QPoint(pos)
            self.current_selection = self._create_rect()
        super().mouse_release(pos)
        
    def _create_rect(self):
        """Create a QRect bounding box for the ellipse"""
        if not self.start_point or not self.end_point:
            return None
            
        x1, y1 = self.start_point.x(), self.start_point.y()
        x2, y2 = self.end_point.x(), self.end_point.y()
        
        left = min(x1, x2)
        top = min(y1, y2)
        width = abs(x2 - x1)
        height = abs(y2 - y1)
        
        return QRect(left, top, width, height)
    
    def apply(self, pos: QPoint, layer: Layer):
        """Selection tool doesn't directly modify pixels"""
        return self.current_selection
    
    def get_selection(self):
        """Get the current selection ellipse bounding rectangle"""
        return self.current_selection
    
    def clear_selection(self):
        """Clear the current selection"""
        self.start_point = None
        self.end_point = None
        self.current_selection = None
    
    def has_selection(self):
        """Check if there's an active selection"""
        return self.current_selection is not None and not self.current_selection.isEmpty()
