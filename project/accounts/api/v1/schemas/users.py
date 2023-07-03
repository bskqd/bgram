from typing import List, Optional

from mixins.schemas import PaginatedResponseSchemaMixin, PhotosFieldSchemaMixin
from pydantic import BaseModel, validator


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


class UsersListSchema(UserBaseSchema, PhotosFieldSchemaMixin):
    id: int
    is_active: bool
    chat_rooms: List[UserChatRoomsSchema]

    class Config:
        orm_mode = True

    @validator('chat_rooms')
    def chat_rooms_ids(cls, value: List[UserChatRoomsSchema]) -> List[int]:  # noqa: N805
        return [chat_room.id for chat_room in value]


class PaginatedUsersListSchema(PaginatedResponseSchemaMixin[UsersListSchema]):
    pass
