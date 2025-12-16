import numpy as np
import cv2
import pickle
import json
import struct
from typing import List, Dict, Any
from pathlib import Path

class FileSaver:
    def __init__(self, filename: str):
        self.filename = filename
        self.file_format = Path(filename).suffix.lower()

    def save_project(self, layers: List[Dict], metadata: Dict = None):
        """Save project with layers in custom .epigimp format"""
        if self.file_format == '.epigimp':
            self._save_native_format(layers, metadata)
        else:
            if self.file_format not in ['.png', '.jpg', '.jpeg', '.bmp', '.tiff']:
                raise ValueError(f"Unsupported file format for export: {self.file_format}")
            self._save_flattened_image(layers)

    def _save_native_format(self, layers: List[Dict], metadata: Dict = None):
        """Save in native EpiGimp format with layers"""
        with open(self.filename, 'wb') as f:
            # Write file header
            f.write(b'EPIGIMP\x00')  # Magic number
            f.write(struct.pack('<I', 1))  # Version
            
            # Write metadata
            if metadata is None:
                metadata = {}
            metadata_json = json.dumps(metadata).encode('utf-8')
            f.write(struct.pack('<I', len(metadata_json)))
            f.write(metadata_json)
            
            # Write number of layers
            f.write(struct.pack('<I', len(layers)))
            
            # Write each layer
            for layer in layers:
                self._write_layer(f, layer)

    def _write_layer(self, file, layer: Dict):
        """Write a single layer to the file"""
        # Layer metadata
        layer_meta = {
            'name': layer.get('name', 'Layer'),
            'visible': layer.get('visible', True),
            'opacity': layer.get('opacity', 1.0),
            'blend_mode': layer.get('blend_mode', 'normal'),
            'position': layer.get('position', (0, 0))
        }
        
        # Write layer metadata
        meta_json = json.dumps(layer_meta).encode('utf-8')
        file.write(struct.pack('<I', len(meta_json)))
        file.write(meta_json)
        
        # Serialize and write layer data
        layer_data = layer['data']  # numpy array
        serialized_data = self.serialize_layer(layer_data)
        file.write(struct.pack('<I', len(serialized_data)))
        file.write(serialized_data)

    def serialize_layer(self, layer: np.ndarray) -> bytes:
        """Serialize numpy array layer data"""
        # Store shape and dtype info
        shape = layer.shape
        dtype = str(layer.dtype)
        
        # Create header
        header = {
            'shape': shape,
            'dtype': dtype
        }
        header_json = json.dumps(header).encode('utf-8')
        
        # Compress layer data
        layer_bytes = layer.tobytes()
        
        # Combine header length + header + data
        result = struct.pack('<I', len(header_json))
        result += header_json
        result += layer_bytes
        
        return result

    def _save_flattened_image(self, layers: List[Dict]):
        """Save as regular image format (PNG, JPG, etc.)"""
        # Flatten all visible layers
        flattened = self._flatten_layers(layers)
        
        # Convert RGBA to appropriate format
        if self.file_format in ['.jpg', '.jpeg']:
            # Convert RGBA to RGB for JPEG
            if flattened.shape[2] == 4:
                # Create white background
                rgb = np.ones((flattened.shape[0], flattened.shape[1], 3), dtype=np.uint8) * 255
                alpha = flattened[:, :, 3:4] / 255.0
                rgb = rgb * (1 - alpha) + flattened[:, :, :3] * alpha
                flattened = rgb.astype(np.uint8)
        
        # Save using OpenCV
        cv2.imwrite(self.filename, cv2.cvtColor(flattened, cv2.COLOR_RGBA2BGRA))

    def _flatten_layers(self, layers: List[Dict]) -> np.ndarray:
        """Flatten all visible layers into a single image"""
        if not layers:
            return np.zeros((600, 800, 4), dtype=np.uint8)
        
        # Get canvas size from first layer
        canvas_shape = layers[0]['data'].shape
        result = np.zeros(canvas_shape, dtype=np.float32)
        
        for layer in layers:
            if not layer.get('visible', True):
                continue
                
            layer_data = layer['data'].astype(np.float32) / 255.0
            opacity = layer.get('opacity', 1.0)
            
            # Apply opacity
            layer_data[:, :, 3] *= opacity
            
            # Simple alpha blending (can be extended for other blend modes)
            alpha = layer_data[:, :, 3:4]
            result = result * (1 - alpha) + layer_data * alpha
        
        return (result * 255).astype(np.uint8)
