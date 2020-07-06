import datetime as dt

from google.cloud.storage import Client

from config import Config


class File:
    BUCKET = Client().bucket("za-2019")
    IMAGE_FOLDER = "images"
    DEFAULT_FILE = "SI001.jpg"

    @classmethod
    def url(cls, name: str) -> str:
        possible_file_names = [f"{name}.{ext}" for ext in Config.EXT]
        file_name = next((file for file in possible_file_names if cls.BUCKET.blob(file).exists), cls.DEFAULT_FILE)
        file_name = f"{cls.IMAGE_FOLDER}/{file_name}"
        url = cls.BUCKET.blob(file_name).generate_signed_url(version="v4", expiration=dt.timedelta(minutes=5))
        return url
