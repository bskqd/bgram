from enum import Enum


class MessagesActionTypeEnum(str, Enum):
    CREATED = 'created'
    UPDATED = 'updated'
    DELETED = 'deleted'
