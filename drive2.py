import io
import os
from typing import List

from apiclient import discovery
# noinspection PyPackageRequirements
from googleapiclient.http import MediaIoBaseDownload
from oauth2client.service_account import ServiceAccountCredentials


class Drive2:
    SCOPES = ['https://www.googleapis.com/auth/drive.readonly.metadata',
              'https://www.googleapis.com/auth/drive.readonly',
              'https://www.googleapis.com/auth/drive.metadata']
    DRIVE = discovery.build('drive', 'v3',
                            credentials=ServiceAccountCredentials.from_json_keyfile_name('google-cloud.json', SCOPES))

    @classmethod
    def get_folders(cls) -> List[str]:
        main_folder: list = cls.DRIVE.files().list(q="name = 'celeb'").execute().get('files', list())
        if not main_folder:
            return list()
        sub_folders = cls.DRIVE.files().list(q=f"'{main_folder[0]['id']}' in parents").execute().get('files', list())
        return [folder['name'] for folder in sub_folders]

    @classmethod
    def folder_exists(cls, folder_name: str) -> bool:
        return folder_name in cls.get_folders()

    @classmethod
    def get_files(cls, folder_name: str) -> List[dict]:
        folder: list = cls.DRIVE.files().list(q=f"name = '{folder_name}'").execute().get('files', list())
        if not folder:
            return list()
        files: list = cls.DRIVE.files().list(q=f"'{folder[0]['id']}' in parents",
                                             pageSize=1000).execute().get('files', list())
        return files

    @classmethod
    def file_exists(cls, folder_name: str, file_name: str) -> bool:
        files = cls.get_files(folder_name)
        if not files:
            return False
        return file_name in [file['name'] for file in files]

    @classmethod
    def download(cls, folder_name: str):
        static_dir = f"flask_app/static/{folder_name}"
        os.makedirs(static_dir, exist_ok=True)
        files = cls.get_files(folder_name)
        for file in files:
            request = cls.DRIVE.files().get_media(fileId=file['id'])
            file_handle = io.FileIO(f"{static_dir}/{file['name']}", 'wb')
            downloader = MediaIoBaseDownload(file_handle, request)
            done = False
            while done is False:
                _, done = downloader.next_chunk()
        return

    @classmethod
    def rename(cls, file: dict, new_file_name) -> dict:
        new_title = {'name': new_file_name}
        file = cls.DRIVE.files().update(fileId=file['id'], body=new_title, fields='name').execute()
        return file
