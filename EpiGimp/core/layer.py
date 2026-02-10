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

    # =========================================================================
    # Selection Operations
    # =========================================================================

    def copy_selection(self, rect) -> Optional[np.ndarray]:
        """
        Copy pixels within a rectangular selection.

        Args:
            rect: QRect defining the selection bounds

        Returns:
            np.ndarray: Copied pixel data, or None if invalid
        """
        if rect is None or rect.isEmpty():
            return None

        x, y = rect.x(), rect.y()
        w, h = rect.width(), rect.height()

        # Ensure bounds are within image
        h_img, w_img = self.pixels.shape[:2]
        x = max(0, min(x, w_img - 1))
        y = max(0, min(y, h_img - 1))
        w = min(w, w_img - x)
        h = min(h, h_img - y)

        if w <= 0 or h <= 0:
            return None

        # Copy the selected region
        return self.pixels[y:y+h, x:x+w].copy()

    def delete_selection(self, rect, selection_type='rectangle') -> None:
        """
        Delete pixels within a selection (make transparent).

        Args:
            rect: QRect defining the selection bounds
            selection_type: 'rectangle' or 'ellipse'
        """
        if rect is None or rect.isEmpty():
            return

        x, y = rect.x(), rect.y()
        w, h = rect.width(), rect.height()

        # Ensure bounds are within image
        h_img, w_img = self.pixels.shape[:2]
        x = max(0, min(x, w_img - 1))
        y = max(0, min(y, h_img - 1))
        w = min(w, w_img - x)
        h = min(h, h_img - y)

        if w <= 0 or h <= 0:
            return

        if selection_type == 'ellipse':
            # Create elliptical mask
            cy, cx = h / 2, w / 2
            yy, xx = np.ogrid[:h, :w]
            mask = ((xx - cx) ** 2) / (cx ** 2) + ((yy - cy) ** 2) / (cy ** 2) <= 1
            # Apply mask: set alpha to 0 where mask is True
            self.pixels[y:y+h, x:x+w][mask] = [0, 0, 0, 0]
        else:
            # Rectangle: just clear the region
            self.pixels[y:y+h, x:x+w] = [0, 0, 0, 0]

        self._update_qimage()

    def fill_selection(self, rect, color: Tuple[int, int, int, int], selection_type='rectangle') -> None:
        """
        Fill pixels within a selection with a color.

        Args:
            rect: QRect defining the selection bounds
            color: RGBA color tuple (0-255)
            selection_type: 'rectangle' or 'ellipse'
        """
        if rect is None or rect.isEmpty():
            return

        x, y = rect.x(), rect.y()
        w, h = rect.width(), rect.height()

        # Ensure bounds are within image
        h_img, w_img = self.pixels.shape[:2]
        x = max(0, min(x, w_img - 1))
        y = max(0, min(y, h_img - 1))
        w = min(w, w_img - x)
        h = min(h, h_img - y)

        if w <= 0 or h <= 0:
            return

        if selection_type == 'ellipse':
            # Create elliptical mask
            cy, cx = h / 2, w / 2
            yy, xx = np.ogrid[:h, :w]
            mask = ((xx - cx) ** 2) / (cx ** 2) + ((yy - cy) ** 2) / (cy ** 2) <= 1
            # Apply color where mask is True
            self.pixels[y:y+h, x:x+w][mask] = color
        else:
            # Rectangle: fill the region
            self.pixels[y:y+h, x:x+w] = color

        self._update_qimage()

    def move_selection(self, source_rect, dest_point, selection_type='rectangle', clear_source=True) -> None:
        """
        Move pixels from source rectangle to destination point.

        Args:
            source_rect: QRect defining the source selection bounds
            dest_point: QPoint for the destination (top-left corner)
            selection_type: 'rectangle' or 'ellipse'
            clear_source: Whether to clear the source area after copying
        """
        if source_rect is None or source_rect.isEmpty():
            return

        # Copy the source selection
        copied_data = self.copy_selection(source_rect)
        if copied_data is None:
            return

        # Clear source if requested
        if clear_source:
            self.delete_selection(source_rect, selection_type)

        # Paste at destination
        dest_x, dest_y = dest_point.x(), dest_point.y()
        h, w = copied_data.shape[:2]
        
        # Ensure destination is within bounds
        h_img, w_img = self.pixels.shape[:2]
        dest_x = max(0, min(dest_x, w_img - 1))
        dest_y = max(0, min(dest_y, h_img - 1))
        
        # Adjust size if goes beyond bounds
        paste_w = min(w, w_img - dest_x)
        paste_h = min(h, h_img - dest_y)
        
        if paste_w <= 0 or paste_h <= 0:
            return

        if selection_type == 'ellipse':
            # Create elliptical mask for pasting
            cy, cx = paste_h / 2, paste_w / 2
            yy, xx = np.ogrid[:paste_h, :paste_w]
            mask = ((xx - cx) ** 2) / (cx ** 2) + ((yy - cy) ** 2) / (cy ** 2) <= 1
            # Paste only where mask is True
            self.pixels[dest_y:dest_y+paste_h, dest_x:dest_x+paste_w][mask] = copied_data[:paste_h, :paste_w][mask]
        else:
            # Rectangle: paste the entire region
            self.pixels[dest_y:dest_y+paste_h, dest_x:dest_x+paste_w] = copied_data[:paste_h, :paste_w]

        self._update_qimage()
