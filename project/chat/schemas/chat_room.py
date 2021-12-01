from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel

from mixins import schemas as mixins_schemas


class ChatRoomBaseSchema(BaseModel):
    name: str
    description: Optional[str] = ''


class ChatRoomCreateSchema(ChatRoomBaseSchema):
    members: Optional[List[int]] = []


class ChatRoomUpdateSchema(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    members: Optional[List[int]] = None


class ChatRoomMemberSchema(BaseModel):
    id: int

    class Config:
        orm_mode = True


class ChatRoomSchema(ChatRoomBaseSchema, mixins_schemas.PhotosFieldSchemaMixin):
    id: int
    created_at: datetime
    modified_at: datetime
    members_count: int

    class Config:
        orm_mode = True
