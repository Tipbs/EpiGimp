# tests for file I/O operations in EpiGimp
from EpiGimp.core.fileio.file_loader import FileLoader
import pytest

def test_load_project():
    # Assuming we have a test .epigimp file with known content
    test_file = "./tests/test_project.epigimp"
    
    # Create a FileLoader instance
    loader = FileLoader(test_file)
    
    # Load the project
    layers, metadata = loader.load_project()
    
    # Perform assertions based on expected content of the test file
    assert isinstance(layers, list), "Layers should be a list"
    assert isinstance(metadata, dict), "Metadata should be a dictionary" 
    assert len(layers) > 0, "There should be at least one layer" 
    

def test_load_invalid_file():
    # Test loading a file with an unsupported format
    with pytest.raises(ValueError):
        loader = FileLoader("./tests/invalid_file.txt")
        loader.load_project()
    
    # Test loading a file that does not exist
    with pytest.raises(FileNotFoundError):
        loader = FileLoader("./tests/non_existent_file.epigimp")
        loader.load_project()
