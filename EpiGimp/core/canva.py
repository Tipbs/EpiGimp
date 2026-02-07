from functools import reduce
from typing import List, Dict, Any
import cv2 as cv

from EpiGimp.core.fileio.loader_png import LoaderPng
from .layer import Layer
import numpy as np
from typing import Tuple
from datetime import datetime

class Canva:
    def __init__(self, shape: Tuple[int, int] = (600, 800), background=(255, 255, 255, 255)):
        self.shape = shape
        self.layers: List[Layer] = []
        self.add_layer(name='Background', color=background)
        self.project_path = None
        self.metadata: Dict[str, Any] = {}
        self._init_metadata()

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
        canva = cls()
        canva.shape = layer.shape
        canva.layers: List[Layer] = []
        canva.add_layer_from_layer(layer)
        canva._init_metadata()
        return canva

    @classmethod
    def load_image(cls, path: str):
        canva = cls()
        img = LoaderPng(path).get_img()
        canva.from_img(img)
        canva = Canva.from_img(img)
        canva.project_path = path
        canva._init_metadata()
        return canva

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
        canva.project_path = filename
        canva.metadata = metadata.get('metadata', {})
        
        for layer_dict in layers_data:
            layer = Layer(pixels=layer_dict['data'], shape=layer_dict['data'].shape, name=layer_dict.get('name', 'Layer'))
            layer.visible = layer_dict.get('visible', True)
            layer.opacity = layer_dict.get('opacity', 1.0)
            layer.blend_mode = layer_dict.get('blend_mode', 'normal')
            layer.position = layer_dict.get('position', (0, 0))
            canva.layers.append(layer)
        
        canva._init_metadata()
        return canva

    def get_img(self) -> Layer:
        return reduce(lambda x, y: Layer(pixels=(cv.addWeighted(x.get_pixels(), 1, y.get_pixels(), 1, 0.0))), self.layers)
        # img = np.zeros((500, 500, 4), dtype=np.uint8)
        return Layer(pixels=(img))

    def composite(self) -> np.ndarray:
