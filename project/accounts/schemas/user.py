from typing import Optional, List

from pydantic import BaseModel, validator

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


class UserChatRoomsSchema(BaseModel):
    id: int

    class Config:
        orm_mode = True


class UserSchema(UserBaseSchema, mixins_schemas.PhotosFieldSchemaMixin):
    id: int
    is_active: bool
    chat_rooms: List[UserChatRoomsSchema]

    class Config:
        orm_mode = True

    @validator('chat_rooms')
    def chat_rooms_ids(cls, value: List[UserChatRoomsSchema]) -> List[int]:
        return [chat_room.id for chat_room in value]
