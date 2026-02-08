from abc import ABC, abstractmethod
from PySide6.QtCore import QPoint

from EpiGimp.core.layer import Layer

class BaseTool(ABC):
    def __init__(self, name: str = 'tool'):
        self.name = name
        self.is_drawing = False
        self.sprite


    def mouse_press(self, pos: QPoint):
        self.is_drawing = True


    def mouse_release(self, pos: QPoint):
        self.is_drawing = False


    def mouse_move(self, pos: QPoint, layer: Layer):
        if not self.is_drawing:
            return



    @abstractmethod
    def apply(self, document, layer_index=0, **kwargs):
        raise NotImplementedError
