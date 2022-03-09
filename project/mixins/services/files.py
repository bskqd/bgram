import asyncio
import os
import uuid
from typing import Any

from fastapi import UploadFile

from core.config import settings
from database.repository import BaseCRUDRepository


class FilesService:
    """
    Service class for working with files.
    """

    def __init__(self, db_repository: BaseCRUDRepository):
        self.db_repository = db_repository

    async def create_object_file(
            self,
            file_model: Any,
            file: UploadFile,
            **kwargs
    ) -> Any:
        """
        Creates an object of file_model class in database.
        """
        object_to_create_in_db = file_model(**kwargs)
        folder_to_save_file = object_to_create_in_db.folder_to_save
        loop = asyncio.get_running_loop()
        content_to_write = await file.read()
        filename = '_'.join([name_part for name_part in file.filename.split()])
        file_path = await loop.run_in_executor(
            None, self.write_file, folder_to_save_file, filename, content_to_write
        )
        object_to_create_in_db.file_path = file_path
        model_instance = await self.db_repository.create(object_to_create_in_db)
        await self.db_repository.commit()
        await self.db_repository.refresh(model_instance)
        return model_instance

    @staticmethod
    def write_file(folder_to_save_file: str, filename: str, content_to_write: bytes) -> str:
        """
        Creates file in media folder.
        """
        folder_to_save_file = os.path.join(settings.MEDIA_PATH, folder_to_save_file)
        os.makedirs(folder_to_save_file, exist_ok=True)
        full_path_to_save_file = os.path.join(folder_to_save_file, filename)
        if os.path.exists(full_path_to_save_file):
            path_to_save_file_without_extension, file_extension = os.path.splitext(full_path_to_save_file)
            path_to_save_file_without_extension = f'{path_to_save_file_without_extension}{uuid.uuid4().hex[:5]}'
            full_path_to_save_file = f'{path_to_save_file_without_extension}{file_extension}'
        with open(full_path_to_save_file, 'wb') as file:
            file.write(content_to_write)
        return full_path_to_save_file.replace(settings.MEDIA_PATH, '', 1)
