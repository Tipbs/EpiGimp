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
        self.project_path = None


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

    @classmethod
    def from_project(cls, filename: str) -> 'Canva':
        from .fileio.file_loader import FileLoader
        file_loader = FileLoader(filename)
        layers_data, metadata = file_loader.load_project()
        
        if 'canvas_shape' in metadata:
            shape = tuple(metadata['canvas_shape'])
        elif layers_data:
            shape = layers_data[0]['data'].shape[:2]
        else:
            shape = (600, 800)
        
        canva = cls.__new__(cls)
        canva.shape = shape
        canva.layers = []
        
        for layer_dict in layers_data:
            layer = Layer(pixels=layer_dict['data'], shape=layer_dict['data'].shape, name=layer_dict.get('name', 'Layer'))
            layer.visible = layer_dict.get('visible', True)
            layer.opacity = layer_dict.get('opacity', 1.0)
            layer.blend_mode = layer_dict.get('blend_mode', 'normal')
            layer.position = layer_dict.get('position', (0, 0))
            canva.layers.append(layer)
        
        return canva

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
            if layer.shape != self.shape:
                import cv2 as cv
                resized = cv.resize(layer.pixels, (self.shape[1], self.shape[0]))
            else:
                resized = layer.pixels
            src = resized.astype(np.float32) / 255.0
            dst = out.astype(np.float32) / 255.0
            alpha = src[..., 3:4]
            out = (src * alpha + dst * (1 - alpha)) * 255.0
        return out.astype(np.uint8)

    def save_project(self, filename: str):
        from .fileio.file_saver import FileSaver
        file_saver = FileSaver(filename)
        layers_data = [
            {
                'name': layer.name,
                'visible': getattr(layer, 'visible', True),
                'opacity': getattr(layer, 'opacity', 1.0),
                'blend_mode': getattr(layer, 'blend_mode', 'normal'),
                'position': getattr(layer, 'position', (0, 0)),
                'data': layer.pixels
            }
            for layer in self.layers
        ]
        metadata = {'canvas_shape': self.shape}
        file_saver.save_project(layers_data, metadata)