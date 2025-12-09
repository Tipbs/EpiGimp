import numpy as np

class Layer:
    def __init__(self, width: int, height: int, color=(0, 0, 0, 0), name: str = 'Layer'):
        self.width = width
        self.height = height
        self.name = name
        r, g, b, a = color
        self.pixels = np.zeros((height, width, 4), dtype=np.uint8)
        self.pixels[..., 0] = r
        self.pixels[..., 1] = g
        self.pixels[..., 2] = b
        self.pixels[..., 3] = a
