from typing import Optional, List

from pydantic import BaseModel

from mixins import schemas as mixins_schemas


class UserBase(BaseModel):
    nickname: str
    email: str
    description: Optional[str] = ''


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    nickname: Optional[str] = None
    email: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class User(UserBase, mixins_schemas.PhotosFieldSchemaABC):
    id: int
    is_active: bool
    chat_rooms: List[int]

    class Config:
        orm_mode = True
