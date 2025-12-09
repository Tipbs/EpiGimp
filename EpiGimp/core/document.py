from typing import List
from .layer import Layer
import numpy as np

class Document:
    def __init__(self, width: int = 800, height: int = 600, background=(255, 255, 255, 255)):
        self.width = width
        self.height = height
        self.layers: List[Layer] = []
        self.add_layer(name='Background', color=background)


    def add_layer(self, name: str = 'Layer', color=(0, 0, 0, 0)) -> Layer:
        layer = Layer(self.width, self.height, color, name=name)
        self.layers.append(layer)
        return layer


    def composite(self) -> np.ndarray:
# very simple alpha composite: base over
        out = np.zeros((self.height, self.width, 4), dtype=np.uint8)
        out[..., 3] = 255 # opaque base
        for layer in self.layers:
            src = layer.pixels.astype(np.float32) / 255.0
            dst = out.astype(np.float32) / 255.0
            alpha = src[..., 3:4]
            out = (src * alpha + dst * (1 - alpha)) * 255.0
        return out.astype(np.uint8)
