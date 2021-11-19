import asyncio
import os
import uuid
from typing import Any, Optional, Type

from fastapi import Depends, UploadFile
from sqlalchemy.engine import ChunkedIteratorResult
from sqlalchemy.orm import Session

from core.config import settings
from database import Base
from mixins import dependencies as mixins_dependencies


async def get_object(
        available_db_data: ChunkedIteratorResult,
        model_for_lookup: Type[Base],
        search_value: Any,
        db_session: Session,
        lookup_kwarg: Optional[str] = 'id'
) -> Any:
    """
    Must return object from available bd data using lookup_kwarg.
    """
    get_object_statement = available_db_data.where(getattr(model_for_lookup, lookup_kwarg, None) == search_value)
    obj = await db_session.execute(get_object_statement)
    return obj.scalar()


async def create_object_in_database(
        object_to_create: Any,
        db_session: Session,
) -> Any:
    """
    Creates the given object_to_create in database (updates if it's already an existing object).
    """
    db_session.add(object_to_create)
    await db_session.commit()
    await db_session.refresh(object_to_create)
    return object_to_create


async def create_object_file(
        file_model: Any,
        file: UploadFile,
        db_session: Session,
        **kwargs
) -> Any:
    """
    Creates an object of file_model class in database.
    """
    object_to_create_in_db = file_model(**kwargs)
    folder_to_save_file = object_to_create_in_db.folder_to_save
    loop = asyncio.get_running_loop()
    content_to_write = await file.read()
    file_path = await loop.run_in_executor(None, write_file, folder_to_save_file, file.filename, content_to_write)
    object_to_create_in_db.file_path = file_path
    return await create_object_in_database(object_to_create_in_db, db_session=db_session)


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
