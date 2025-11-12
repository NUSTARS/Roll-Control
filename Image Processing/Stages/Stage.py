from abc import ABC, abstractmethod
from PIL.Image import Image

class Stage(ABC):
    # IMU data: {"orient": [], "gravity": [], ...}
    def __init__(self, IMU_data: dict, altimeter_data: list):
        pass

    @abstractmethod
    def open(self):
        pass

    @abstractmethod
    def close(self):
        pass

    @abstractmethod
    def process(self, image : Image) -> Image:
        pass

    