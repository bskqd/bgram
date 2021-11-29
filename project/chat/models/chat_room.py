from sqlalchemy import Column, Integer, String, Table, ForeignKey
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship

from chat.constants import ChatRoomMemberType
from database import Base
from mixins.models import DateTimeABC, DescriptionABC, IsActiveABC

__all__ = ['chatroom_members_association_table', 'ChatRoom']


chatroom_members_association_table = Table(
    'chatroom_members_association',
    Base.metadata,
    Column('room_id', Integer, ForeignKey('chat_rooms.id', ondelete='CASCADE'), index=True),
    Column('user_id', Integer, ForeignKey('users.id', ondelete='CASCADE'), index=True),
    Column('member_type', String, nullable=False, default=ChatRoomMemberType.MEMBER.value)
)


class ChatRoom(DateTimeABC, DescriptionABC, IsActiveABC):
    __tablename__ = 'chat_rooms'

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)

    members = relationship(
        'User', secondary=chatroom_members_association_table, back_populates='chat_rooms'
    )

    @hybrid_property
    def members_count(self):
        return len(self.members)
