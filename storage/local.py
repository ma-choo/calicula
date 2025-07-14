# storage/local.py

import os
from typing import List
from subcalendar import Subcalendar
from .backend_base import StorageBackend

SUBCAL_DIR = os.path.expanduser("~/.local/share/subcalendars")

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

    def rename(self, old_name: str, new_name: str):
        old_path = os.path.join(SUBCAL_DIR, old_name)
        new_path = os.path.join(SUBCAL_DIR, new_name)
        if os.path.exists(old_path):
            os.rename(old_path, new_path)

