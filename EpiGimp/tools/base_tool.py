from abc import ABC, abstractmethod
from PySide6.QtCore import QPoint

from EpiGimp.core.layer import Layer

class BaseTool(ABC):
    def __init__(self, name: str = 'tool', tooltip: str = 'tooltip'):
        self.name = name
        self.tooltip = tooltip
        self.is_drawing = False


    def mouse_press(self, pos: QPoint):
        self.is_drawing = True


    def mouse_release(self, pos: QPoint):
        self.is_drawing = False


    def mouse_move(self, pos: QPoint, layer: Layer):
        if not self.is_drawing:
            return

    @abstractmethod
    def apply(self, pos: QPoint, layer: Layer):
        raise NotImplementedError

class ToolNotImplemented(BaseTool):
    def __init__(self):
        super().__init__()

    def apply(self, pos: QPoint, layer: Layer):
        raise NotImplementedError
