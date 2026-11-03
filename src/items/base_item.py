
from abc import ABC, abstractmethod 


class BaseItem(ABC):
    def __init__(self, id: int, type: str):
        self.id = id
        self.type = type


        return

    @abstractmethod
    def display_info(self):
        pass