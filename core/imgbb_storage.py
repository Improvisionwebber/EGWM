import base64
import os
from io import BytesIO

import requests
from PIL import Image, ImageOps

from django.core.files.storage import Storage
from django.core.files.base import ContentFile


class ImgBBStorage(Storage):
    """
    Uploads optimized Django images directly to ImgBB.
    Images are resized and compressed before upload.
    """

    MAX_SIZE = 2000
    JPEG_QUALITY = 82
    WEBP_QUALITY = 82

    def __init__(self):
        self.api_key = os.environ.get(
            "IMGBB_API_KEY",
            "b15da317474447e69e6859a9ad6ba545"
        )

    def _optimize_image(self, content):
        """
        Resize and compress an uploaded image before sending it to ImgBB.
        """

        content.seek(0)

        try:
            image = Image.open(content)

            # Fix images taken on phones/cameras that use EXIF rotation.
            image = ImageOps.exif_transpose(image)

            # Don't allow extremely large images.
            image.thumbnail(
                (self.MAX_SIZE, self.MAX_SIZE),
                Image.Resampling.LANCZOS
            )

            original_format = image.format

            output = BytesIO()

            # Keep transparency for PNG images such as logos, QR codes, etc.
            if image.mode in ("RGBA", "LA") or (
                image.mode == "P" and "transparency" in image.info
            ):
                image.save(
                    output,
                    format="PNG",
                    optimize=True
                )

            elif original_format == "PNG":
                image = image.convert("RGB")
                image.save(
                    output,
                    format="JPEG",
                    quality=self.JPEG_QUALITY,
                    optimize=True
                )

            else:
                # JPEG/WebP/other normal photos become WebP.
                if image.mode != "RGB":
                    image = image.convert("RGB")

                image.save(
                    output,
                    format="WEBP",
                    quality=self.WEBP_QUALITY,
                    method=6
                )

            output.seek(0)

            return ContentFile(
                output.read(),
                name=content.name
            )

        except Exception:
            # If Pillow cannot process the file, return the original.
            content.seek(0)
            return content

    def _save(self, name, content):
        try:
            # Optimize before uploading to ImgBB.
            content = self._optimize_image(content)

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