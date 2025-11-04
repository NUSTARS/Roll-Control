from abc import ABC, abstractmethod

class Stage(ABC):

    @abstractmethod
    def open(self):
        pass

    @abstractmethod
    def close(self, arg1):
        pass

    @abstractmethod
    def operate(self, arg1):
        pass

    