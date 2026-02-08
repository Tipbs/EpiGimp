import numpy as np
from typing import Tuple
import cv2 as cv


class Layer:
    def __init__(
            self, shape: Tuple[int, int] = (600, 400), color=(0, 0, 0, 0), name: str = "Layer", pixels = None
    ):
        self.shape = shape
        self.name: str = name
        self.visibility = True
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

        self.qimage = QImage(
            self.pixels.data, 
            self.width, 
            self.height, 
            self.width * 4,  # Bytes per line (stride)
            QImage.Format_RGBA8888
        )

    def get_painter(self):
        """Returns a QPainter active on THIS layer"""
        return QPainter(self.qimage)

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

    def get_visibility(self):
        return self.visibility

    def toggle_visibility(self):
        self.visibility = not self.visibility

    def flip_horizontal(self):
        self.pixels = cv.flip(self.pixels, 1)
    
    def flip_vertical(self):
        self.pixels = cv.flip(self.pixels, 0)
    
    def rotate_90_clockwise(self):
        self.pixels = cv.rotate(self.pixels, cv.ROTATE_90_CLOCKWISE)
        self.shape = (self.pixels.shape[0], self.pixels.shape[1])
    
    def rotate_90_counterclockwise(self):
        self.pixels = cv.rotate(self.pixels, cv.ROTATE_90_COUNTERCLOCKWISE)
        self.shape = (self.pixels.shape[0], self.pixels.shape[1])
    
    def rotate_180(self):
        self.pixels = cv.rotate(self.pixels, cv.ROTATE_180)

    def transform(self, matrix: np.ndarray = None, type: str = ""):
        if type == "flip_horizontal":
            self.flip_horizontal()
        elif type == "flip_vertical":
            self.flip_vertical()
        elif type == "rotate_90_cw":
            self.rotate_90_clockwise()
        elif type == "rotate_90_ccw":
            self.rotate_90_counterclockwise()
        elif type == "rotate_180":
            self.rotate_180()
        elif matrix is not None:
            h, w = self.shape
            self.pixels = cv.warpAffine(
                self.pixels, 
                matrix, 
                (w, h),
                borderMode=cv.BORDER_CONSTANT,
                borderValue=(0, 0, 0, 0)
            )
