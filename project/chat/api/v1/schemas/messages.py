from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel

from mixins.schemas import PaginatedResponseSchemaMixin, PhotosFieldSchemaMixin


class UpdateMessageSchema(BaseModel):
    text: str


class MessageAuthorSchema(BaseModel):
    id: int
    nickname: str

    class Config:
        orm_mode = True


class ListMessagesSchema(PhotosFieldSchemaMixin):
    id: int
    is_edited: bool
    text: str
    author: MessageAuthorSchema
    replayed_message_id: Optional[int]
    scheduled_at: Optional[datetime]

    class Config:
        orm_mode = True


class PaginatedListMessagesSchema(PaginatedResponseSchemaMixin):
    data: List[ListMessagesSchema]
