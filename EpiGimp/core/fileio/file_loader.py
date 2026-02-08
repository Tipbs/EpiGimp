import numpy as np
import json
import struct
from typing import List, Dict, Tuple
from pathlib import Path

class FileLoader:
    def __init__(self, filename: str):
        self.filename = filename
        self.file_format = Path(filename).suffix.lower()

    def load_project(self) -> Tuple[List[Dict], Dict]:
        if self.file_format != '.epigimp':
            raise ValueError("Unsupported file format: {}".format(self.file_format))
        return self._load_native_format()

    def _load_native_format(self) -> Tuple[List[Dict], Dict]:
        with open(self.filename, 'rb') as f:
            magic = f.read(8)
            if magic != b'EPIGIMP\x00':
                raise ValueError("Invalid EpiGimp file format")
            version = struct.unpack('<I', f.read(4))[0]
            if version != 1:
                raise ValueError(f"Unsupported file version: {version}")
            metadata_len = struct.unpack('<I', f.read(4))[0]
            metadata_json = f.read(metadata_len).decode('utf-8')
            metadata = json.loads(metadata_json)
            
            num_layers = struct.unpack('<I', f.read(4))[0]
            layers = []
            for _ in range(num_layers):
                layer = self._read_layer(f)
                layers.append(layer)
            
            return layers, metadata

    def _read_layer(self, file) -> Dict:
        meta_len = struct.unpack('<I', file.read(4))[0]
        meta_json = file.read(meta_len).decode('utf-8')
        layer_meta = json.loads(meta_json)
        
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
        header_len = struct.unpack('<I', data[:4])[0]
        offset = 4
        
        header_json = data[offset:offset + header_len].decode('utf-8')
        header = json.loads(header_json)
        offset += header_len
        
        array_data = data[offset:]
        
        shape = tuple(header['shape'])
        dtype = np.dtype(header['dtype'])
        
        array = np.frombuffer(array_data, dtype=dtype).reshape(shape)
        return array.copy()