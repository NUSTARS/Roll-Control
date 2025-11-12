from Stage import Stage
from PIL.Image import Image   # ✅ import the class, not the module


# Eliott 
class Orient(Stage):
    # IMU data: {"orient": [], "gravity": [], ...}
    def __init__(self, IMU_data: list, altimeter_data: list): # underscore is for python to know that its a constructor
        pass

    def open(self): pass
    def close(self): pass

    def process(self, image: Image) -> Image: # Look into libraries to see how to orient the image given stuff into the constructor 
        pass

