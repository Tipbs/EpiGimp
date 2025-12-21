from functools import reduce
from typing import List
from .layer import Layer
import numpy as np
from typing import Tuple


class Canva:
    def __init__(self, shape: Tuple[int, int] = (600, 800), background=(255, 255, 255, 255)):
        self.shape = shape
        self.layers: List[Layer] = []
        self.add_layer(name='Background', color=background)


    def add_layer(self, name: str = 'Layer', color=(0, 0, 0, 0)) -> Layer:
        layer = Layer(self.shape, color, name=name)
        self.layers.append(layer)
        return layer

    def add_layer_from_layer(self, layer: Layer) -> Layer:
        self.layers.append(layer)
        return layer

    def add_img_layer(self, img) -> Layer:
        layer = Layer.from_img(img)
        self.add_layer_from_layer(layer)
        return layer

    @classmethod
    def from_img(cls, img):
        layer = Layer.from_img(img)
        doc = cls()
        doc.shape = layer.shape
        doc.layers: List[Layer] = []
        doc.add_layer_from_layer(layer)
        return doc

    def get_img(self) -> Layer:
        print(self.layers[0].shape)
        return reduce(lambda x, y: Layer(pixels=(cv.addWeighted(x.get_pixels(), 1, y.get_pixels(), 1, 0.0))), self.layers)
        # img = np.zeros((500, 500, 4), dtype=np.uint8)
        return Layer(pixels=(img))

    def composite(self) -> np.ndarray:
# very simple alpha composite: base over
        out = np.zeros((self.shape[0], self.shape[1], 4), dtype=np.uint8)
        out[..., 3] = 255 # opaque base
        for layer in self.layers:
            src = layer.pixels.astype(np.float32) / 255.0
            dst = out.astype(np.float32) / 255.0
            alpha = src[..., 3:4]
            out = (src * alpha + dst * (1 - alpha)) * 255.0
        return out.astype(np.uint8)
