from enum import Enum


class MessagesActionTypeEnum(str, Enum):
    CREATE = 'create'
    UPDATE = 'update'
    DELETE = 'delete'


ALLOWED_MESSAGES_ACTION_TYPES = {
    MessagesActionTypeEnum.CREATE.value,
    MessagesActionTypeEnum.UPDATE.value,
    MessagesActionTypeEnum.DELETE.value,
}
