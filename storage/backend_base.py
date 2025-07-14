# storage/backend_base.py

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

    @abstractmethod
    def rename(self, old_name: str, new_name: str):
        """Rename a subcalendar from old_name to new_name in storage."""
        pass

