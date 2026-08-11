import base64
import os
import requests

from django.core.files.storage import Storage
from django.core.files.base import ContentFile


class ImgBBStorage(Storage):
    """
    Uploads Django images directly to ImgBB.
    """

    def __init__(self):
        self.api_key = os.environ.get(
            "IMGBB_API_KEY",
            "b15da317474447e69e6859a9ad6ba545"
        )

    def _save(self, name, content):
        try:
            file_data = content.read()

            encoded_image = base64.b64encode(file_data).decode("utf-8")

            response = requests.post(
                "https://api.imgbb.com/1/upload",
                data={
                    "key": self.api_key,
                    "image": encoded_image,
                    "name": os.path.basename(name),
                },
                timeout=60,
            )

            response.raise_for_status()

            result = response.json()

            if not result.get("success"):
                raise Exception(
                    result.get("error", {}).get(
                        "message",
                        "ImgBB upload failed."
                    )
                )

            return result["data"]["url"]

        except requests.RequestException as e:
            raise Exception(f"ImgBB upload failed: {e}")

    def _open(self, name, mode="rb"):
        response = requests.get(name, timeout=60)
        response.raise_for_status()

        return ContentFile(response.content)

    def exists(self, name):
        return False

    def url(self, name):
        return name

    def delete(self, name):
        pass

    def deconstruct(self):
        """
        Allows Django migrations to serialize this storage class.
        """
        return (
            f"{self.__class__.__module__}.{self.__class__.__name__}",
            [],
            {},
        )