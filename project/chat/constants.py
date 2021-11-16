from enum import Enum


class ChatRoomMemberType(str, Enum):
    ADMIN = 'admin'
    MEMBER = 'member'
