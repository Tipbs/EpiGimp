import numpy as np
import cv2
import json
import struct
from typing import List, Dict, Tuple
from pathlib import Path

class FileLoader:
    def __init__(self, filename: str):
        self.filename = filename
        self.file_format = Path(filename).suffix.lower()

    def load_project(self) -> Tuple[List[Dict], Dict]:
        """Load project, returns (layers, metadata)"""
        if self.file_format == '.epigimp':
            return self._load_native_format()
        else:
            if self.file_format not in ['.png', '.jpg', '.jpeg', '.bmp', '.tiff']:
                raise ValueError(f"Unsupported file format for loading: {self.file_format}")
            return self._load_image_as_layer()

    def _load_native_format(self) -> Tuple[List[Dict], Dict]:
        """Load native EpiGimp format"""
        with open(self.filename, 'rb') as f:
            # Check magic number
            magic = f.read(8)
            if magic != b'EPIGIMP\x00':
                raise ValueError("Invalid EpiGimp file format")
            
            # Read version
            version = struct.unpack('<I', f.read(4))[0]
            if version != 1:
                raise ValueError(f"Unsupported file version: {version}")
            
            # Read metadata
            metadata_len = struct.unpack('<I', f.read(4))[0]
            metadata_json = f.read(metadata_len).decode('utf-8')
            metadata = json.loads(metadata_json)
            
            # Read number of layers
            num_layers = struct.unpack('<I', f.read(4))[0]
            
            # Read each layer
            layers = []
            for _ in range(num_layers):
                layer = self._read_layer(f)
                layers.append(layer)
            
            return layers, metadata

    def _read_layer(self, file) -> Dict:
        """Read a single layer from the file"""
        # Read layer metadata
        meta_len = struct.unpack('<I', file.read(4))[0]
        meta_json = file.read(meta_len).decode('utf-8')
        layer_meta = json.loads(meta_json)
        
        # Read layer data
        data_len = struct.unpack('<I', file.read(4))[0]
        serialized_data = file.read(data_len)
        layer_data = self.deserialize_layer(serialized_data)
        
        return {
            'name': layer_meta['name'],
            'visible': layer_meta['visible'],
            'opacity': layer_meta['opacity'],
            'blend_mode': layer_meta['blend_mode'],
            'position': tuple(layer_meta['position']),
            'data': layer_data
        }

    def deserialize_layer(self, data: bytes) -> np.ndarray:
        """Deserialize layer data back to numpy array"""
        # Read header length
        header_len = struct.unpack('<I', data[:4])[0]
        offset = 4
        
        # Read header
        header_json = data[offset:offset + header_len].decode('utf-8')
        header = json.loads(header_json)
        offset += header_len
        
        # Read array data
        array_data = data[offset:]
        
        # Reconstruct numpy array
        shape = tuple(header['shape'])
        dtype = np.dtype(header['dtype'])
        
        array = np.frombuffer(array_data, dtype=dtype).reshape(shape)
        return array.copy()  # Return a copy to avoid memory issues

    def _load_image_as_layer(self) -> Tuple[List[Dict], Dict]:
        """Load regular image as a single layer"""
        # Load image using OpenCV
        img = cv2.imread(self.filename, cv2.IMREAD_UNCHANGED)
        
        if img is None:
            raise ValueError(f"Could not load image: {self.filename}")
        
        # Convert BGR(A) to RGB(A)
        if len(img.shape) == 3:
            if img.shape[2] == 3:
                img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                # Add alpha channel
                alpha = np.ones((img.shape[0], img.shape[1], 1), dtype=img.dtype) * 255
                img = np.concatenate([img, alpha], axis=2)
            elif img.shape[2] == 4:
                img = cv2.cvtColor(img, cv2.COLOR_BGRA2RGBA)
        else:
            # Grayscale - convert to RGBA
            img = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
            alpha = np.ones((img.shape[0], img.shape[1], 1), dtype=img.dtype) * 255
            img = np.concatenate([img, alpha], axis=2)
        
        # Create layer
        layer = {
            'name': Path(self.filename).stem,
            'visible': True,
            'opacity': 1.0,
            'blend_mode': 'normal',
            'position': (0, 0),
            'data': img
        }
        
        metadata = {
            'created_from': self.filename,
            'original_format': self.file_format
        }
        
        return [layer], metadata