import typing
from typing import List, Dict, Any, Tuple, Optional, Union
from functools import reduce
from datetime import datetime

import cv2 as cv
import numpy as np
from PIL import Image

from EpiGimp.core.fileio.loader_png import LoaderPng
# Assuming 'from .layer import Layer' refers to a sibling file
from .layer import Layer 

# Import strictly for type checking to avoid circular imports at runtime
if typing.TYPE_CHECKING:
    pass

class Canva:
    """
    The core Canvas class representing an image project.

    It manages a stack of :class:`Layer` objects, handles global transformations,
    metadata, and rendering (compositing) the final image.
    """

    # Class-level counter default, can be overridden per instance
    _global_count = 0

    def __init__(self, shape: Tuple[int, int] = (600, 800), background: Tuple[int, int, int, int] = (0, 0, 0, 255)) -> None:
        """
        Initialize a new Canvas.

        Args:
            shape (Tuple[int, int]): The dimensions of the canvas (height, width).
            background (Tuple[int, int, int, int]): RGBA color for the initial background layer.
        """
        self.shape = shape  # (height, width) usually, but code usage suggests (height, width)
        self.layers: List[Layer] = []
        self.active_layer: Optional[Layer] = None

        # Instance specific counter for layer naming
        self.layer_count = 0

        # Initialize background
        self.add_layer(name='Background', color=background)

        self.project_path: Optional[str] = None
        self.metadata: Dict[str, Any] = {}
        self._init_metadata()

    def default_name(self) -> str:
        """Generate a default name for a new layer (e.g., 'Layer #1')."""
        name = f"Layer #{self.layer_count}"
        self.layer_count += 1
        return name

    # =========================================================================
    # Layer Management
    # =========================================================================

    def set_active_layer(self, idx: int) -> None:
        """
        Set the active layer by index.

        Args:
            idx (int): The index of the layer to activate.
        """
        if not self.layers:
            self.active_layer = None
            return

        if 0 <= idx < len(self.layers):
            self.active_layer = self.layers[idx]

    def swap_layer(self, fst: int, snd: int) -> None:
        """
        Swap the positions of two layers in the stack.

        Args:
            fst (int): Index of the first layer.
            snd (int): Index of the second layer.
        """
        if 0 <= fst < len(self.layers) and 0 <= snd < len(self.layers):
            self.layers[fst], self.layers[snd] = self.layers[snd], self.layers[fst]

    def del_layer(self, idx: int) -> None:
        """
        Delete a layer at the specified index and reassign the active layer.

        Args:
            idx (int): Index of the layer to delete.
        """
        if not (0 <= idx < len(self.layers)):
            return

        del self.layers[idx]

        if not self.layers:
            self.active_layer = None
        elif idx < len(self.layers):
            # Select the layer that took the place of the deleted one
            self.active_layer = self.layers[idx]
        else:
            # If we deleted the last layer, select the new last layer
            self.active_layer = self.layers[idx - 1]

    def add_layer(self, name: Optional[str] = None, color: Tuple[int, int, int, int] = (0, 0, 0, 0)) -> Layer:
        """
        Create and add a new solid color layer.

        Args:
            name (Optional[str]): Name of the layer. Defaults to auto-generated.
            color (Tuple[int, int, int, int]): RGBA color tuple.

        Returns:
            Layer: The newly created layer.
        """
        if not name:
            name = self.default_name()

        layer = Layer(self.shape, color, name=name)
        self.layers.append(layer)
        self.active_layer = layer
        return layer

    def add_layer_from_layer(self, layer: Layer) -> Layer:
        """
        Add an existing Layer object to the canvas.

        Args:
            layer (Layer): The layer object to add.

        Returns:
            Layer: The added layer.
        """
        self.layers.append(layer)
        self.active_layer = layer
        return layer

    def add_img_layer(self, img: Union[np.ndarray, Image.Image], name: Optional[str] = None) -> Layer:
        """
        Create a layer from an image source (numpy array or PIL Image).

        Args:
            img: Source image data.
            name (Optional[str]): Layer name.

        Returns:
            Layer: The newly created layer.
        """
        if not name:
            name = self.default_name()

        layer = Layer.from_img(img, name)
        # layer.shape = (layer.shape[1], layer.shape[0])
        self.add_layer_from_layer(layer)
        return layer

    # =========================================================================
    # Factory Methods & I/O
    # =========================================================================

    @classmethod
    def from_img(cls, img: Union[np.ndarray, Image.Image], name: str = "Layer") -> 'Canva':
        """
        Factory method: Create a Canvas initialized with a single image layer.
        Sets the canvas shape to match the image dimensions.
        """
        layer = Layer.from_img(img, name)
        canva = cls()
        # Shape is (height, width)
        canva.shape = layer.shape 
        print("from_img", canva.shape)
        canva.layers = []  # Clear default background
        canva.add_layer_from_layer(layer)
        canva._init_metadata()
        return canva

    @classmethod
    def load_image(cls, path: str) -> 'Canva':
        """
        Factory method: Load an image from a file path into a new Canvas.
        """
        # LoaderPng presumably returns a PIL Image or Numpy Array
        img = LoaderPng(path).get_img() 
        canva = cls.from_img(img, path)
        canva.project_path = path
        canva._init_metadata()
        return canva

    @classmethod
    def from_project(cls, filename: str) -> 'Canva':
        """
        Factory method: Load a full project state from a custom file format (.epigimp).

        Args:
            filename (str): Path to the project file.
        """
        from .fileio.file_loader import FileLoader

        file_loader = FileLoader(filename)
        layers_data, metadata = file_loader.load_project()

        # Determine shape from metadata or fallback to first layer or default
        if 'canvas_shape' in metadata:
            shape = tuple(metadata['canvas_shape'])
        elif layers_data:
            shape = layers_data[0]['data'].shape[:2]
        else:
            shape = (600, 800)

        # Bypass __init__ to manually construct state
        canva = cls.__new__(cls)
        canva.shape = shape
        canva.layers = []
        canva.layer_count = 0 
        canva.project_path = filename
        canva.metadata = metadata.get('metadata', {})

        # Reconstruct layers
        for layer_dict in layers_data:
            layer = Layer(
                    pixels=layer_dict['data'], 
                    shape=layer_dict['data'].shape, 
                    name=layer_dict.get('name', 'Layer')
                    )
            layer.visible = layer_dict.get('visible', True)
            layer.opacity = layer_dict.get('opacity', 1.0)
            layer.blend_mode = layer_dict.get('blend_mode', 'normal')
            layer.position = layer_dict.get('position', (0, 0))
            canva.layers.append(layer)

            # Update internal counter to avoid name collisions on new layers
            # Simple heuristic: if name contains "Layer #", try to parse max index
            # For now, just incrementing roughly based on count
            canva.layer_count += 1

        # Set active layer to top-most if exists
        canva.active_layer = canva.layers[-1] if canva.layers else None

        canva._init_metadata()
        return canva

    def save_project(self, filename: str) -> None:
        """
        Save the current canvas state to a file.
        """
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

        metadata_export = {
                'canvas_shape': self.shape,
                'metadata': self.metadata
                }

        file_saver.save_project(layers_data, metadata_export)
        self.project_path = filename

    def add_layer_from_project(self, filename: str) -> None:
        """Import an image/project file as a new layer into the current canvas."""
        layer = Layer.from_img(LoaderPng(filename).get_img())
        self.add_layer_from_layer(layer)

    # =========================================================================
    # Compositing & Rendering
    # =========================================================================

    def composite_different_sizes(self, layer: Layer, position: Tuple[int, int] = (0, 0)) -> Image.Image:
        """
        Helper: Composites a layer (potentially smaller) onto a transparent 
        canvas matching the main canvas size.
        """
        # "RGBA" ensures transparency. (0, 0, 0, 0) is fully transparent.
        print("shape", self.shape)
        layer_h, layer_w = self.shape[0], self.shape[1]
        layer_canvas = Image.new("RGBA", (layer_w, layer_h), (0, 0, 0, 0))
        layer_canvas.paste(layer.get_pil(), position)
        return layer_canvas

    def get_image_for_compisition(self, layer: Layer) -> Image.Image:
        """
        Prepares a single layer for composition (handling visibility and resizing).
        """
        if not getattr(layer, 'visible', True):
            # Return fully transparent layer if hidden
            return Image.new("RGBA", (self.shape[1], self.shape[0]), (0, 0, 0, 0))

        layer_h, layer_w = layer.shape[0], layer.shape[1]

        # If sizes differ, expand the layer to match canvas bounds
        if (layer_h, layer_w) != self.shape:
            # Note: composite_different_sizes expects PIL image logic
            print("compositing")
            return self.composite_different_sizes(layer, getattr(layer, 'position', (0,0)))

        print("no compositing")
        return layer.get_pil()

    def get_img(self) -> Layer:
        """
        Render the final image using PIL's Alpha Composite.
        Returns the result as a flattened Layer object.
        """
        if not self.layers:
            return Layer(self.shape)

        # Reduce stack: Composite Layer 0 + Layer 1 -> Result + Layer 2 -> ...
        final_pil = reduce(
                lambda bottom, top: Image.alpha_composite(bottom, self.get_image_for_compisition(top)), 
                [self.get_image_for_compisition(self.layers[0])] + self.layers[1:]
                )

        # final_pil.show()
        return Layer(pixels=np.array(final_pil))

    def composite(self) -> np.ndarray:
        """
        Render the final image using NumPy-based manual alpha blending.

        Returns:
            np.ndarray: The flattened image as a numpy array (uint8).
        """
        # Initialize output buffer (transparent)
        out = np.zeros((self.shape[0], self.shape[1], 4), dtype=np.uint8)

        # Initialize base to opaque white or transparent? 
        # Original code sets alpha to 255 (Opaque Black effectively if RGB is 0)
        out[..., 3] = 255 

        for layer in self.layers:
            if not getattr(layer, 'visible', True):
                continue

            # Resize if necessary
            if layer.shape != self.shape:
                # cv.resize expects (width, height)
                resized = cv.resize(layer.pixels, (self.shape[1], self.shape[0]))
            else:
                resized = layer.pixels

            # Normalize to 0-1 float for blending math
            src = resized.astype(np.float32) / 255.0
            dst = out.astype(np.float32) / 255.0

            # Extract Alpha channel
            alpha = src[..., 3:4]

            # Standard "Source Over" composition
            # Out = Src * Alpha + Dst * (1 - Alpha)
            out_float = (src * alpha + dst * (1.0 - alpha)) * 255.0
            out = out_float.astype(np.uint8)

        return out

    # =========================================================================
    # Transformations
    # =========================================================================

    def flip_horizontal(self) -> None:
        """Apply horizontal flip to all layers."""
        self.active_layer.flip_horizontal()

    def flip_vertical(self) -> None:
        """Apply vertical flip to all layers."""
        self.active_layer.flip_vertical()

    def rotate_90_clockwise(self) -> None:
        """Rotate the canvas and all layers 90 degrees clockwise."""
        self.active_layer.rotate_90_clockwise()
        # Swap canvas dimensions
        # self.shape = (self.shape[1], self.shape[0])

    def rotate_90_counterclockwise(self) -> None:
        """Rotate the canvas and all layers 90 degrees counter-clockwise."""
        self.active_layer.rotate_90_counterclockwise()
        # Swap canvas dimensions
        # self.shape = (self.shape[1], self.shape[0])

    def rotate_180(self) -> None:
        """Rotate the canvas and all layers 180 degrees."""
        self.active_layer.rotate_180()

    def adjust_color_temperature(self, original_temp: int = 6500, target_temp: int = 6500, opacity: float = 1.0, layer_idx: Optional[int] = None) -> None:
        """
        Adjust color temperature for a specific layer or all layers.

        Args:
            original_temp (int): Original Kelvin temperature.
            target_temp (int): Target Kelvin temperature.
            opacity (float): Strength of the effect (0.0 to 1.0).
            layer_idx (Optional[int]): Index of layer to modify. If None, applies to all.
        """
        if layer_idx is not None:
            if 0 <= layer_idx < len(self.layers):
                self.layers[layer_idx].adjust_color_temperature(original_temp, target_temp, opacity)
        else:
            for layer in self.layers:
                layer.adjust_color_temperature(original_temp, target_temp, opacity)

    # =========================================================================
    # Metadata Handling
    # =========================================================================

    def _init_metadata(self) -> None:
        """Initialize default metadata schema."""
        now = datetime.now()
        date_str = now.strftime('%Y:%m:%d %H:%M:%S')

        self.metadata = {
                'width': self.shape[1],
                'height': self.shape[0],
                'bits_per_sample': '8 8 8',
                'datetime': date_str,
                'datetime_original': date_str,
                'datetime_digitized': date_str,
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

    def update_metadata_datetime(self) -> None:
        """Update modification timestamps in metadata."""
        now = datetime.now()
        self.metadata['datetime'] = now.strftime('%Y:%m:%d %H:%M:%S')
        if 'xmp' not in self.metadata:
            self.metadata['xmp'] = {}
        self.metadata['xmp']['Xmp.xmp.ModifyDate'] = now.isoformat()

    def set_metadata(self, metadata: Dict[str, Any]) -> None:
        """
        Merge new metadata into the existing metadata dictionary.

        Args:
            metadata (Dict[str, Any]): Dictionary of metadata keys to update.
        """
        self.metadata.update(metadata)

        # Deep merge specific nested dictionaries
        for key in ['exif', 'xmp', 'iptc']:
            if key in metadata:
                if key not in self.metadata:
                    self.metadata[key] = {}
                self.metadata[key].update(metadata[key])

        # Handle resolution specific updates
        if 'x_resolution' in metadata:
            self.metadata['x_resolution'] = metadata['x_resolution']
        if 'y_resolution' in metadata:
            self.metadata['y_resolution'] = metadata['y_resolution']

    def get_metadata(self) -> Dict[str, Any]:
        """
        Generate a standardized dictionary of metadata for export (EXIF, XMP, IPTC).

        Returns:
            Dict[str, Any]: The complete metadata structure.
        """
        # Refresh current dimensions
        self.metadata['width'] = self.shape[1]
        self.metadata['height'] = self.shape[0]

        current_time_str = datetime.now().strftime('%Y:%m:%d %H:%M:%S')

        # --- EXIF Mapping ---
        exif_data = {
                'Exif.Image.BitsPerSample': self.metadata.get('bits_per_sample', '8 8 8'),
                'Exif.Image.DateTime': self.metadata.get('datetime', current_time_str),
                'Exif.Image.DateTimeOriginal': self.metadata.get('datetime_original', current_time_str),
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
                'Exif.Photo.DateTimeDigitized': self.metadata.get('datetime_digitized', current_time_str),
                'Exif.Photo.DateTimeOriginal': self.metadata.get('datetime_original', current_time_str),
                'Exif.Photo.PixelXDimension': self.shape[1],
                'Exif.Photo.PixelYDimension': self.shape[0],
                'Exif.Image.Rating': self.metadata.get('rating', 0),
                }

        # --- XMP Mapping ---
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
                'Xmp.dc.rights': self.metadata.get('copyright', ''),
                }

        # --- IPTC Mapping ---
        iptc_data = {
                'Iptc.Application2.RecordVersion': '4',
                'Iptc.Application2.DateCreated': self.metadata.get('datetime_original', datetime.now().strftime('%Y%m%d')),
                'Iptc.Application2.TimeCreated': datetime.now().strftime('%H%M%S+0000'),
                'Iptc.Application2.Byline': self.metadata.get('author', ''),
                'Iptc.Application2.Caption': self.metadata.get('description', ''),
                'Iptc.Application2.Copyright': self.metadata.get('copyright', ''),
                }

        # Merge existing raw metadata blocks if they exist
        if self.metadata.get('exif'): exif_data.update(self.metadata['exif'])
        if self.metadata.get('xmp'): xmp_data.update(self.metadata['xmp'])
        if self.metadata.get('iptc'): iptc_data.update(self.metadata['iptc'])

        return {
                **self.metadata,
                'exif': exif_data,
                'xmp': xmp_data,
                'iptc': iptc_data,
                'layer_count': len(self.layers),
                'project_path': self.project_path,
                }
