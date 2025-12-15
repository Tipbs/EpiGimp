import cv2

class LoaderPng:
    def __init__(self, filename: str):
        cv2.imread(filename, cv2.IMREAD_COLOR)

    def get_layer(self, )
