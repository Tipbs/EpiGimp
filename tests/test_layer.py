from EpiGimp.core.layer import *
from EpiGimp.core.fileio.loader_png import *
 
def test_create_layer():
    Layer((120, 120))
    # assert test.addition(2, 3) == 5

def test_create_layer_from_opencv():
    file = "./tests/output-onlinepngtools.png"
    img = LoaderPng(file).get_img()
    layer = Layer.from_img(img)
    print(layer)
    
