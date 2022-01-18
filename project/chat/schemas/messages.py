from pydantic import BaseModel


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
