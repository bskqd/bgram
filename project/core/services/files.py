import abc
import asyncio
import os
import uuid
from typing import Type, Union

from fastapi import UploadFile

from core.config import SettingsABC
from core.database.repository import BaseDatabaseRepository
from core.dependencies.providers import provide_settings
from mixins.models import FileABC


class FilesServiceABC(abc.ABC):
    @abc.abstractmethod
    async def create_object_file(self, *args, **kwargs) -> FileABC:
        pass

    @abc.abstractmethod
    async def change_file(self, *args, **kwargs) -> FileABC:
        pass

    @abc.abstractmethod
    async def delete_file_object(self, *args, **kwargs):
        pass

    @abc.abstractmethod
    async def remove_file_from_filesystem(self, file_path: str):
        pass


class FilesService(FilesServiceABC):
    """
    Service class for working with files.
    """
    file_model: Type[FileABC] = None

    def __init__(self, db_repository: BaseDatabaseRepository, settings: SettingsABC = provide_settings()):
        self.db_repository = db_repository
        self.settings = settings

    async def create_object_file(self, file: UploadFile, **kwargs) -> FileABC:
        """
        Creates an object of file_model class in database.
        """
        object_to_create_in_db = self.file_model(**kwargs)
        file_path = await self.write_file(object_to_create_in_db.folder_to_save, file)
        object_to_create_in_db.file_path = file_path
        model_instance = await self.db_repository.create(object_to_create_in_db)
        await self.db_repository.commit()
        await self.db_repository.refresh(model_instance)
        return model_instance

    async def change_file(self, file_object: Union[FileABC, int], replacement_file: UploadFile) -> FileABC:
        """
        Changes file_path in file_object to new uploaded file.
        """
        if isinstance(file_object, int):
            file_object = await self.db_repository.get_one(self.file_model.id == file_object)
        new_file_path = await self.write_file(file_object.folder_to_save, replacement_file)
        file_path_to_remove = file_object.file_path
        file_object = await self.db_repository.update_object(file_object, file_path=new_file_path)
        await self.db_repository.commit()
        await self.db_repository.refresh(file_object)
        await self.remove_file_from_filesystem(file_path_to_remove)
        return file_object

    async def delete_file_object(self, file_object_to_delete: Union[FileABC, int]):
        """
        Deletes file object from db and removes file from filesystem.
        """
        if isinstance(file_object_to_delete, int):
            file_object_to_delete = await self.db_repository.get_one(self.file_model.id == file_object_to_delete)
        file_path_to_remove = file_object_to_delete.file_path
        await self.db_repository.delete(self.file_model.id == file_object_to_delete.id)
        await self.db_repository.commit()
        await self.remove_file_from_filesystem(file_path_to_remove)

    async def remove_file_from_filesystem(self, file_path: str):
        file_path_to_remove = os.path.join(self.settings.MEDIA_PATH, file_path)
        loop = asyncio.get_running_loop()
        if os.path.exists(file_path_to_remove):
            await loop.run_in_executor(None, os.remove, file_path_to_remove)

    async def write_file(self, folder_to_save_file: str, file: UploadFile) -> str:
        content_to_write = await file.read()
        filename = '_'.join(file.filename.split())
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(
            None, self.write_file_to_filesystem, folder_to_save_file, filename, content_to_write,
        )

    def write_file_to_filesystem(self, folder_to_save_file: str, filename: str, content_to_write: bytes) -> str:
        folder_to_save_file = os.path.join(self.settings.MEDIA_PATH, folder_to_save_file)
        os.makedirs(folder_to_save_file, exist_ok=True)
        full_path_to_save_file = os.path.join(folder_to_save_file, filename)
        if os.path.exists(full_path_to_save_file):
            path_to_save_file_without_extension, file_extension = os.path.splitext(full_path_to_save_file)
            path_to_save_file_without_extension = f'{path_to_save_file_without_extension}{uuid.uuid4().hex[:5]}'
            full_path_to_save_file = f'{path_to_save_file_without_extension}{file_extension}'
        with open(full_path_to_save_file, 'wb') as file:
            file.write(content_to_write)
        return full_path_to_save_file.replace(self.settings.MEDIA_PATH, '', 1)
