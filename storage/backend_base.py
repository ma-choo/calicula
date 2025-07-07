from abc import ABC, abstractmethod
from subcalendar import Subcalendar
from typing import List

class StorageBackend(ABC):
    @abstractmethod
    def read_all(self) -> List[Subcalendar]:
        pass

    @abstractmethod
    def write(self, subcalendar: Subcalendar):
        pass
