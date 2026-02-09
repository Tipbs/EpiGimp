from EpiGimp.core.canva import *
from EpiGimp.core.fileio.loader_png import *
 
def test_create_document():
    Canva((120, 120))
    # assert test.addition(2, 3) == 5

def test_create_document_from_opencv():
    file = "./tests/output-onlinepngtools.png"
    img = LoaderPng(file).get_img()
    doc = Canva.from_img(img)
    print(doc)

def test_get_img():
    file = "./tests/output-onlinepngtools.png"
    img1 = LoaderPng(file).get_img()
    img2 = LoaderPng(file).get_img()
    doc = Canva.from_img(img1)
    doc.add_img_layer(img2)
    doc.get_img()
