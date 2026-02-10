import numpy as np
import cv2 as cv
from PIL import Image
from PySide6.QtGui import QImage, QPainter
from typing import Tuple, Optional, Union, Dict, Any

class Layer:
    """
    Represents a single image layer containing pixel data and metadata.

    The layer manages a NumPy array (H, W, 4) for pixel data (RGBA) and 
    automatically synchronizes it with a QImage for rendering.
    """

    def __init__(
        self, 
        shape: Tuple[int, int] = (600, 400), 
        color: Tuple[int, int, int, int] = (0, 0, 0, 0), 
        name: str = "Layer", 
        pixels: Optional[np.ndarray] = None
    ) -> None:
        """
        Initialize a Layer.

        Args:
            shape (Tuple[int, int]): Dimensions (height, width). Used if pixels is None.
            color (Tuple[int, int, int, int]): Initial RGBA fill color.
            name (str): The display name of the layer.
            pixels (Optional[np.ndarray]): Existing numpy array to wrap. If provided, 'shape' and 'color' args are ignored.
        """
        self.name: str = name
        self.visibility: bool = True
        
        # Initialize Pixel Data
        if pixels is None:
            # Create new blank array
            # Note: shape passed as (height, width)
            self.shape = shape
            self.pixels = np.zeros((shape[0], shape[1], 4), dtype=np.uint8)
            # Fill color
            self.pixels[:] = color
        else:
            # Use provided pixels
            self.pixels = pixels
            
            # Ensure RGBA format
            if self.pixels.shape[2] == 3:
                # Convert RGB to RGBA
                h, w = self.pixels.shape[:2]
                rgba = np.zeros((h, w, 4), dtype=np.uint8)
                rgba[..., :3] = self.pixels
                rgba[..., 3] = 255
                self.pixels = rgba
            
            self.shape = (self.pixels.shape[0], self.pixels.shape[1])

        # Initialize QImage view
        self.qimage: QImage = QImage()
        self._update_qimage()

    def _update_qimage(self) -> None:
        """
        Refresh the QImage object to point to the current self.pixels array.
        
        Must be called whenever self.pixels is reassigned (e.g. after rotation/flip),
        as those operations often return a new memory buffer.
        """
        height, width = self.pixels.shape[:2]
        bytes_per_line = width * 4
        
        # QImage references the numpy array data directly. 
        # We must ensure the array stays alive (self.pixels holds the reference).
        self.qimage = QImage(
            self.pixels.data, 
            width, 
            height, 
            bytes_per_line, 
            QImage.Format.Format_RGBA8888
        )

    def get_painter(self) -> QPainter:
        """Returns a QPainter active on THIS layer's QImage."""
        return QPainter(self.qimage)

    # =========================================================================
    # Factory Methods
    # =========================================================================

    @classmethod
    def from_img(cls, img: Union[np.ndarray, Image.Image], name: str = "Layer") -> 'Layer':
        """Create a Layer from a numpy array or PIL Image."""
        if isinstance(img, Image.Image):
            img = np.array(img)
        return cls(img.shape[:2], pixels=img, name=name)
    
    @classmethod
    def from_loader_dict(cls, layer_dict: Dict[str, Any]) -> 'Layer':
        """Reconstruct a Layer from a saved project dictionary."""
        return cls(
            shape=layer_dict['data'].shape,
            pixels=layer_dict['data'],
            name=layer_dict.get('name', 'Layer')
        )

    # =========================================================================
    # Getters / Setters
    # =========================================================================

    def get_pixels(self) -> np.ndarray:
        """Get the raw numpy array (H, W, 4)."""
        return self.pixels

    def get_pil(self) -> Image.Image:
        """Get the layer as a PIL Image."""
        return Image.fromarray(self.pixels.astype('uint8'))

    def get_visibility(self) -> bool:
        return self.visibility

    def set_visibility(self, state: bool) -> None:
        self.visibility = state

    def set_name(self, name: str) -> None:
        self.name = name

    def toggle_visibility(self) -> None:
        self.visibility = not self.visibility

    # =========================================================================
    # Transformations
    # =========================================================================

    def flip_horizontal(self) -> None:
        """Flip the layer horizontally."""
        # cv.flip returns a new array, so we must update qimage
        self.pixels = cv.flip(self.pixels, 1)
        self._update_qimage()
    
    def flip_vertical(self) -> None:
        """Flip the layer vertically."""
        self.pixels = cv.flip(self.pixels, 0)
        self._update_qimage()
    
    def rotate_90_clockwise(self) -> None:
        """Rotate 90 degrees clockwise."""
        self.pixels = cv.rotate(self.pixels, cv.ROTATE_90_CLOCKWISE)
        self.shape = (self.pixels.shape[0], self.pixels.shape[1])
        self._update_qimage()
    
    def rotate_90_counterclockwise(self) -> None:
        """Rotate 90 degrees counter-clockwise."""
        self.pixels = cv.rotate(self.pixels, cv.ROTATE_90_COUNTERCLOCKWISE)
        self.shape = (self.pixels.shape[0], self.pixels.shape[1])
        self._update_qimage()
    
    def rotate_180(self) -> None:
        """Rotate 180 degrees."""
        self.pixels = cv.rotate(self.pixels, cv.ROTATE_180)
        self._update_qimage()

    def transform(self, matrix: Optional[np.ndarray] = None, type: str = "") -> None:
        """
        Apply a geometric transformation.

        Args:
            matrix (Optional[np.ndarray]): A 2x3 affine transformation matrix.
            type (str): A string identifier for standard transforms ('flip_horizontal', etc).
        """
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
            self._update_qimage()

    # =========================================================================
    # Color Adjustments
    # =========================================================================

    def kelvin_to_rgb(self, kelvin: float) -> np.ndarray:
        """
        Convert a color temperature (Kelvin) to RGB.
        Algorithm derived from Tanner Helland's work.
        
        Args:
            kelvin (float): Temperature in Kelvin (1000 to 40000).

        Returns:
            np.ndarray: RGB values [r, g, b] as floats (0-255).
        """
        temp = kelvin / 100.0
        
        # Calculate Red
        if temp <= 66:
            red = 255.0
        else:
            red = temp - 60
            red = 329.698727446 * (red ** -0.1332047592)
            red = max(0.0, min(255.0, red))
        
        # Calculate Green
        if temp <= 66:
            green = temp
            green = 99.4708025861 * np.log(green) - 161.1195681661
        else:
            green = temp - 60
            green = 288.1221695283 * (green ** -0.0755148492)
        green = max(0.0, min(255.0, green))
        
        # Calculate Blue
        if temp >= 66:
            blue = 255.0
        elif temp <= 19:
            blue = 0.0
        else:
            blue = temp - 10
            blue = 138.5177312231 * np.log(blue) - 305.0447927307
            blue = max(0.0, min(255.0, blue))
        
        return np.array([red, green, blue], dtype=np.float32)
    
    def adjust_color_temperature(self, original_temp: float = 6500, target_temp: float = 6500, opacity: float = 1.0) -> None:
        """
        Adjust the color temperature of the layer.

        This calculates a scaling factor between the original and target temperatures
        and multiplies the RGB channels of the layer.

        Args:
            original_temp (float): The assumed current temperature of the image.
            target_temp (float): The desired temperature.
            opacity (float): Blending factor (0.0 to 1.0).
        """
        if original_temp == target_temp or opacity <= 0:
            return
        
        # Normalize to 0-1 for ratio calculation
        original_rgb = self.kelvin_to_rgb(original_temp) / 255.0
        target_rgb = self.kelvin_to_rgb(target_temp) / 255.0
        
        # Avoid division by zero
        scale = target_rgb / (original_rgb + 1e-6)
        
        # Extract RGB channels (ignore Alpha for calculation)
        rgb = self.pixels[:, :, :3].astype(np.float32)
        
        # Apply scaling: Broadcasting scale [1, 1, 3] over image [H, W, 3]
        adjusted = rgb * scale[np.newaxis, np.newaxis, :]
        adjusted = np.clip(adjusted, 0, 255)
        
        # Blend based on opacity
        if opacity < 1.0:
            result = rgb * (1 - opacity) + adjusted * opacity
            self.pixels[:, :, :3] = result.astype(np.uint8)
        else:
            self.pixels[:, :, :3] = adjusted.astype(np.uint8)
            
        # Note: Since this modifies pixels in-place without reallocating, 
        # the QImage view remains valid, but calling update might be safer if implementation changes.
        # However, to be consistent with transform methods:
        self._update_qimage()