# very simple alpha composite: base over
        out = np.zeros((self.shape[0], self.shape[1], 4), dtype=np.uint8)
        out[..., 3] = 255 # opaque base
        for layer in self.layers:
            if layer.shape != self.shape:
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
        self.update_metadata_datetime()
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
        metadata = {
            'canvas_shape': self.shape,
            'metadata': self.metadata
        }
        file_saver.save_project(layers_data, metadata)
        self.project_path = filename
    
    def add_layer_from_project(self, filename: str):
        layer = Layer.from_img(LoaderPng(filename).get_img())
        self.add_layer_from_layer(layer)

    def _init_metadata(self):
        now = datetime.now()
        self.metadata = {
            'width': self.shape[1],
            'height': self.shape[0],
            'bits_per_sample': '8 8 8',
            'datetime': now.strftime('%Y:%m:%d %H:%M:%S'),
            'datetime_original': now.strftime('%Y:%m:%d %H:%M:%S'),
            'datetime_digitized': now.strftime('%Y:%m:%d %H:%M:%S'),
            'resolution_unit': 'inch',
            'x_resolution': 72,
            'y_resolution': 72,
            'color_space': 'sRGB',
            'offset_time': '+01:00',
            'offset_time_digitized': '+01:00',
            'offset_time_original': '+01:00',
            'title': '',
            'author': '',
            'author_title': '',
            'description': '',
            'description_writer': '',
            'keywords': '',
            'copyright': '',
            'copyright_url': '',
            'rating': 0,
            'exif': {},
            'xmp': {},
            'iptc': {}
        }

    def get_metadata(self) -> Dict[str, Any]:
        self.metadata['width'] = self.shape[1]
        self.metadata['height'] = self.shape[0]
        
        exif_data = {
            'Exif.Image.BitsPerSample': self.metadata.get('bits_per_sample', '8 8 8'),
            'Exif.Image.DateTime': self.metadata.get('datetime', datetime.now().strftime('%Y:%m:%d %H:%M:%S')),
            'Exif.Image.DateTimeOriginal': self.metadata.get('datetime_original', datetime.now().strftime('%Y:%m:%d %H:%M:%S')),
            'Exif.Image.ImageLength': self.shape[0],
            'Exif.Image.ImageWidth': self.shape[1],
            'Exif.Image.ResolutionUnit': self.metadata.get('resolution_unit', 'inch'),
            'Exif.Image.XResolution': self.metadata.get('x_resolution', 72),
            'Exif.Image.YResolution': self.metadata.get('y_resolution', 72),
            'Exif.Image.Software': 'EpiGimp 1.0.0',
            'Exif.Image.Copyright': self.metadata.get('copyright', ''),
            'Exif.Image.Artist': self.metadata.get('author', ''),
            'Exif.Image.ImageDescription': self.metadata.get('description', ''),
            'Exif.Photo.ColorSpace': self.metadata.get('color_space', 'sRGB'),
            'Exif.Photo.DateTimeDigitized': self.metadata.get('datetime_digitized', datetime.now().strftime('%Y:%m:%d %H:%M:%S')),
            'Exif.Photo.DateTimeOriginal': self.metadata.get('datetime_original', datetime.now().strftime('%Y:%m:%d %H:%M:%S')),
            'Exif.Photo.OffsetTime': self.metadata.get('offset_time', '+01:00'),
            'Exif.Photo.OffsetTimeDigitized': self.metadata.get('offset_time_digitized', '+01:00'),
            'Exif.Photo.OffsetTimeOriginal': self.metadata.get('offset_time_original', '+01:00'),
            'Exif.Photo.PixelXDimension': self.shape[1],
            'Exif.Photo.PixelYDimension': self.shape[0],
            'Exif.Image.Rating': self.metadata.get('rating', 0),
        }
        
        xmp_data = {
            'Xmp.tiff.ImageWidth': self.shape[1],
            'Xmp.tiff.ImageLength': self.shape[0],
            'Xmp.tiff.XResolution': f"{self.metadata.get('x_resolution', 72)}/1",
            'Xmp.tiff.YResolution': f"{self.metadata.get('y_resolution', 72)}/1",
            'Xmp.tiff.ResolutionUnit': '2' if self.metadata.get('resolution_unit') == 'inch' else '3',
            'Xmp.xmp.CreatorTool': 'EpiGimp 1.0.0',
            'Xmp.xmp.CreateDate': self.metadata.get('datetime_original', datetime.now().isoformat()),
            'Xmp.xmp.ModifyDate': self.metadata.get('datetime', datetime.now().isoformat()),
            'Xmp.xmp.Rating': self.metadata.get('rating', 0),
            'Xmp.dc.format': 'image/png',
            'Xmp.dc.title': self.metadata.get('title', ''),
            'Xmp.dc.creator': self.metadata.get('author', ''),
            'Xmp.dc.description': self.metadata.get('description', ''),
            'Xmp.dc.subject': self.metadata.get('keywords', ''),
            'Xmp.dc.rights': self.metadata.get('copyright', ''),
            'Xmp.photoshop.AuthorsPosition': self.metadata.get('author_title', ''),
            'Xmp.photoshop.CaptionWriter': self.metadata.get('description_writer', ''),
        }
        
        iptc_data = {
            'Iptc.Application2.RecordVersion': '4',
            'Iptc.Application2.DateCreated': self.metadata.get('datetime_original', datetime.now().strftime('%Y%m%d')),
            'Iptc.Application2.TimeCreated': datetime.now().strftime('%H%M%S+0000'),
            'Iptc.Application2.Byline': self.metadata.get('author', ''),
            'Iptc.Application2.BylineTitle': self.metadata.get('author_title', ''),
            'Iptc.Application2.Caption': self.metadata.get('description', ''),
            'Iptc.Application2.Writer': self.metadata.get('description_writer', ''),
            'Iptc.Application2.Keywords': self.metadata.get('keywords', ''),
            'Iptc.Application2.Copyright': self.metadata.get('copyright', ''),
        }
        
        if 'exif' in self.metadata and self.metadata['exif']:
            exif_data.update(self.metadata['exif'])
        if 'xmp' in self.metadata and self.metadata['xmp']:
            xmp_data.update(self.metadata['xmp'])
        if 'iptc' in self.metadata and self.metadata['iptc']:
            iptc_data.update(self.metadata['iptc'])
        
        return {
            **self.metadata,
            'exif': exif_data,
            'xmp': xmp_data,
            'iptc': iptc_data,
            'layer_count': len(self.layers),
            'project_path': self.project_path,
        }

    def set_metadata(self, metadata: Dict[str, Any]):
        self.metadata.update(metadata)
        
        if 'exif' in metadata:
            if 'exif' not in self.metadata:
                self.metadata['exif'] = {}
            self.metadata['exif'].update(metadata['exif'])
            
        if 'xmp' in metadata:
            if 'xmp' not in self.metadata:
                self.metadata['xmp'] = {}
            self.metadata['xmp'].update(metadata['xmp'])
            
        if 'iptc' in metadata:
            if 'iptc' not in self.metadata:
                self.metadata['iptc'] = {}
            self.metadata['iptc'].update(metadata['iptc'])
        
        if 'x_resolution' in metadata or 'y_resolution' in metadata:
            self.metadata['x_resolution'] = metadata.get('x_resolution', self.metadata.get('x_resolution', 72))
            self.metadata['y_resolution'] = metadata.get('y_resolution', self.metadata.get('y_resolution', 72))

    def update_metadata_datetime(self):
        now = datetime.now()
        self.metadata['datetime'] = now.strftime('%Y:%m:%d %H:%M:%S')
        
        if 'xmp' not in self.metadata:
            self.metadata['xmp'] = {}
        self.metadata['xmp']['Xmp.xmp.ModifyDate'] = now.isoformat()