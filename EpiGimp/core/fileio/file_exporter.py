import cv2
import numpy as np

class FileExporter:
    def __init__(self, filename: str, layer: np.ndarray):
        self.filename = filename
        self.layer = layer
        
    def export(self):
        self.layer = cv2.cvtColor(self.layer, cv2.COLOR_RGBA2BGR)
        cv2.imwrite(self.filename, self.layer)