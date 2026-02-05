import numpy as np
import cv2
import pickle
import json
import struct
from typing import List, Dict, Any
from pathlib import Path

class FileSaver:
    def __init__(self, filename: str):
        if not filename.endswith('.epigimp'):
            filename+= '.epigimp'
        self.filename = filename
        self.file_format = Path(filename).suffix.lower()

    def save_project(self, layers: List[Dict], metadata: Dict = None):
        self._save_native_format(layers, metadata)

    def _save_native_format(self, layers: List[Dict], metadata: Dict = None):
        with open(self.filename, 'wb') as f:
            f.write(b'EPIGIMP\x00') 
            f.write(struct.pack('<I', 1))
            
            if metadata is None:
                metadata = {}
            metadata_json = json.dumps(metadata).encode('utf-8')
            f.write(struct.pack('<I', len(metadata_json)))
            f.write(metadata_json)
            
            f.write(struct.pack('<I', len(layers)))
            
            for layer in layers:
                self._write_layer(f, layer)

    def _write_layer(self, file, layer: Dict):
        layer_meta = {
            'name': layer.get('name', 'Layer'),
            'visible': layer.get('visible', True),
            'opacity': layer.get('opacity', 1.0),
            'blend_mode': layer.get('blend_mode', 'normal'),
            'position': layer.get('position', (0, 0))
        }
        meta_json = json.dumps(layer_meta).encode('utf-8')
        file.write(struct.pack('<I', len(meta_json)))
        file.write(meta_json)
        
        layer_data = layer['data']
        serialized_data = self.serialize_layer(layer_data)
        file.write(struct.pack('<I', len(serialized_data)))
        file.write(serialized_data)

    def serialize_layer(self, layer: np.ndarray) -> bytes:
        shape = layer.shape
        dtype = str(layer.dtype)
        
        header = {
            'shape': shape,
            'dtype': dtype
        }
        header_json = json.dumps(header).encode('utf-8')
        
        layer_bytes = layer.tobytes()
        result = struct.pack('<I', len(header_json))
        result += header_json
        result += layer_bytes
        
        return result