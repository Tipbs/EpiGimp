from abc import ABC, abstractmethod
from PySide6.QtCore import QPoint

class BaseTool(ABC):
    def __init__(self, name: str = 'tool'):
        self.name = name
        self.is_drawing = False


    def mouse_press(self, pos: QPoint):
        self.is_drawing = True


    def mouse_release(self, pos: QPoint):
        self.is_drawing = False


    def mouse_move(self, pos: QPoint):
        pass


    @abstractmethod
    def apply(self, document, layer_index=0, **kwargs):
        raise NotImplementedError
