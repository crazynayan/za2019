import os
from typing import Dict, List

STATIC_FOLDER = 'flask_app/static'


def create_drive() -> Dict[str, List[str]]:
    drive: Dict[str, List[str]] = dict()
    for folder_name in os.listdir(STATIC_FOLDER):
        drive[folder_name] = [file[:-4] for file in os.listdir(f"{STATIC_FOLDER}/{folder_name}")
                              if file.endswith('.jpg')]
    return drive


class Drive:
    DRIVE = create_drive()

    @classmethod
    def get_folders(cls) -> List[str]:
        return list(cls.DRIVE)

    @classmethod
    def folder_exists(cls, folder_name: str) -> bool:
        return folder_name in cls.get_folders()

    @classmethod
    def get_files(cls, folder_name: str) -> List[str]:
        return cls.DRIVE[folder_name] if folder_name in cls.DRIVE else list()
