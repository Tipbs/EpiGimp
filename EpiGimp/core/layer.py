import numpy as np
from typing import Tuple
# import numpy.typing as npt


class Layer:
    def __init__(
            self, shape: Tuple[int, int] = (600, 400), color=(0, 0, 0, 0), name: str = "Layer", pixels = None
    ):
        self.shape = shape
        self.name: str = name
        if pixels is None:
            r, g, b, a = color
            self.pixels = np.zeros((shape[0], shape[1], 4), dtype=np.uint8)
            self.pixels[..., 0] = r
            self.pixels[..., 1] = g
            self.pixels[..., 2] = b
            self.pixels[..., 3] = a
        else:
            self.pixels = pixels
            if self.pixels.shape[2] == 3:
                rgba = np.zeros((self.shape[0], self.shape[1], 4), dtype=np.uint8)
                rgba[..., :3] = self.pixels
                rgba[..., 3] = 255
                self.pixels = rgba

    @classmethod
    def from_img(cls, img, name: str = "Layer"):
        layer = cls(img.shape, pixels=img, name=name)
        return layer
    
    def from_loader_dict(cls, layer_dict: dict):
        layer = cls(
            shape=layer_dict['data'].shape,
            pixels=layer_dict['data'],
            name=layer_dict.get('name', 'Layer')
        )
        return layer

    def get_pixels(self):
        return self.pixels
