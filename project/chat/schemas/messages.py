from typing import List

from pydantic import BaseModel

from mixins.schemas import PaginatedResponseSchemaMixin, PhotosFieldSchemaMixin


class UpdateMessageSchema(BaseModel):
    text: str


class ListMessagesSchema(PhotosFieldSchemaMixin):
    id: int
    is_edited: bool
    text: str
    author_id: int

    class Config:
        orm_mode = True


class PaginatedListMessagesSchema(PaginatedResponseSchemaMixin):
    data: List[ListMessagesSchema]
