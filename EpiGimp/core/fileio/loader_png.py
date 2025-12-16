import cv2 as cv
from EpiGimp.core.layer import Layer

class LoaderPng:
    def __init__(self, filename: str):
        self.img = cv.imread(filename, cv.IMREAD_COLOR)
        assert self.img is not None, "File not found"

    def get_layer(self):
        return Layer.from_opencv(self.img)

    def get_img(self):
        return self.img
