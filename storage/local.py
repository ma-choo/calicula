import os
from typing import List
from subcalendar import Subcalendar
from .backend_base import StorageBackend

SUBCAL_DIR = os.path.expanduser("~/.config/calicula/subcalendars")

if not os.path.exists(SUBCAL_DIR):
    os.makedirs(SUBCAL_DIR)


class LocalStorageBackend(StorageBackend):
    def read_all(self) -> List[Subcalendar]:
        return Subcalendar.read_all_local(SUBCAL_DIR)

    def write(self, subcalendar: Subcalendar):
        subcalendar.write_local(SUBCAL_DIR)

    @property
    def name(self):
        return "local"
