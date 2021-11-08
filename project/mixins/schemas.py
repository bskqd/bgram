from datetime import datetime

from pydantic import BaseModel, validator

from core.config import settings


class FilesSchema(BaseModel):
    id: int
    created_at: datetime
    file_path: str

    class Config:
        orm_mode = True

    @validator('file_path')
    def file_path_with_media_url(cls, value) -> str:
        return f'{settings.HOST_DOMAIN}/{settings.MEDIA_URL}/{value}'
