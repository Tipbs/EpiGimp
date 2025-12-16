import numpy as np
# import numpy.typing as npt


class Layer:
    def __init__(
        self, width: int, height: int, color=(0, 0, 0, 0), name: str = "Layer"
    ):
        self.width: int = width
        self.height: int = height
        self.name: str = name
        r, g, b, a = color
        self.pixels = np.zeros((height, width, 4), dtype=np.uint8)
        self.pixels[..., 0] = r
        self.pixels[..., 1] = g
        self.pixels[..., 2] = b
        self.pixels[..., 3] = a

    @classmethod
    def from_opencv(cls, img, name: str = "Layer"):
        cls.width, cls.height, _ = img.shape
        cls.name = name
        cls.pixels = img
