from typing import Optional, List

from pydantic import BaseModel

from mixins import schemas as mixins_schemas


class UserBaseSchema(BaseModel):
    nickname: str
    email: str
    description: Optional[str] = ''


class UserCreateSchema(UserBaseSchema):
    password: str


class UserUpdateSchema(BaseModel):
    nickname: Optional[str] = None
    email: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class UserSchema(UserBaseSchema, mixins_schemas.PhotosFieldSchemaMixin):
    id: int
    is_active: bool
    chat_rooms: List[int]

    class Config:
        orm_mode = True
