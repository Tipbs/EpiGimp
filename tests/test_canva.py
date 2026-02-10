import pytest
import numpy as np
from PIL import Image
from EpiGimp.core.canva import Canva
from EpiGimp.core.layer import Layer
from EpiGimp.core.fileio.loader_png import LoaderPng
from datetime import datetime
import os


class TestCanvaCreation:
    def test_default_canva_creation(self):
        canva = Canva()
        assert canva.shape == (600, 800)
        assert len(canva.layers) == 1
        assert canva.layers[0].name == "Background"
        assert canva.active_layer is not None
    
    def test_custom_shape_canva(self):
        canva = Canva(shape=(100, 200))
        assert canva.shape == (100, 200)
        assert canva.layers[0].shape == (100, 200)
    
    def test_custom_background_color(self):
        canva = Canva(background=(255, 128, 64, 255))
        bg_layer = canva.layers[0]
        assert np.all(bg_layer.pixels[0, 0] == [255, 128, 64, 255])
    
    def test_canva_has_metadata(self):
        canva = Canva()
        assert 'width' in canva.metadata
        assert 'height' in canva.metadata
        assert 'datetime' in canva.metadata
    
    def test_canva_from_img(self):
        img = np.random.randint(0, 255, (100, 100, 4), dtype=np.uint8)
        canva = Canva.from_img(img, name="Test Image")
        assert canva.shape[:2] == (100, 100)
        assert len(canva.layers) == 1
        assert canva.layers[0].name == "Test Image"


class TestLayerManagement:
    def test_add_layer(self):
        canva = Canva()
        initial_count = len(canva.layers)
        layer = canva.add_layer(name="New Layer")
        assert len(canva.layers) == initial_count + 1
        assert layer.name == "New Layer"
        assert canva.active_layer == layer
    
    def test_add_layer_default_name(self):
        canva = Canva()
        layer1 = canva.add_layer()
        layer2 = canva.add_layer()
        assert "Layer #" in layer1.name
        assert "Layer #" in layer2.name
        assert layer1.name != layer2.name
    
    def test_add_layer_from_layer(self):
        canva = Canva()
        new_layer = Layer(shape=(100, 100), name="Custom Layer")
        canva.add_layer_from_layer(new_layer)
        assert new_layer in canva.layers
        assert canva.active_layer == new_layer
    
    def test_add_img_layer(self):
        canva = Canva()
        img = np.random.randint(0, 255, (100, 100, 4), dtype=np.uint8)
        layer = canva.add_img_layer(img)
        assert layer in canva.layers
        assert layer.shape[:2] == (100, 100)
    
    def test_set_active_layer(self):
        canva = Canva()
        canva.add_layer(name="Layer 1")
        canva.add_layer(name="Layer 2")
        canva.set_active_layer(0)
        assert canva.active_layer == canva.layers[0]
        canva.set_active_layer(1)
        assert canva.active_layer == canva.layers[1]
    
    def test_set_active_layer_invalid_index(self):
        canva = Canva()
        current_active = canva.active_layer
        canva.set_active_layer(100)
        assert canva.active_layer == current_active
    
    def test_del_layer(self):
        canva = Canva()
        canva.add_layer(name="Layer 1")
        canva.add_layer(name="Layer 2")
        initial_count = len(canva.layers)
        canva.del_layer(1)
        assert len(canva.layers) == initial_count - 1
        assert canva.active_layer is not None
    
    def test_del_layer_updates_active(self):
        canva = Canva()
        canva.add_layer(name="Layer 1")
        canva.add_layer(name="Layer 2")
        canva.set_active_layer(1)
        canva.del_layer(1)
        assert canva.active_layer in canva.layers
    
    def test_del_all_layers(self):
        canva = Canva()
        while len(canva.layers) > 0:
            canva.del_layer(0)
        assert len(canva.layers) == 0
        assert canva.active_layer is None
    
    def test_swap_layer_invalid_indices(self):
        canva = Canva()
        canva.add_layer(name="Layer 1")
        original_order = canva.layers.copy()
        canva.swap_layer(0, 100)
        assert canva.layers == original_order


class TestCompositing:
    def test_get_img_single_layer(self):
        canva = Canva(shape=(100, 100))
        result = canva.get_img()
        assert isinstance(result, Layer)
        assert result.shape == (100, 100)
    
    def test_get_img_multiple_layers(self):
        canva = Canva(shape=(100, 100))
        canva.add_layer(name="Layer 1", color=(255, 0, 0, 255))
        result = canva.get_img()
        assert isinstance(result, Layer)
    
    def test_composite_returns_array(self):
        canva = Canva(shape=(100, 100))
        canva.add_layer(name="Layer 1", color=(255, 0, 0, 128))
        result = canva.composite()
        assert isinstance(result, np.ndarray)
        assert result.shape == (100, 100, 4)
        assert result.dtype == np.uint8
    
    def test_composite_alpha_blending(self):
        canva = Canva(shape=(100, 100), background=(0, 0, 255, 255))
        layer = canva.add_layer(name="Red", color=(255, 0, 0, 128))
        result = canva.composite()
        # With 50% alpha red over blue, should get purple-ish result
        assert result[0, 0, 0] > 0  # Has some red
        assert result[0, 0, 2] > 0  # Has some blue


