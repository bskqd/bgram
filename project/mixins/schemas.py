from datetime import datetime
from typing import Generic, List, Optional, TypeVar

from core.dependencies.providers import provide_settings
from pydantic import BaseModel, validator

T = TypeVar('T', bound=BaseModel)


class FilesSchema(BaseModel):
    id: int
    created_at: datetime
    modified_at: datetime
    file_path: str

    class Config:
        orm_mode = True

    @validator('file_path')
    def file_path_with_media_url(cls, value: str) -> str:  # noqa: N805
        settings = provide_settings()
        return f'{settings.HOST_DOMAIN}/{settings.MEDIA_URL}{"" if value.startswith("/") else "/"}{value}'

    @validator('created_at')
    def created_at_as_string(cls, value: datetime) -> str:  # noqa: N805
        return str(value)

    @validator('modified_at')
    def modified_at_as_string(cls, value: datetime) -> str:  # noqa: N805
        return str(value)


class PhotosFieldSchemaMixin(BaseModel):
    photos: List[FilesSchema]


class PaginatedResponseSchemaMixin(Generic[T], BaseModel):
    count: int
    total_pages: int
    current_page: int
    page_size: int
    next: Optional[str]
    previous: Optional[str]
    data: List[T]
