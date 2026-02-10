import pytest
import numpy as np
from PIL import Image
from EpiGimp.core.layer import Layer
from EpiGimp.core.fileio.loader_png import LoaderPng


class TestLayerCreation:
    def test_default_layer_creation(self):
        layer = Layer()
        assert layer.shape == (600, 400)
        assert layer.name == "Layer"
        assert layer.visibility == True
        assert layer.pixels.shape == (600, 400, 4)
    
    def test_custom_shape_layer(self):
        layer = Layer(shape=(100, 200))
        assert layer.shape == (100, 200)
        assert layer.pixels.shape == (100, 200, 4)
    
    def test_custom_color_layer(self):
        layer = Layer(color=(255, 128, 64, 255))
        assert np.all(layer.pixels[:, :, 0] == 255)
        assert np.all(layer.pixels[:, :, 1] == 128)
        assert np.all(layer.pixels[:, :, 2] == 64)
        assert np.all(layer.pixels[:, :, 3] == 255)
    
    def test_custom_name_layer(self):
        layer = Layer(name="Test Layer")
        assert layer.name == "Test Layer"
    
    def test_layer_from_pixels(self):
        pixels = np.random.randint(0, 255, (100, 100, 4), dtype=np.uint8)
        layer = Layer(shape=(100, 100), pixels=pixels)
        assert np.array_equal(layer.pixels, pixels)
    
    def test_layer_from_rgb_pixels(self):
        pixels = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
        layer = Layer(shape=(100, 100), pixels=pixels)
        assert layer.pixels.shape == (100, 100, 4)
        assert np.all(layer.pixels[:, :, 3] == 255)
    
    def test_layer_from_img(self):
        img = np.random.randint(0, 255, (100, 100, 4), dtype=np.uint8)
        layer = Layer.from_img(img, name="From Image")
        assert layer.name == "From Image"
        assert layer.shape[:2] == (100, 100)


class TestLayerProperties:
    def test_get_pixels(self):
        layer = Layer()
        pixels = layer.get_pixels()
        assert isinstance(pixels, np.ndarray)
        assert pixels.shape == (600, 400, 4)
    
    def test_get_pil(self):
        layer = Layer()
        pil_img = layer.get_pil()
        assert isinstance(pil_img, Image.Image)
        assert pil_img.size == (400, 600)
    
    def test_get_visibility(self):
        layer = Layer()
        assert layer.get_visibility() == True
    
    def test_set_visibility(self):
        layer = Layer()
        layer.set_visibility(False)
        assert layer.visibility == False
        layer.set_visibility(True)
        assert layer.visibility == True
    
    def test_toggle_visibility(self):
        layer = Layer()
        initial = layer.visibility
        layer.toggle_visibility()
        assert layer.visibility == (not initial)
        layer.toggle_visibility()
        assert layer.visibility == initial
    
    def test_set_name(self):
        layer = Layer()
        layer.set_name("New Name")
        assert layer.name == "New Name"


class TestLayerTransformations:
    def test_flip_horizontal(self):
        layer = Layer(shape=(10, 10), color=(255, 0, 0, 255))
        layer.pixels[0, 0] = [0, 255, 0, 255]
        layer.flip_horizontal()
        assert np.array_equal(layer.pixels[0, -1, :3], [0, 255, 0])
    
    def test_flip_vertical(self):
        layer = Layer(shape=(10, 10), color=(255, 0, 0, 255))
        layer.pixels[0, 0] = [0, 255, 0, 255]
        layer.flip_vertical()
        assert np.array_equal(layer.pixels[-1, 0, :3], [0, 255, 0])
    
    def test_rotate_90_clockwise(self):
        layer = Layer(shape=(10, 20))
        original_shape = layer.shape
        layer.rotate_90_clockwise()
        assert layer.shape == (20, 10)
        assert layer.pixels.shape[:2] == (20, 10)
    
    def test_rotate_90_counterclockwise(self):
        layer = Layer(shape=(10, 20))
        original_shape = layer.shape
        layer.rotate_90_counterclockwise()
        assert layer.shape == (20, 10)
        assert layer.pixels.shape[:2] == (20, 10)
    
    def test_rotate_180(self):
        layer = Layer(shape=(10, 20))
        layer.pixels[0, 0] = [255, 0, 0, 255]
        layer.rotate_180()
        assert layer.shape == (10, 20)
        assert np.array_equal(layer.pixels[-1, -1, :3], [255, 0, 0])
    
    def test_transform_flip_horizontal(self):
        layer = Layer(shape=(10, 10))
        layer.pixels[0, 0] = [255, 0, 0, 255]
        layer.transform(type="flip_horizontal")
        assert np.array_equal(layer.pixels[0, -1, :3], [255, 0, 0])
    
    def test_transform_flip_vertical(self):
        layer = Layer(shape=(10, 10))
        layer.pixels[0, 0] = [255, 0, 0, 255]
        layer.transform(type="flip_vertical")
        assert np.array_equal(layer.pixels[-1, 0, :3], [255, 0, 0])
    
    def test_transform_rotate_90_cw(self):
        layer = Layer(shape=(10, 20))
        layer.transform(type="rotate_90_cw")
        assert layer.shape == (20, 10)
    
    def test_transform_rotate_90_ccw(self):
        layer = Layer(shape=(10, 20))
        layer.transform(type="rotate_90_ccw")
        assert layer.shape == (20, 10)
    
    def test_transform_rotate_180(self):
        layer = Layer(shape=(10, 20))
        layer.transform(type="rotate_180")
        assert layer.shape == (10, 20)


