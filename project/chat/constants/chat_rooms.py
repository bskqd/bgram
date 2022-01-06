from enum import Enum


class ChatRoomMemberTypeEnum(str, Enum):
    ADMIN = 'admin'
    MEMBER = 'member'
