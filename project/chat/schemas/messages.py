from typing import List

from pydantic import BaseModel

from mixins.schemas import PaginatedResponseSchemaMixin


class CreateMessageSchema(BaseModel):
    text: str


class UpdateMessageSchema(CreateMessageSchema):
    pass


class ListMessagesSchema(BaseModel):
    id: int
    is_edited: bool
    text: str
    author_id: int

    class Config:
        orm_mode = True


class PaginatedListMessagesSchema(PaginatedResponseSchemaMixin):
    data: List[ListMessagesSchema]
