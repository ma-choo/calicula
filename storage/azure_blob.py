import configparser
import os
from typing import List
from azure.storage.blob import BlobServiceClient
from subcalendar import Subcalendar
from .backend_base import StorageBackend

class AzureBlobStorageBackend(StorageBackend):
    def __init__(self):
        # try azure app service env variables
        self.connection_string = os.getenv("AZURE_CONNECTION_STRING")
        self.container_name = os.getenv("AZURE_CONTAINER")

        # fallback to config file for local development
        if not self.connection_string or not self.container_name:
            config_path = os.path.expanduser("~/.config/calicula/config")
            config = configparser.ConfigParser()
            config.read(config_path)

            if not self.connection_string:
                self.connection_string = config.get("azure", "connection_string")

            if not self.container_name:
                self.container_name = config.get("azure", "container")

        service_client = BlobServiceClient.from_connection_string(self.connection_string)
        self.container_client = service_client.get_container_client(self.container_name)

    def read_all(self) -> List[Subcalendar]:
        subcalendars = []
        blobs = self.container_client.list_blobs()
        for blob in blobs:
            blob_client = self.container_client.get_blob_client(blob.name)
            data = blob_client.download_blob().readall().decode("utf-8")
            subcalendar = Subcalendar.from_blob(blob.name, data)
            subcalendars.append(subcalendar)
        return subcalendars

    def write(self, subcalendar: Subcalendar):
        data = subcalendar.to_blob()
        blob_client = self.container_client.get_blob_client(subcalendar.name)
        blob_client.upload_blob(data, overwrite=True)

    @property
    def name(self):
        return "azure"
