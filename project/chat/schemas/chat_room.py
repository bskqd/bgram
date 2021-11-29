from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, validator


class ChatRoomBase(BaseModel):
    name: str
    description: Optional[str] = ''


class ChatRoomCreate(ChatRoomBase):
    members: Optional[List[int]] = []


class ChatRoomUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    members: Optional[List[int]] = None


class ChatRoomMemberSchema(BaseModel):
    id: int

    class Config:
        orm_mode = True


class ChatRoom(ChatRoomBase):
    id: int
    created_at: datetime
    modified_at: datetime
    members_count: int

    class Config:
        orm_mode = True
