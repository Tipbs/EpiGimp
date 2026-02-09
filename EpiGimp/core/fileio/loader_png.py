import cv2 as cv
import numpy as np
from EpiGimp.core.layer import Layer

class LoaderPng:
    def __init__(self, filename: str):
        try:
            with open(filename, 'rb') as f:
                file_bytes = np.frombuffer(f.read(), dtype=np.uint8)
            self.img = cv.imdecode(file_bytes, cv.IMREAD_UNCHANGED)
        except Exception as e:
            self.img = None
        assert self.img is not None, "Failed to load image"
        self.convert_to_RGBA()

    def convert_to_RGBA(self):
        if self.img.ndim == 2:
            self.img = cv.cvtColor(self.img, cv.COLOR_GRAY2RGBA)
        elif self.img.shape[2] == 3:
            self.img = cv.cvtColor(self.img, cv.COLOR_BGR2RGBA)
        elif self.img.shape[2] == 4:
            self.img = cv.cvtColor(self.img, cv.COLOR_BGRA2RGBA)

    def get_layer(self):
        return Layer.from_img(self.img)

    def get_img(self):
        return self.img
