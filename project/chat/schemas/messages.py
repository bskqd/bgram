from typing import Optional

from pydantic import BaseModel, validator

from chat.constants.messages import ALLOWED_MESSAGES_ACTION_TYPES


class SendMessageInChatSchema(BaseModel):
    action: str
    message_id: Optional[int] = None
    text: str

    @validator('action')
    def action_validator(cls, value: str) -> str:
        if value not in ALLOWED_MESSAGES_ACTION_TYPES:
            raise ValueError('Action is not allowed')
        return value


class MessageInChatSchema(BaseModel):
    id: int
    is_edited: bool
    text: str
    author_id: int

    class Config:
        orm_mode = True
