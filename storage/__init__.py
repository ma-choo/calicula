import configparser
import os
from .local import LocalStorageBackend
from .azure_blob import AzureBlobStorageBackend

def get_backend():
    # try azure app service env variables
    backend_type = os.getenv("CALICULA_STORAGE_BACKEND")

    if backend_type is None:
        # fallback to config file for local development
        config_path = os.path.expanduser("~/.config/calicula/config")
        config = configparser.ConfigParser()
        config.read(config_path)
        backend_type = config.get("storage", "backend", fallback="local")

    backend_type = backend_type.lower()

    if backend_type == "azure":
        return AzureBlobStorageBackend()
    else:
        return LocalStorageBackend()
