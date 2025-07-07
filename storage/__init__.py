import configparser
import os
from .local import LocalStorageBackend
from .azure_blob import AzureBlobStorageBackend

def get_backend():
    config_path = os.path.expanduser("~/.config/calicula/config")
    config = configparser.ConfigParser()
    config.read(config_path)

    backend_type = config.get("storage", "backend", fallback="local").lower()

    if backend_type == "azure":
        return AzureBlobStorageBackend()
    else:
        return LocalStorageBackend()