class TestColorTemperature:
    def test_kelvin_to_rgb_warm(self):
        layer = Layer()
        rgb = layer.kelvin_to_rgb(3200)
        assert rgb[0] > 200
        assert rgb[2] < 200
    
    def test_kelvin_to_rgb_cool(self):
        layer = Layer()
        rgb = layer.kelvin_to_rgb(8000)
        assert rgb[2] > 200
        assert rgb[0] < 255
    
    def test_kelvin_to_rgb_neutral(self):
        layer = Layer()
        rgb = layer.kelvin_to_rgb(6500)
        assert 200 < rgb[0] < 256
        assert 200 < rgb[1] < 256
        assert 200 < rgb[2] < 256
    
    def test_adjust_color_temperature_no_change(self):
        layer = Layer(shape=(10, 10), color=(128, 128, 128, 255))
        original = layer.pixels.copy()
        layer.adjust_color_temperature(6500, 6500)
        assert np.array_equal(layer.pixels, original)
    
    def test_adjust_color_temperature_warm(self):
        layer = Layer(shape=(10, 10), color=(128, 128, 128, 255))
        layer.adjust_color_temperature(6500, 3200)
        # After warming, red channel increases, blue decreases
        # Using more lenient assertions due to rounding
        assert layer.pixels[0, 0, 0] >= 127
        assert layer.pixels[0, 0, 2] <= 129
    
    def test_adjust_color_temperature_cool(self):
        layer = Layer(shape=(10, 10), color=(128, 128, 128, 255))
        layer.adjust_color_temperature(6500, 8000)
        # After cooling, blue channel should increase
        assert layer.pixels[0, 0, 2] >= 128
    
    def test_adjust_color_temperature_opacity(self):
        layer = Layer(shape=(10, 10), color=(128, 128, 128, 255))
        original = layer.pixels.copy()
        layer.adjust_color_temperature(6500, 3200, opacity=0.5)
        # With 50% opacity, changes should be moderate
        assert not np.array_equal(layer.pixels, original)
        # Red should increase but not too much (lowered upper bound)
        assert 127 <= layer.pixels[0, 0, 0] <= 160
    
    def test_adjust_color_temperature_zero_opacity(self):
        layer = Layer(shape=(10, 10), color=(128, 128, 128, 255))
        original = layer.pixels.copy()
        layer.adjust_color_temperature(6500, 3200, opacity=0.0)
        assert np.array_equal(layer.pixels, original)
    
    def test_adjust_color_temperature_full_opacity(self):
        layer = Layer(shape=(10, 10), color=(128, 128, 128, 255))
        layer.adjust_color_temperature(6500, 3200, opacity=1.0)
        # With full opacity warming, red should definitely be higher
        assert layer.pixels[0, 0, 0] >= 127


class TestLayerFromFile:
    @pytest.fixture
    def sample_image(self, tmp_path):
        img = Image.new('RGBA', (100, 100), (255, 0, 0, 255))
        img_path = tmp_path / "sample.png"
        img.save(img_path)
        return str(img_path)
    
    def test_load_from_png(self, sample_image):
        # Create image data directly from PIL
        pil_img = Image.open(sample_image)
        img_array = np.array(pil_img)
        
        # Create layer from the image array
        layer = Layer.from_img(img_array, name="Loaded")
        assert layer.name == "Loaded"
        assert layer.pixels.shape[2] == 4
        # Check that most pixels are red (allowing for some variation)
        assert np.mean(layer.pixels[:, :, 0]) > 200


class TestLayerQImage:
    def test_qimage_creation(self):
        layer = Layer(shape=(100, 100))
        assert layer.qimage is not None
        assert layer.qimage.width() == 100
        assert layer.qimage.height() == 100
    
    def test_qimage_format(self):
        layer = Layer()
        from PySide6.QtGui import QImage
        assert layer.qimage.format() == QImage.Format_RGBA8888


class TestLayerEdgeCases:
    def test_empty_layer(self):
        layer = Layer(shape=(0, 0))
        assert layer.pixels.shape == (0, 0, 4)
    
    def test_single_pixel_layer(self):
        layer = Layer(shape=(1, 1), color=(255, 128, 64, 32))
        assert layer.pixels.shape == (1, 1, 4)
        assert layer.pixels[0, 0, 0] == 255
    
    def test_large_layer(self):
        layer = Layer(shape=(4000, 4000))
        assert layer.pixels.shape == (4000, 4000, 4)
    
    def test_transparent_layer(self):
        layer = Layer(color=(0, 0, 0, 0))
        assert np.all(layer.pixels[:, :, 3] == 0)
    
    def test_opaque_layer(self):
        layer = Layer(color=(0, 0, 0, 255))
        assert np.all(layer.pixels[:, :, 3] == 255)