class TestTransformations:
    def test_flip_horizontal(self):
        canva = Canva(shape=(10, 10))
        canva.layers[0].pixels[0, 0] = [255, 0, 0, 255]
        canva.flip_horizontal()
        assert np.array_equal(canva.layers[0].pixels[0, -1, :3], [255, 0, 0])
    
    def test_flip_vertical(self):
        canva = Canva(shape=(10, 10))
        canva.layers[0].pixels[0, 0] = [255, 0, 0, 255]
        canva.flip_vertical()
        assert np.array_equal(canva.layers[0].pixels[-1, 0, :3], [255, 0, 0])
    
    def test_rotate_180(self):
        canva = Canva(shape=(10, 20))
        canva.layers[0].pixels[0, 0] = [255, 0, 0, 255]
        canva.rotate_180()
        assert canva.shape == (10, 20)
        assert np.array_equal(canva.layers[0].pixels[-1, -1, :3], [255, 0, 0])


class TestColorTemperature:
    def test_adjust_color_temperature_single_layer(self):
        canva = Canva(shape=(10, 10))
        canva.add_layer(color=(128, 128, 128, 255))
        original_bg = canva.layers[0].pixels.copy()
        canva.adjust_color_temperature(6500, 3200, layer_idx=1)
        # Only layer 1 should be affected
        assert np.array_equal(canva.layers[0].pixels, original_bg)
        assert canva.layers[1].pixels[0, 0, 0] >= 127
    
    def test_adjust_color_temperature_invalid_index(self):
        canva = Canva(shape=(10, 10))
        original = canva.layers[0].pixels.copy()
        canva.adjust_color_temperature(6500, 3200, layer_idx=100)
        # Nothing should change with invalid index
        assert np.array_equal(canva.layers[0].pixels, original)


class TestMetadata:
    def test_get_metadata(self):
        canva = Canva()
        metadata = canva.get_metadata()
        assert 'width' in metadata
        assert 'height' in metadata
        assert 'exif' in metadata
        assert 'xmp' in metadata
        assert 'iptc' in metadata
        assert metadata['width'] == 800
        assert metadata['height'] == 600
        assert metadata['layer_count'] == 1
    
    def test_set_metadata(self):
        canva = Canva()
        canva.set_metadata({
            'title': 'Test Title',
            'author': 'Test Author',
            'description': 'Test Description'
        })
        assert canva.metadata['title'] == 'Test Title'
        assert canva.metadata['author'] == 'Test Author'
        assert canva.metadata['description'] == 'Test Description'
    
    def test_set_metadata_resolution(self):
        canva = Canva()
        canva.set_metadata({
            'x_resolution': 300,
            'y_resolution': 300
        })
        assert canva.metadata['x_resolution'] == 300
        assert canva.metadata['y_resolution'] == 300
    
    def test_metadata_exif_structure(self):
        canva = Canva()
        metadata = canva.get_metadata()
        assert 'Exif.Image.ImageWidth' in metadata['exif']
        assert 'Exif.Image.ImageLength' in metadata['exif']
        assert 'Exif.Image.Software' in metadata['exif']
        assert metadata['exif']['Exif.Image.Software'] == 'EpiGimp 1.0.0'

class TestImageLoading:
    @pytest.fixture
    def sample_png(self, tmp_path):
        img = Image.new('RGBA', (100, 100), (255, 0, 0, 255))
        img_path = tmp_path / "test.png"
        img.save(img_path)
        return str(img_path)
    
    def test_load_image(self, sample_png):
        canva = Canva.load_image(sample_png)
        assert canva.shape[:2] == (100, 100)
        assert len(canva.layers) == 1
        assert canva.project_path == sample_png
    
    def test_add_layer_from_project(self, sample_png):
        canva = Canva(shape=(100, 100))
        initial_count = len(canva.layers)
        canva.add_layer_from_project(sample_png)
        assert len(canva.layers) == initial_count + 1


class TestEdgeCases:
    def test_empty_canva_get_img(self):
        canva = Canva.__new__(Canva)
        canva.shape = (100, 100)
        canva.layers = []
        canva.active_layer = None
        result = canva.get_img()
        assert isinstance(result, Layer)
        assert result.shape == (100, 100)
    
    def test_large_canva(self):
        canva = Canva(shape=(4000, 4000))
        assert canva.shape == (4000, 4000)
        assert canva.layers[0].shape == (4000, 4000)
    
    def test_small_canva(self):
        canva = Canva(shape=(1, 1))
        assert canva.shape == (1, 1)
        assert canva.layers[0].shape == (1, 1)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
