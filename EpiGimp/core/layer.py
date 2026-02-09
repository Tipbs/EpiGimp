from PySide6.QtGui import QImage
import numpy as np
from typing import Tuple
import cv2 as cv
from PIL import Image

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
            self.shape[1], 
            self.shape[0], 
            self.shape[1] * 4,  # Bytes per line (stride)
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

    def get_pil(self):
        return Image.fromarray(self.pixels.astype('uint8'))

    def get_visibility(self):
        return self.visibility

    def set_visibility(self, state: Bool):
        self.visibility = state

    def set_name(self, name: Bool):
        self.name = name

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
    
    def kelvin_to_rgb(self, kelvin):
        temp = kelvin / 100.0
        
        if temp <= 66:
            red = 255
        else:
            red = temp - 60
            red = 329.698727446 * (red ** -0.1332047592)
            red = max(0, min(255, red))
        
        if temp <= 66:
            green = temp
            green = 99.4708025861 * np.log(green) - 161.1195681661
        else:
            green = temp - 60
            green = 288.1221695283 * (green ** -0.0755148492)
        green = max(0, min(255, green))
        
        if temp >= 66:
            blue = 255
        elif temp <= 19:
            blue = 0
        else:
            blue = temp - 10
            blue = 138.5177312231 * np.log(blue) - 305.0447927307
            blue = max(0, min(255, blue))
        
        return np.array([red, green, blue], dtype=np.float32)
    
    def adjust_color_temperature(self, original_temp=6500, target_temp=6500, opacity=1.0):
        if original_temp == target_temp or opacity == 0:
            return
        
        original_rgb = self.kelvin_to_rgb(original_temp) / 255.0
        target_rgb = self.kelvin_to_rgb(target_temp) / 255.0
        
        scale = target_rgb / (original_rgb + 1e-6)
        
        rgb = self.pixels[:, :, :3].astype(np.float32) / 255.0
        
        adjusted = rgb * scale[np.newaxis, np.newaxis, :]
        adjusted = np.clip(adjusted, 0, 1)
        
        result = rgb * (1 - opacity) + adjusted * opacity
        
        self.pixels[:, :, :3] = (result * 255).astype(np.uint8)

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
