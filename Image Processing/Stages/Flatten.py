from Stage import Stage
from PIL.Image import Image   # ✅ import the class, not the module

class Flatten(Stage):
    # IMU data: {"orient": [], "gravity": [], ...}
    def __init__(self, IMU_data: list, altimeter_data: list):
        pass
    
    def open(self): pass
    def close(self): pass

    def process(self, image: Image) -> Image:
        return